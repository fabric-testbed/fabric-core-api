"""DB-free tests for org-affiliation resolution.

COmanage's ``OrgIdentity.Affiliation`` is eduPersonAffiliation, which many IdPs
never release through CILogon. It used to be a precondition for storing the
OrgIdentity at all, so a person whose IdP sent ``O`` ("The State University of
New York at Buffalo") but no ``Affiliation`` got no ``people_organizations``
row, a NULL ``FabricPeople.org_affiliation``, and ``"affiliation": "Unknown"``
from ``people_uuid_get``.

The behavior tests drive the two functions that resolve the scalar FK against
fake COmanage payloads. The source pins cover the other three copies of the
same predicate (``update_user_org_affiliations``, ``db_load.load_organizations``,
``db_verify.load_organizations``), which need a live DB to exercise, and pin the
invariant that makes the placeholder safe: nothing in the API reads
``Organizations.affiliation``.
"""

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from swagger_server.response_code import comanage_utils

_RESPONSE_CODE = Path(comanage_utils.__file__).resolve().parent
_DATABASE = _RESPONSE_CODE.parent / "database"

_COMANAGE_UTILS = Path(comanage_utils.__file__)
_DB_LOAD = _DATABASE / "db_load.py"
_DB_VERIFY = _DATABASE / "db_verify.py"
_PEOPLE_CONTROLLER = _RESPONSE_CODE / "people_controller.py"
_JOURNEY_TRACKER_UTILS = _RESPONSE_CODE / "journey_tracker_utils.py"
_CORE_API_METRICS = _RESPONSE_CODE / "core_api_metrics_controller.py"
_PEOPLE_MODELS = _DATABASE / "models" / "people.py"

_BUFFALO = "The State University of New York at Buffalo"

# every copy of the OrgIdentity-storing predicate
_GUARD_SITES = (
    (_COMANAGE_UTILS, "update_org_affiliation"),
    (_COMANAGE_UTILS, "update_organizations"),
    (_COMANAGE_UTILS, "update_user_org_affiliations"),
    (_DB_LOAD, "load_organizations"),
    (_DB_VERIFY, "load_organizations"),
)


# ---------------------------------------------------------------------------
# fakes
# ---------------------------------------------------------------------------


class _FakeOrganizations:
    """Stand-in for the Organizations model plus its .query interface."""

    rows = []

    def __init__(self):
        self.id = None
        self.org_identity_id = None
        self.organization = None
        self.affiliation = None

    class _Query:
        def filter_by(self, **kwargs):
            matches = [
                row
                for row in _FakeOrganizations.rows
                if all(getattr(row, k, None) == v for k, v in kwargs.items())
            ]
            return SimpleNamespace(one_or_none=lambda: matches[0] if matches else None)

    query = _Query()


class _FakeSession:
    def __init__(self):
        self.rolled_back = False

    def add(self, row):
        if row not in _FakeOrganizations.rows:
            row.id = len(_FakeOrganizations.rows) + 1
            _FakeOrganizations.rows.append(row)

    def commit(self):
        pass

    def rollback(self):
        self.rolled_back = True


@pytest.fixture
def org_store(monkeypatch):
    """Patch the module's Organizations model and db session with fakes."""
    _FakeOrganizations.rows = []
    monkeypatch.setattr(comanage_utils, "Organizations", _FakeOrganizations)
    monkeypatch.setattr(comanage_utils, "db", SimpleNamespace(session=_FakeSession()))
    return _FakeOrganizations


def _org_identity(identity_id, organization, affiliation=None, deleted=False):
    return {
        "Id": identity_id,
        "O": organization,
        "Affiliation": affiliation,
        "Deleted": deleted,
    }


# ---------------------------------------------------------------------------
# behavior - update_organizations() (bulk CO sweep)
# ---------------------------------------------------------------------------


def test_organization_stored_when_idp_sends_no_affiliation(org_store, monkeypatch):
    """The reported case: O present, Affiliation absent -> row is created."""
    monkeypatch.setattr(
        comanage_utils,
        "api",
        SimpleNamespace(
            org_identities_view_per_co=lambda: {
                "OrgIdentities": [_org_identity(141906, _BUFFALO)]
            }
        ),
    )

    comanage_utils.update_organizations()

    assert len(org_store.rows) == 1
    assert org_store.rows[0].organization == _BUFFALO
    assert org_store.rows[0].affiliation == comanage_utils.UNSPECIFIED_ORG_AFFILIATION


