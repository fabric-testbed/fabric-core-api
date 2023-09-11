# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.profile_projects import ProfileProjects  # noqa: E501
from swagger_server.models.projects import Projects  # noqa: E501
from swagger_server.models.projects_details import ProjectsDetails  # noqa: E501
from swagger_server.models.projects_expires_on_patch import ProjectsExpiresOnPatch  # noqa: E501
from swagger_server.models.projects_patch import ProjectsPatch  # noqa: E501
from swagger_server.models.projects_personnel_patch import ProjectsPersonnelPatch  # noqa: E501
from swagger_server.models.projects_post import ProjectsPost  # noqa: E501
from swagger_server.models.projects_tags_patch import ProjectsTagsPatch  # noqa: E501
from swagger_server.models.projects_token_holders_patch import ProjectsTokenHoldersPatch  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status423_locked import Status423Locked  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestProjectsController(BaseTestCase):
    """ProjectsController integration test stubs"""

    def test_projects_get(self):
        """Test case for projects_get

        Search for FABRIC Projects
        """
        query_string = [('search', 'search_example'),
                        ('offset', 1),
                        ('limit', 200),
                        ('person_uuid', 'person_uuid_example'),
                        ('sort_by', 'name'),
                        ('order_by', 'asc')]
        response = self.client.open(
            '/projects',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_post(self):
        """Test case for projects_post

        Create new Project
        """
        body = ProjectsPost()
        response = self.client.open(
            '/projects',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_preferences_get(self):
        """Test case for projects_preferences_get

        List of Projects Preference options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/projects/preferences',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_profile_preferences_get(self):
        """Test case for projects_profile_preferences_get

        List of Projects Profile Preference options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/projects/profile/preferences',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_tags_get(self):
        """Test case for projects_tags_get

        List of Projects Tags options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/projects/tags',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_delete(self):
        """Test case for projects_uuid_delete

        Delete Project as owner
        """
        response = self.client.open(
            '/projects/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_expires_on_patch(self):
        """Test case for projects_uuid_expires_on_patch

        Update Project expires on date as Facility Operator
        """
        body = ProjectsExpiresOnPatch()
        response = self.client.open(
            '/projects/{uuid}/expires-on'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_get(self):
        """Test case for projects_uuid_get

        Project details by UUID
        """
        response = self.client.open(
            '/projects/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_patch(self):
        """Test case for projects_uuid_patch

        Update Project details as owner
        """
        body = ProjectsPatch()
        response = self.client.open(
            '/projects/{uuid}'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_personnel_patch(self):
        """Test case for projects_uuid_personnel_patch

        Update Project personnel as owner
        """
        body = ProjectsPersonnelPatch()
        response = self.client.open(
            '/projects/{uuid}/personnel'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_profile_patch(self):
        """Test case for projects_uuid_profile_patch

        Update Project Profile details as owner
        """
        body = ProfileProjects()
        response = self.client.open(
            '/projects/{uuid}/profile'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_tags_patch(self):
        """Test case for projects_uuid_tags_patch

        Update Projects Tags as Facility Operator
        """
        body = ProjectsTagsPatch()
        response = self.client.open(
            '/projects/{uuid}/tags'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_projects_uuid_token_holders_patch(self):
        """Test case for projects_uuid_token_holders_patch

        Update Project Long-Lived Token Holders as facility-operator
        """
        body = ProjectsTokenHoldersPatch()
        query_string = [('operation', 'add')]
        response = self.client.open(
            '/projects/{uuid}/token-holders'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
