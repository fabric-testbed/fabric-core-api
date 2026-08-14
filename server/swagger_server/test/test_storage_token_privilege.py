"""Regression tests: no identity substitution on the /storage write path.

All five storage operations used to carry this block:

    # TODO: token access does not have an api_user --> choose first facility-operator
    if not api_user.id:
        api_user = <first active facility operator>

Any caller whose identity resolves to an empty FabricPeople fell through it and
was promoted to a REAL facility operator, after which
``api_user.is_facility_operator()`` was true and the write proceeded. That is a
privilege escalation for:

  * a ``readonly`` bearer token (confirmed against a live app: POST /storage
    returned 200 and created the volume),
  * a ``services`` bearer token,
  * any authenticated user whose ``sub`` is not in the local people table.

The write path (POST / PATCH / DELETE) no longer substitutes. The read path
keeps the existing global-read behavior only for the named readonly/services
tokens. An authenticated human whose sub is unknown locally is denied instead
of being promoted; preserving service compatibility does not require granting
that human facility-operator visibility.

The ansible token continues to resolve to a real person via
``first_valid_facility_operator()``, so ``api_user.id`` is set before the
storage guard. That full token-to-person path is pinned below, because "the
ansible integration keeps working" is the constraint this fix had to hold.

Standard-library unittest only, so it runs on Python 3.12 alongside the other
1.x regression tests::

    PYTHONPATH=server python server/swagger_server/test/test_storage_token_privilege.py
"""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# comanage_utils creates its client at import time.
os.environ.setdefault("COMANAGE_API_URL", "http://example.invalid")
os.environ.setdefault("COMANAGE_API_USER", "test-user")
os.environ.setdefault("COMANAGE_API_PASS", "test-pass")
os.environ.setdefault("COMANAGE_API_CO_ID", "1")
os.environ.setdefault("COMANAGE_API_CO_NAME", "test-co")
os.environ.setdefault("COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID", "1")
os.environ.setdefault("CORE_API_DEFAULT_FACILITY", "FABRIC")
os.environ.setdefault("COU_ID_PROJECTS", "1")
os.environ.setdefault("COU_NAME_JUPYTERHUB", "JupyterHub")
os.environ.setdefault("COU_NAME_FACILITY_OPERATORS", "facility-operators")
os.environ.setdefault("PROJECTS_RENEWAL_PERIOD_IN_DAYS", "365")
os.environ.setdefault("ANSIBLE_AUTHORIZATION_TOKEN", "test-ansible-token")
os.environ.setdefault("READONLY_AUTHORIZATION_TOKEN", "test-readonly-token")
os.environ.setdefault("SERVICES_AUTHORIZATION_TOKEN", "test-services-token")

from flask import Flask  # noqa: E402

from swagger_server.response_code import (  # noqa: E402
    decorators,
    people_utils,
    storage_controller,
    vouch_utils,
)

_APP = Flask(__name__)

STORAGE_UUID = "33333333-3333-4333-8333-333333333333"


def _tokened_caller():
    """What get_person_by_login_claims returns for a token with no local person.

    Exactly what a readonly/services token -- or an authenticated user whose sub
    is unknown locally -- produces: a bare FabricPeople with no id.
    """
    return SimpleNamespace(
        id=None,
        active=None,
        display_name=None,
        is_facility_operator=lambda: False,
    )


def _facility_operator():
    """A real, active facility operator (what the ansible token resolves to)."""
    return SimpleNamespace(
        id=42,
        active=True,
        display_name="Real Operator",
        is_facility_operator=lambda: True,
    )