def test_real_affiliation_is_preserved(org_store, monkeypatch):
    """The placeholder is a fallback, never an overwrite."""
    monkeypatch.setattr(
        comanage_utils,
        "api",
        SimpleNamespace(
            org_identities_view_per_co=lambda: {
                "OrgIdentities": [
                    _org_identity(1, "Renaissance Computing Institute", "staff")
                ]
            }
        ),
    )

    comanage_utils.update_organizations()

    assert org_store.rows[0].affiliation == "staff"


@pytest.mark.parametrize(
    "identity,reason",
    [
        (_org_identity(2, None, "faculty"), "no organization name"),
        (_org_identity(3, _BUFFALO, "faculty", deleted=True), "deleted identity"),
        (_org_identity(None, _BUFFALO, "faculty"), "no org_identity_id"),
    ],
)
def test_unusable_org_identities_are_still_skipped(
    org_store, monkeypatch, identity, reason
):
    """Only the Affiliation requirement was dropped - the rest still gate."""
    monkeypatch.setattr(
        comanage_utils,
        "api",
        SimpleNamespace(
            org_identities_view_per_co=lambda: {"OrgIdentities": [identity]}
        ),
    )

    comanage_utils.update_organizations()

    assert org_store.rows == [], reason


# ---------------------------------------------------------------------------
# behavior - update_org_affiliation() (per-person FK, the 'Unknown' fix)
# ---------------------------------------------------------------------------


def test_person_org_affiliation_resolves_without_affiliation(org_store, monkeypatch):
    """people_uuid_get renders Organizations.organization, so setting the FK is
    what turns 'Unknown' into the real institution name."""
    fab_person = SimpleNamespace(id=7, org_affiliation=None)
    monkeypatch.setattr(
        comanage_utils,
        "FabricPeople",
        SimpleNamespace(
            query=SimpleNamespace(
                filter_by=lambda **kw: SimpleNamespace(one_or_none=lambda: fab_person)
            )
        ),
    )
    monkeypatch.setattr(
        comanage_utils,
        "api",
        SimpleNamespace(
            coorg_identity_links_view_by_identity=lambda **kw: {
                "CoOrgIdentityLinks": [{"OrgIdentityId": 141906}]
            },
            org_identities_view_one=lambda **kw: {
                "OrgIdentities": [_org_identity(141906, _BUFFALO)]
            },
        ),
    )

    comanage_utils.update_org_affiliation(fab_person_id=7, co_person_id=1003367)

    assert len(org_store.rows) == 1
    assert org_store.rows[0].organization == _BUFFALO
    assert fab_person.org_affiliation == org_store.rows[0].id


# ---------------------------------------------------------------------------
# source pins - the copies that need a live DB, and the safety invariant
# ---------------------------------------------------------------------------


def _function_node(path: Path, name: str) -> ast.FunctionDef:
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError("{0} not found in {1}".format(name, path.name))


def _is_construction_of(value: ast.expr, class_name: str) -> bool:
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == class_name
    )


def _statement_blocks(node: ast.FunctionDef):
    """Every statement list inside ``node`` - its body and each nested body."""
    for child in ast.walk(node):
        for field in ("body", "orelse", "finalbody"):
            block = getattr(child, field, None)
            if isinstance(block, list) and all(
                isinstance(stmt, ast.stmt) for stmt in block
            ):
                yield block


