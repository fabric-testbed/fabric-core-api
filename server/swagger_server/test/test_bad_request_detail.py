"""Regression tests: a 400 must say which field failed and why.

`flask_bad_request` formatted the exception itself::

    'Validation error or other malformed request type: {0}'.format(exception)

Connexion's `BadRequestProblem` carries its message on `.detail` and
stringifies to an empty string, so every body-validation 400 arrived with the
prefix and nothing after it -- in the body and in the `X-Error` header.

That erasure has a measured cost: `broker.fabric-testbed.net` sent 3,602
`PUT /quotas/{uuid}` requests to production and received 3,602 400s, with
`quota_used` stuck at 0 across 5,678 rows. Connexion rejected the bodies before
the handler ran, and the response said only "Validation error or other
malformed request type:", so nothing in the logs or the response identified the
offending field.

The detail is now extracted from whichever attribute the exception actually
uses, then collapsed to a single line and bounded -- `cors_400` puts the same
string in the `X-Error` header, where a newline makes the response invalid.

Standard-library unittest only, so it runs on Python 3.12 alongside the other
1.x regression tests::

    PYTHONPATH=server python server/swagger_server/test/test_bad_request_detail.py
"""

import os
import unittest

# comanage_utils creates its client at import time.
os.environ.setdefault("COMANAGE_API_URL", "http://example.invalid")
os.environ.setdefault("COMANAGE_API_USER", "test-user")
os.environ.setdefault("COMANAGE_API_PASS", "test-pass")
os.environ.setdefault("COMANAGE_API_CO_ID", "1")
os.environ.setdefault("COMANAGE_API_CO_NAME", "test-co")
os.environ.setdefault("COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID", "1")
os.environ.setdefault("CORE_API_DEFAULT_FACILITY", "FABRIC")

from connexion.exceptions import BadRequestProblem  # noqa: E402
from flask import Flask  # noqa: E402
from jsonschema import ValidationError  # noqa: E402

from swagger_server.response_code.cors_response import (  # noqa: E402
    _X_ERROR_MAX_LEN,
    cors_400,
    problem_detail,
)

_APP = Flask(__name__)

# What Connexion 2.14 raises for a null-valued numeric field, verbatim:
# validation.py builds detail as "<jsonschema message> - '<path>'".
BROKER_SHAPED_DETAIL = "None is not of type 'number' - 'quota_used'"


class TestTheErasureThisFixes(unittest.TestCase):
    def test_str_of_a_BadRequestProblem_is_still_empty(self):
        # The premise of the bug. If a Connexion upgrade ever makes this false,
        # this test fails and the fix can be revisited rather than assumed.
        self.assertEqual(str(BadRequestProblem(detail=BROKER_SHAPED_DETAIL)), "")

    def test_the_old_formatting_produced_a_bare_prefix(self):
        old = 'Validation error or other malformed request type: {0}'.format(
            BadRequestProblem(detail=BROKER_SHAPED_DETAIL))
        self.assertEqual(old, 'Validation error or other malformed request type: ')


class TestDetailExtraction(unittest.TestCase):
    def test_connexion_detail_is_surfaced(self):
        self.assertEqual(
            problem_detail(BadRequestProblem(detail=BROKER_SHAPED_DETAIL)),
            BROKER_SHAPED_DETAIL)

    def test_jsonschema_message_and_path_are_surfaced(self):
        error = ValidationError("None is not of type 'number'")
        error.absolute_path.append("quota_used")
        detail = problem_detail(error)
        self.assertIn("None is not of type 'number'", detail)
        self.assertIn("quota_used", detail)

    def test_a_detail_less_exception_falls_back_to_its_text(self):
        self.assertEqual(problem_detail(ValueError("no body supplied")), "no body supplied")

    def test_an_empty_exception_never_yields_an_empty_detail(self):
        # A blank detail would reproduce the bug in a different disguise.
        self.assertEqual(problem_detail(BadRequestProblem(detail=None)), "BadRequestProblem")
        self.assertEqual(problem_detail(ValueError()), "ValueError")


class TestTheHeaderStaysValid(unittest.TestCase):
    """cors_400 copies the detail into X-Error; headers cannot hold newlines."""

    def test_multiline_detail_is_collapsed_to_one_line(self):
        # jsonschema's str() spans many lines -- schema dump, instance dump.
        error = ValidationError("None is not of type 'number'")
        error.absolute_path.append("quota_used")
        multiline = BadRequestProblem(detail="line one\nline two\n\n  line three")
        detail = problem_detail(multiline)
        self.assertNotIn("\n", detail)
        self.assertEqual(detail, "line one line two line three")

    def test_long_detail_is_truncated(self):
        detail = problem_detail(BadRequestProblem(detail="x" * 500))
        self.assertEqual(len(detail), _X_ERROR_MAX_LEN)
        self.assertTrue(detail.endswith("..."))

    def test_the_400_response_carries_the_field_in_body_and_header(self):
        with _APP.test_request_context("/quotas/uuid", method="PUT"):
            response = cors_400(
                details='Validation error or other malformed request type: {0}'.format(
                    problem_detail(BadRequestProblem(detail=BROKER_SHAPED_DETAIL))))
        self.assertEqual(response.status_code, 400)
        self.assertIn("quota_used", response.headers["X-Error"])
        self.assertNotIn("\n", response.headers["X-Error"])
        self.assertIn("quota_used", response.data.decode())

    def test_a_multiline_detail_survives_werkzeug_header_validation(self):
        # The regression this guards: an un-collapsed value turns a 400 into a
        # 500 (or a stripped header) at the WSGI layer.
        with _APP.test_request_context("/quotas/uuid", method="PUT"):
            response = cors_400(details=problem_detail(
                BadRequestProblem(detail="bad\nvalue")))
            list(response.get_wsgi_headers(_APP.test_request_context().request.environ))
        self.assertEqual(response.headers["X-Error"], "bad value")


if __name__ == "__main__":
    unittest.main()