class _WriteHandlerCase(unittest.TestCase):
    """Drive one write handler and report (response, cors_403, fabric_roles)."""

    def _call(self, handler_name, api_user, **kwargs):
        sentinel_403 = object()
        with (
            patch.object(
                storage_controller,
                "get_person_by_login_claims",
                return_value=(api_user, "token-readonly"),
            ),
            patch.object(storage_controller, "FabricRoles") as fabric_roles,
            patch.object(storage_controller, "FabricPeople") as fabric_people,
            patch.object(storage_controller, "FabricProjects") as fabric_projects,
            patch.object(storage_controller, "FabricStorage") as fabric_storage,
            patch.object(
                storage_controller, "cors_403", return_value=sentinel_403
            ) as cors_403,
            patch.object(storage_controller, "cors_404", return_value=object()),
            patch.object(storage_controller, "cors_500", return_value=object()),
            patch.object(storage_controller, "cors_200", return_value=object()),
        ):
            # If the handler gets past the guard it will look for a row; give it
            # none so it stops at a 404 rather than exercising the whole write.
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = None
            fabric_storage.query.filter_by.return_value.one_or_none.return_value = None
            # Call the UNDECORATED handler: login_or_token_required is the
            # authentication gate, and what is under test here is the
            # authorization performed inside the handler body.
            handler = getattr(storage_controller, handler_name).__wrapped__
            with _APP.test_request_context("/storage"):
                response = handler(**kwargs)
        return response, sentinel_403, cors_403, fabric_roles


class TestWritePathRejectsSubstitutedIdentity(_WriteHandlerCase):
    """A caller with no local person must be refused, not promoted."""

    def test_delete_is_denied(self):
        response, sentinel_403, cors_403, _roles = self._call(
            "storage_uuid_delete", _tokened_caller(), uuid=STORAGE_UUID
        )
        self.assertIs(response, sentinel_403)
        cors_403.assert_called_once()

    def test_patch_is_denied(self):
        response, sentinel_403, cors_403, _roles = self._call(
            "storage_uuid_patch",
            _tokened_caller(),
            uuid=STORAGE_UUID,
            body=MagicMock(),
        )
        self.assertIs(response, sentinel_403)
        cors_403.assert_called_once()

    def test_post_is_denied(self):
        response, sentinel_403, cors_403, _roles = self._call(
            "storage_post", _tokened_caller(), body=MagicMock()
        )
        self.assertIs(response, sentinel_403)
        cors_403.assert_called_once()


class TestWritePathNeverLooksUpAFacilityOperator(_WriteHandlerCase):
    """The structural half of the fix.

    Asserting only on the 403 would still pass if some later check happened to
    deny for an unrelated reason. The substitution is gone only if the
    facility-operator lookup is never performed at all.
    """

    def _assert_no_operator_lookup(self, handler_name, **kwargs):
        _response, _sentinel, _cors_403, fabric_roles = self._call(
            handler_name, _tokened_caller(), **kwargs
        )
        fabric_roles.query.filter_by.assert_not_called()

    def test_delete_does_not_look_up_an_operator(self):
        self._assert_no_operator_lookup("storage_uuid_delete", uuid=STORAGE_UUID)

    def test_patch_does_not_look_up_an_operator(self):
        self._assert_no_operator_lookup(
            "storage_uuid_patch", uuid=STORAGE_UUID, body=MagicMock()
        )

    def test_post_does_not_look_up_an_operator(self):
        self._assert_no_operator_lookup("storage_post", body=MagicMock())


class TestStaticServiceTokenResolution(unittest.TestCase):
    """Named service credentials must resolve without entering JWT handling."""

    def test_readonly_and_services_tokens_resolve_without_jwt_or_psk(self):
        cases = (
            (
                "READONLY_AUTHORIZATION_TOKEN",
                vouch_utils.IdSourceEnum.READONLY.value,
            ),
            (
                "SERVICES_AUTHORIZATION_TOKEN",
                vouch_utils.IdSourceEnum.SERVICES.value,
            ),
        )
        for env_name, expected_source in cases:
            with self.subTest(env_name=env_name):
                with (
                    patch.object(vouch_utils.jwt, "decode") as jwt_decode,
                    patch.object(
                        vouch_utils, "TaskTimeoutTracker"
                    ) as task_timeout_tracker,
                ):
                    claims = vouch_utils.token_get_custom_claims(os.environ[env_name])

                self.assertEqual(claims["source"], expected_source)
                self.assertIsNone(claims["sub"])
                jwt_decode.assert_not_called()
                task_timeout_tracker.query.filter_by.assert_not_called()


