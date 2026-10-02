"""A revoked CM token stays revoked under every encoding PyJWT still verifies.

The TRL holds sha256 of each token as the Credential Manager issued it, and
``decorators.validate_authorization_token`` hashes the presented string. Any
re-encoding the JWT library accepts therefore re-mints a revoked token
(Dependabot #33, CVE-2026-102269): PyJWT <=2.13 verified signatures with
altered unused low bits in the final base64url character, and 2.15.1 verifies
a signature with trailing ``=`` padding. These drive the real decode +
revocation chain with a locally generated RS256 key, a fake PSK row and a
patched TRL — no DB, no network.
"""

import hashlib
from types import SimpleNamespace

import flask
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from swagger_server.response_code import decorators

_B64URL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"

_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_TOKEN = jwt.encode({"sub": "revoked-user", "iss": "cm"}, _KEY, algorithm="RS256")


def _altered_signature(token: str) -> str:
    # A 256-byte RS256 signature is 342 base64url chars: the last one carries
    # 4 unused low bits, so changing them leaves the decoded bytes identical.
    header, payload, sig = token.split(".")
    i = _B64URL.index(sig[-1])
    alt = _B64URL[(i & ~0xF) | ((i + 1) & 0xF)]
    return f"{header}.{payload}.{sig[:-1]}{alt}"


def _padded_header(token: str) -> str:
    header, payload, sig = token.split(".")
    return f"{header}=.{payload}.{sig}"


VARIANTS = {
    "signature-padded-==": lambda t: t + "==",
    "signature-padded-=": lambda t: t + "=",
    "signature-altered-low-bits": _altered_signature,
    "header-padded": _padded_header,
    "trailing-space": lambda t: t + " ",
    "trailing-newline": lambda t: t + "\n",
}


def _trl(*tokens):
    return [hashlib.sha256(t.encode()).hexdigest() for t in tokens]


@pytest.fixture
def validate(monkeypatch):
    for var in (
        "ANSIBLE_AUTHORIZATION_TOKEN",
        "READONLY_AUTHORIZATION_TOKEN",
        "SERVICES_AUTHORIZATION_TOKEN",
    ):
        monkeypatch.delenv(var, raising=False)
    psk = SimpleNamespace(
        value=jwt.algorithms.RSAAlgorithm.to_jwk(_KEY.public_key()),
        timed_out=lambda: False,
    )
    query = SimpleNamespace(
        filter_by=lambda **kw: SimpleNamespace(one_or_none=lambda: psk)
    )
    monkeypatch.setattr(decorators, "TaskTimeoutTracker", SimpleNamespace(query=query))
    trl = []
    monkeypatch.setattr(decorators, "get_token_revocation_list", lambda: trl)

    def run(token):
        with flask.Flask(__name__).test_request_context("/projects"):
            return decorators.validate_authorization_token("Bearer " + token)

    run.trl = trl
    return run


def test_accepts_canonical_unrevoked_token(validate):
    assert validate(_TOKEN) is True


def test_denies_canonical_revoked_token(validate):
    validate.trl.extend(_trl(_TOKEN))
    assert validate(_TOKEN) is False


@pytest.mark.parametrize("variant", VARIANTS)
def test_denies_reencoded_revoked_token(validate, variant):
    validate.trl.extend(_trl(_TOKEN))
    assert validate(VARIANTS[variant](_TOKEN)) is False


@pytest.mark.parametrize("variant", ["signature-padded-==", "header-padded"])
def test_is_token_revoked_denies_non_canonical_even_with_empty_trl(validate, variant):
    assert decorators.is_token_revoked(VARIANTS[variant](_TOKEN)) is True


def test_altered_low_bits_rejected_by_library():
    # Not caught by _CANONICAL_JWS (every char is still base64url): this
    # variant is closed only by PyJWT >= 2.14 enforcing canonical encoding,
    # so a downgrade below the pyproject floor fails here.
    with pytest.raises(jwt.DecodeError):
        jwt.decode(_altered_signature(_TOKEN), _KEY.public_key(), algorithms=["RS256"])