def _organizations_affiliation_writes(node: ast.FunctionDef) -> list:
    """``<name>.affiliation = ...`` writes where ``<name>`` holds an ``Organizations()``.

    Scoped to the block and to the current binding of the name, because
    ``update_user_org_affiliations`` reuses one local (``fab_org``) for an
    ``Organizations`` row and then for a ``UserOrgAffiliations`` row. Only the
    first writes ``organizations.affiliation``, the NOT NULL column this guards;
    ``user_org_affiliations.affiliation`` is a different column that is always
    handed a non-empty string. Matching every ``.affiliation`` write regardless
    of the receiver made this test pass on v2-develop only by accident - the
    UserOrgAffiliations write there had been rewritten into a ``pg_insert``
    keyword argument by an unrelated race fix, so the ORM assignment the check
    would have tripped on was simply absent.
    """
    writes = []
    for block in _statement_blocks(node):
        organizations = set()
        for stmt in block:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if _is_construction_of(stmt.value, "Organizations"):
                        organizations.add(target.id)
                    else:
                        organizations.discard(target.id)
                elif (
                    isinstance(target, ast.Attribute)
                    and target.attr == "affiliation"
                    and isinstance(target.value, ast.Name)
                    and target.value.id in organizations
                ):
                    writes.append(stmt)
    return writes


def _org_identity_guard(path: Path, name: str) -> str:
    node = _function_node(path, name)
    guards = [
        ast.unparse(child.test)
        for child in ast.walk(node)
        if isinstance(child, ast.If)
        and "org_identity_id and organization" in ast.unparse(child.test)
    ]
    assert len(guards) == 1, (
        "{0}.{1}: expected one OrgIdentity guard, found {2}".format(
            path.name, name, len(guards)
        )
    )
    return guards[0]


@pytest.mark.parametrize("path,name", _GUARD_SITES, ids=lambda v: getattr(v, "name", v))
def test_guard_no_longer_requires_eduperson_affiliation(path, name):
    guard = _org_identity_guard(path, name)
    assert "affiliation" not in guard, (
        "{0}.{1} still discards an OrgIdentity that carries no eduPersonAffiliation".format(
            path.name, name
        )
    )
    # the name and the tombstone are still load-bearing
    assert "organization" in guard
    assert "Deleted" in guard


@pytest.mark.parametrize("path,name", _GUARD_SITES, ids=lambda v: getattr(v, "name", v))
def test_affiliation_column_always_gets_a_value(path, name):
    """Organizations.affiliation is NOT NULL - every write needs the fallback."""
    node = _function_node(path, name)
    writes = _organizations_affiliation_writes(node)
    assert writes, "{0}.{1}: no Organizations affiliation write found".format(
        path.name, name
    )
    for write in writes:
        assert (
            ast.unparse(write.value) == "affiliation or UNSPECIFIED_ORG_AFFILIATION"
        ), "{0}.{1} can write NULL into a NOT NULL column".format(path.name, name)


def test_affiliation_column_is_still_not_null():
    """No migration in this change - the placeholder exists precisely so the
    column constraint stays as it is."""
    source = _PEOPLE_MODELS.read_text()
    organizations = source.split("class Organizations")[1].split("class ")[0]
    assert "affiliation = db.Column(db.String(), nullable=False)" in organizations


@pytest.mark.parametrize(
    "path",
    [_PEOPLE_CONTROLLER, _JOURNEY_TRACKER_UTILS, _CORE_API_METRICS],
    ids=lambda p: p.name,
)
def test_api_consumers_read_organization_not_affiliation(path):
    """The placeholder is only safe while no response renders it. Every API
    consumer of an Organizations row must read .organization."""
    tree = ast.parse(path.read_text())

    # names bound to an Organizations row (e.g. `org = Organizations.query...`)
    org_bound = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign) and "Organizations" in ast.unparse(node.value)
        for target in node.targets
        if isinstance(target, ast.Name)
    }

    def _is_org_expr(value) -> bool:
        if isinstance(value, ast.Name):
            return value.id in org_bound
        return "Organizations" in ast.unparse(value)

    reads = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.ctx, ast.Load)
        and _is_org_expr(node.value)
    }
    # getattr(Organizations.query...one_or_none(), 'organization', None)
    reads |= {
        node.args[1].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "getattr"
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and _is_org_expr(node.args[0])
    }

    assert "organization" in reads, (
        "{0}: no Organizations.organization read found".format(path.name)
    )
    assert "affiliation" not in reads, (
        "{0} renders Organizations.affiliation, which may now be the "
        "'{1}' placeholder".format(
            path.name, comanage_utils.UNSPECIFIED_ORG_AFFILIATION
        )
    )