class TestAnsibleIntegrationIsUnaffected(_WriteHandlerCase):
    """The constraint this fix had to hold: nothing breaks for ansible.

    The ansible token borrows a real facility operator's identity upstream in
    first_valid_facility_operator(), so it arrives with api_user.id set and a
    true is_facility_operator(). It must still get past the guard.
    """

    def test_ansible_token_resolves_to_a_real_operator(self):
        """Exercise Authorization header -> claims -> local person resolution."""
        operator = _facility_operator()
        operator_sub = "real-operator-sub"
        claims = {
            "aud": None,
            "email": "operator@example.test",
            "family_name": "Operator",
            "given_name": "Real",
            "iss": None,
            "name": operator.display_name,
            "source": vouch_utils.IdSourceEnum.ANSIBLE.value,
            "sub": operator_sub,
        }
        subject_identifier = SimpleNamespace(sub=operator_sub, people_id=operator.id)

        with (
            patch.object(
                vouch_utils,
                "first_valid_facility_operator",
                return_value=claims,
            ) as first_valid_facility_operator,
            patch.object(vouch_utils.jwt, "decode") as jwt_decode,
            patch.object(vouch_utils, "TaskTimeoutTracker") as task_timeout_tracker,
            patch.object(people_utils, "UserSubjectIdentifiers") as subject_identifiers,
            patch.object(people_utils, "FabricPeople") as fabric_people,
        ):
            subject_identifiers.query.filter.return_value.one_or_none.return_value = (
                subject_identifier
            )
            fabric_people.query.filter_by.return_value.first.return_value = operator
            with _APP.test_request_context(
                "/storage",
                headers={
                    "Authorization": "Bearer {0}".format(
                        os.environ["ANSIBLE_AUTHORIZATION_TOKEN"]
                    )
                },
            ):
                api_user, id_source = people_utils.get_person_by_login_claims()

        self.assertIs(api_user, operator)
        self.assertEqual(id_source, vouch_utils.IdSourceEnum.ANSIBLE.value)
        first_valid_facility_operator.assert_called_once_with()
        jwt_decode.assert_not_called()
        task_timeout_tracker.query.filter_by.assert_not_called()

    def test_delete_passes_the_guard(self):
        _response, sentinel_403, cors_403, _roles = self._call(
            "storage_uuid_delete", _facility_operator(), uuid=STORAGE_UUID
        )
        cors_403.assert_not_called()

    def test_patch_passes_the_guard(self):
        _response, sentinel_403, cors_403, _roles = self._call(
            "storage_uuid_patch",
            _facility_operator(),
            uuid=STORAGE_UUID,
            body=MagicMock(),
        )
        cors_403.assert_not_called()

    def test_post_passes_the_guard(self):
        _response, sentinel_403, cors_403, _roles = self._call(
            "storage_post", _facility_operator(), body=MagicMock()
        )
        cors_403.assert_not_called()


class _ReadHandlerCase(unittest.TestCase):
    """Drive one read handler and expose its authorization-side effects."""

    def _call(self, handler_name, id_source, **kwargs):
        sentinel_403 = object()
        sentinel_404 = object()
        with (
            patch.object(
                storage_controller,
                "get_person_by_login_claims",
                return_value=(_tokened_caller(), id_source),
            ),
            patch.object(storage_controller, "FabricRoles") as fabric_roles,
            patch.object(storage_controller, "FabricPeople") as fabric_people,
            patch.object(storage_controller, "FabricProjects") as fabric_projects,
            patch.object(storage_controller, "FabricStorage") as fabric_storage,
            patch.object(
                storage_controller, "cors_403", return_value=sentinel_403
            ) as cors_403,
            patch.object(storage_controller, "cors_404", return_value=sentinel_404),
            patch.object(storage_controller, "cors_500", return_value=object()),
        ):
            fabric_roles.query.filter_by.return_value = [SimpleNamespace(people_id=42)]
            fabric_people.query.filter_by.return_value.one_or_none.return_value = (
                _facility_operator()
            )
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = None
            fabric_storage.query.filter_by.return_value.one_or_none.return_value = None
            handler = getattr(storage_controller, handler_name).__wrapped__
            with _APP.test_request_context("/storage"):
                response = handler(**kwargs)
        return response, sentinel_403, sentinel_404, cors_403, fabric_roles


