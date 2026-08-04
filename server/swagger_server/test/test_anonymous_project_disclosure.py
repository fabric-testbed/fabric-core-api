"""Regression tests for anonymous access to project details.

`projects_uuid_get` has two authorization branches. The authenticated branch
returns 403 to a non-member asking for a private project. The anonymous branch
had no equivalent check, so an unauthenticated caller received strictly more of
a private project (name, description, communities, funding, fabric_matrix,
project_type) than a signed-in non-member did.

These tests use only the standard-library unittest runner so they remain
runnable on Python 3.12 while the generated legacy nose suite awaits migration.
"""

import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

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
os.environ.setdefault("PROJECTS_RENEWAL_PERIOD_IN_DAYS", "365")

import yaml
from flask import Flask

from swagger_server.response_code import projects_controller
from swagger_server.response_code import cors_response

PRIVATE_UUID = "11111111-1111-4111-8111-111111111111"
PUBLIC_UUID = "22222222-2222-4222-8222-222222222222"


def _project(uuid, is_public):
    """A row with every attribute the anonymous branch reads."""
    return SimpleNamespace(
        id=1,
        uuid=uuid,
        active=True,
        is_public=is_public,
        name="Project",
        description="Description",
        communities=[SimpleNamespace(community="Research")],
        project_funding=[
            SimpleNamespace(
                agency="NSF",
                agency_other=None,
                award_amount="1",
                award_number="A-1",
                directorate="CISE",
            )
        ],
        project_type=SimpleNamespace(name="research"),
    )


class TestAnonymousProjectDisclosure(unittest.TestCase):
    def _call_anonymously(self, project):
        """Drive projects_uuid_get down the anonymous branch.

        The branch is selected by a falsy id_source, not by a missing user.
        """
        sentinel_403 = object()
        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(None, None),
            ),
            patch.object(projects_controller, "FabricProjects") as fabric_projects,
            # projects_uuid_get still recomputes lifecycle inline on this
            # branch; it is not what these tests are about.
            patch.object(projects_controller, "projects_set_active"),
            patch.object(projects_controller, "get_fabric_matrix", return_value=None),
            patch.object(
                projects_controller, "cors_403", return_value=sentinel_403
            ) as cors_403,
            patch.object(
                projects_controller,
                "cors_200",
                side_effect=lambda response_body: response_body,
            ),
        ):
            query = fabric_projects.query.filter_by.return_value
            query.one_or_none.return_value = project
            response = projects_controller.projects_uuid_get(uuid=project.uuid)
        return response, sentinel_403, cors_403

    def test_anonymous_caller_is_denied_a_private_project(self):
        project = _project(PRIVATE_UUID, is_public=False)
        response, sentinel_403, cors_403 = self._call_anonymously(project)

        self.assertIs(response, sentinel_403)
        cors_403.assert_called_once()

    def test_anonymous_caller_still_reads_a_public_project(self):
        """The guard must not close the anonymous tier it is narrowing."""
        project = _project(PUBLIC_UUID, is_public=True)
        response, _sentinel_403, cors_403 = self._call_anonymously(project)

        cors_403.assert_not_called()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.results[0].uuid, PUBLIC_UUID)
        self.assertEqual(response.results[0].name, "Project")

    def test_private_project_leaks_no_attributes_on_denial(self):
        """A 403 body must not carry the row's own fields.

        Asserting on the denial response rather than only on the status keeps
        a future 'helpful' error message from reintroducing the disclosure.
        """
        project = _project(PRIVATE_UUID, is_public=False)
        _response, _sentinel_403, cors_403 = self._call_anonymously(project)

        details = cors_403.call_args.kwargs["details"]
        self.assertNotIn(project.name, details)
        self.assertNotIn(project.description, details)
        self.assertNotIn(project.uuid, details)


class TestPublicErrorContract(unittest.TestCase):
    def test_internal_error_details_never_reach_the_wire(self):
        private_detail = "SELECT secret FROM tokens\n[parameters: ('ā',)]"
        app = Flask(__name__)
        with app.test_request_context("/announcements"):
            response = cors_response.cors_500(details=private_detail)

        body = json.loads(response.get_data(as_text=True))
        public_detail = "An internal server error occurred."
        self.assertEqual(response.status_code, 500)
        self.assertEqual(body["errors"][0]["details"], public_detail)
        self.assertEqual(response.headers["X-Error"], public_detail)
        self.assertNotIn(private_detail, response.get_data(as_text=True))

    def test_announcements_search_contract_rejects_nul(self):
        swagger_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "swagger", "swagger.yaml"
        )
        with open(swagger_path) as stream:
            spec = yaml.safe_load(stream)
        parameters = spec["paths"]["/announcements"]["get"]["parameters"]
        search = next(item for item in parameters if item["name"] == "search")
        self.assertEqual(search["schema"]["pattern"], r"^[^\x00]*$")


if __name__ == "__main__":
    unittest.main()
