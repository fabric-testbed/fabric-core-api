"""Focused regression tests for project-type behavior.

These tests use only the standard-library unittest runner so they remain runnable
on Python 3.12 while the generated legacy nose suite awaits migration.
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
os.environ.setdefault("PROJECTS_RENEWAL_PERIOD_IN_DAYS", "365")

from swagger_server.database.models.projects import EnumProjectTypes
from swagger_server.models.projects_patch import ProjectsPatch
from swagger_server.models.projects_post import ProjectsPost
from swagger_server.response_code import (
    people_utils,
    projects_controller,
    projects_utils,
)


class TestProjectTypeRegressions(unittest.TestCase):
    def test_project_type_options_include_infrastructure(self):
        with patch.object(
            projects_controller,
            "cors_200",
            side_effect=lambda response_body: response_body,
        ):
            response = projects_controller.projects_project_types_get()

        self.assertIn("infrastructure", response.results)

    def test_create_project_honors_requested_infrastructure_type(self):
        body = ProjectsPost(
            description="Infrastructure project",
            is_public=False,
            name="Infrastructure",
            project_lead="lead-uuid",
            project_type="infrastructure",
        )
        creator = SimpleNamespace(
            preferred_email="creator@example.net",
            uuid="creator-uuid",
        )
        project_lead = SimpleNamespace(
            preferred_email="lead@example.net",
            project_lead_approved=False,
            uuid="lead-uuid",
        )
        fab_project = SimpleNamespace(id=1, tags=[])

        with (
            patch.object(projects_utils, "FabricPeople") as fabric_people,
            patch.object(projects_utils, "FabricProjects", return_value=fab_project),
            patch.object(projects_utils, "create_comanage_group", return_value=1),
            patch.object(projects_utils, "create_projects_preferences"),
            patch.object(projects_utils, "create_profile_projects"),
            patch.object(projects_utils, "update_projects_personnel"),
            patch.object(projects_utils, "send_fabric_email"),
            patch.object(projects_utils, "ProjectsTags") as projects_tags,
            patch.object(projects_utils, "EnumResourceTypes", []),
            patch.object(projects_utils, "db"),
        ):
            fabric_people.query.filter_by.return_value.first.return_value = project_lead
            projects_tags.query.filter.return_value.one_or_none.return_value = (
                SimpleNamespace()
            )

            created = projects_utils.create_fabric_project_from_api(
                body=body, project_creator=creator
            )

        self.assertIs(created.project_type, EnumProjectTypes.infrastructure)

    def test_project_admin_cannot_create_infrastructure_project(self):
        body = ProjectsPost(project_type="infrastructure")
        api_user = MagicMock(active=True, display_name="Project Admin")
        api_user.is_project_admin.return_value = True
        api_user.is_facility_operator.return_value = False
        denied = object()

        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(api_user, None),
            ),
            patch.object(
                projects_controller, "cors_400", return_value=denied
            ) as cors_400,
        ):
            response = projects_controller.projects_post.__wrapped__(body=body)

        self.assertIs(response, denied)
        cors_400.assert_called_once()

    def test_facility_operator_can_create_infrastructure_project(self):
        body = ProjectsPost(project_lead="lead-uuid", project_type="infrastructure")
        api_user = MagicMock(active=True, uuid="operator-uuid")
        api_user.is_project_admin.return_value = False
        api_user.is_facility_operator.return_value = True
        project_lead = object()
        fab_project = SimpleNamespace(
            active=False,
            created="created",
            is_public=False,
            uuid="project-uuid",
        )
        expected = object()

        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(api_user, None),
            ),
            patch.object(projects_controller, "FabricPeople") as fabric_people,
            patch.object(
                projects_controller,
                "create_fabric_project_from_api",
                return_value=fab_project,
            ) as create,
            patch.object(projects_controller, "add_core_api_event"),
            patch.object(
                projects_controller, "projects_uuid_get", return_value=expected
            ),
            patch.object(projects_controller, "db"),
        ):
            fabric_people.query.filter_by.return_value.first.return_value = project_lead
            response = projects_controller.projects_post.__wrapped__(body=body)

        self.assertIs(response, expected)
        create.assert_called_once_with(body=body, project_creator=api_user)

    def test_project_admin_cannot_patch_project_to_infrastructure(self):
        body = ProjectsPatch(
            description="", name="", preferences={}, project_type="infrastructure"
        )
        api_user = MagicMock(uuid="admin-uuid")
        api_user.is_facility_operator.return_value = False
        fab_project = SimpleNamespace(
            description="description",
            name="name",
            project_type=EnumProjectTypes.research,
            uuid="project-uuid",
        )
        denied = object()

        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(api_user, None),
            ),
            patch.object(projects_controller, "FabricProjects") as fabric_projects,
            patch.object(
                projects_controller,
                "project_is_editable_by_api_user",
                return_value=(True, None),
            ),
            patch.object(projects_controller, "cors_400", return_value=denied),
        ):
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = (
                fab_project
            )
            response = projects_controller.projects_uuid_patch.__wrapped__(
                uuid="project-uuid", body=body
            )

        self.assertIs(response, denied)
        self.assertIs(fab_project.project_type, EnumProjectTypes.research)

    def test_facility_operator_can_patch_project_to_infrastructure(self):
        body = ProjectsPatch(
            description="", name="", preferences={}, project_type="infrastructure"
        )
        api_user = MagicMock(uuid="operator-uuid")
        api_user.is_facility_operator.return_value = True
        fab_project = SimpleNamespace(
            description="description",
            name="name",
            project_type=EnumProjectTypes.research,
            uuid="project-uuid",
        )
        expected = object()

        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(api_user, None),
            ),
            patch.object(projects_controller, "FabricProjects") as fabric_projects,
            patch.object(
                projects_controller,
                "project_is_editable_by_api_user",
                return_value=(True, None),
            ),
            patch.object(projects_controller, "projects_set_active"),
            patch.object(projects_controller, "cors_200", return_value=expected),
            patch.object(projects_controller, "db"),
        ):
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = (
                fab_project
            )
            response = projects_controller.projects_uuid_patch.__wrapped__(
                uuid="project-uuid", body=body
            )

        self.assertIs(response, expected)
        self.assertIs(fab_project.project_type, EnumProjectTypes.infrastructure)

    def test_patch_without_project_type_leaves_type_unchanged(self):
        # PATCH bodies must not default project_type: an omitted field used to
        # deserialize as 'research' and silently reset the project's type.
        body = ProjectsPatch(description="", name="", preferences={})
        api_user = MagicMock(uuid="owner-uuid")
        api_user.is_facility_operator.return_value = False
        fab_project = SimpleNamespace(
            description="description",
            name="name",
            project_type=EnumProjectTypes.infrastructure,
            uuid="project-uuid",
        )
        expected = object()

        with (
            patch.object(
                projects_controller,
                "get_person_by_login_claims",
                return_value=(api_user, None),
            ),
            patch.object(projects_controller, "FabricProjects") as fabric_projects,
            patch.object(
                projects_controller,
                "project_is_editable_by_api_user",
                return_value=(True, None),
            ),
            patch.object(projects_controller, "projects_set_active"),
            patch.object(projects_controller, "cors_200", return_value=expected),
            patch.object(projects_controller, "db"),
        ):
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = (
                fab_project
            )
            response = projects_controller.projects_uuid_patch.__wrapped__(
                uuid="project-uuid", body=body
            )

        self.assertIsNone(body.project_type)
        self.assertIs(response, expected)
        self.assertIs(fab_project.project_type, EnumProjectTypes.infrastructure)

    def test_infrastructure_project_grants_jupyterhub_access(self):
        fab_person = SimpleNamespace(
            id=1,
            roles=[SimpleNamespace(name="project-uuid-pm")],
            uuid="person-uuid",
        )
        fab_project = SimpleNamespace(
            is_active=lambda: True,
            project_type=EnumProjectTypes.infrastructure,
        )

        with (
            patch.object(people_utils, "is_valid_uuid", return_value=True),
            patch.object(people_utils, "FabricGroups") as fabric_groups,
            patch.object(people_utils, "FabricProjects") as fabric_projects,
            patch.object(people_utils, "create_comanage_role") as create_role,
        ):
            jupyterhub_group = object()
            fabric_groups.query.filter_by.return_value.one_or_none.return_value = (
                jupyterhub_group
            )
            fabric_projects.query.filter_by.return_value.one_or_none.return_value = (
                fab_project
            )

            people_utils.set_jupyterhub_role(fab_person)

        create_role.assert_called_once_with(
            fab_person=fab_person, fab_group=jupyterhub_group
        )


if __name__ == "__main__":
    unittest.main()