class TestReadPathAuthorization(_ReadHandlerCase):
    """Pin service-token compatibility without promoting unknown humans."""

    _READ_CALLS = (
        (
            "storage_get",
            {"offset": 0, "limit": 10, "project_uuid": "unknown-project"},
        ),
        ("storage_uuid_get", {"uuid": STORAGE_UUID}),
    )

    def test_unknown_authenticated_people_are_denied(self):
        for id_source in (
            vouch_utils.IdSourceEnum.COOKIE.value,
            vouch_utils.IdSourceEnum.USER.value,
        ):
            for handler_name, kwargs in self._READ_CALLS:
                with self.subTest(id_source=id_source, handler=handler_name):
                    response, sentinel_403, _sentinel_404, cors_403, roles = self._call(
                        handler_name, id_source, **kwargs
                    )
                    self.assertIs(response, sentinel_403)
                    cors_403.assert_called_once()
                    roles.query.filter_by.assert_not_called()

    def test_named_service_tokens_keep_the_existing_read_path(self):
        for id_source in (
            vouch_utils.IdSourceEnum.READONLY.value,
            vouch_utils.IdSourceEnum.SERVICES.value,
        ):
            for handler_name, kwargs in self._READ_CALLS:
                with self.subTest(id_source=id_source, handler=handler_name):
                    response, _sentinel_403, sentinel_404, cors_403, roles = self._call(
                        handler_name, id_source, **kwargs
                    )
                    self.assertIs(response, sentinel_404)
                    cors_403.assert_not_called()
                    roles.query.filter_by.assert_called_once_with(
                        name=os.getenv("COU_NAME_FACILITY_OPERATORS")
                    )


class TestUnsetStaticTokenIsNeverMatched(unittest.TestCase):
    """An unset or blank static-token env var must never match a caller.

    os.getenv() returns None for an unset var; the pre-fix code compared the
    incoming token against format(None) == 'None' (and the decorator against
    'Bearer None'), so a caller sending the literal token 'None' matched the
    ansible branch and -- once the branches became a first-match if/elif chain
    -- was promoted to a real facility operator with write access. The guard is
    that a static token participates in the comparison only when configured.
    """

    _STATIC_TOKEN_ENVS = (
        "ANSIBLE_AUTHORIZATION_TOKEN",
        "READONLY_AUTHORIZATION_TOKEN",
        "SERVICES_AUTHORIZATION_TOKEN",
    )

    def test_claims_resolver_does_not_promote_bearer_none(self):
        """token_get_custom_claims('None') must not reach the ansible branch."""
        for placeholder in ("<unset>", ""):
            with self.subTest(placeholder=placeholder):
                with patch.dict(os.environ):
                    for env_name in self._STATIC_TOKEN_ENVS:
                        if placeholder == "<unset>":
                            os.environ.pop(env_name, None)
                        else:
                            os.environ[env_name] = placeholder
                    with (
                        patch.object(
                            vouch_utils, "first_valid_facility_operator"
                        ) as first_valid_facility_operator,
                        patch.object(
                            vouch_utils, "TaskTimeoutTracker"
                        ) as task_timeout_tracker,
                    ):
                        # Force the user-token branch to fail closed (no DB, no
                        # network) so the assertion rests only on which branch
                        # the literal 'None' token selected.
                        task_timeout_tracker.query.filter_by.return_value.one_or_none.return_value = None
                        claims = vouch_utils.token_get_custom_claims("None")

                # The ansible identity path was never entered, and no facility
                # operator claims were produced.
                first_valid_facility_operator.assert_not_called()
                self.assertNotEqual(
                    claims["source"], vouch_utils.IdSourceEnum.ANSIBLE.value
                )
                self.assertIsNone(claims["sub"])

    def test_decorator_gate_rejects_bearer_none(self):
        """validate_authorization_token('Bearer None') must be False when unset."""
        for placeholder in ("<unset>", ""):
            with self.subTest(placeholder=placeholder):
                with patch.dict(os.environ):
                    for env_name in self._STATIC_TOKEN_ENVS:
                        if placeholder == "<unset>":
                            os.environ.pop(env_name, None)
                        else:
                            os.environ[env_name] = placeholder
                    with patch.object(
                        decorators, "TaskTimeoutTracker"
                    ) as task_timeout_tracker:
                        task_timeout_tracker.query.filter_by.return_value.one_or_none.return_value = None
                        with _APP.test_request_context("/storage"):
                            is_valid = decorators.validate_authorization_token(
                                "Bearer None"
                            )

                self.assertFalse(is_valid)


if __name__ == "__main__":
    unittest.main()
