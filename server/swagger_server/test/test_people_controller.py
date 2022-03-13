# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.people import People  # noqa: E501
from swagger_server.models.people_details import PeopleDetails  # noqa: E501
from swagger_server.models.people_patch import PeoplePatch  # noqa: E501
from swagger_server.models.people_profile_patch import PeopleProfilePatch  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestPeopleController(BaseTestCase):
    """PeopleController integration test stubs"""

    def test_people_get(self):
        """Test case for people_get

        Search for FABRIC People
        """
        query_string = [('search', 'search_example'),
                        ('offset', 1),
                        ('limit', 20)]
        response = self.client.open(
            '/people',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_preferences_get(self):
        """Test case for people_preferences_get

        List of People Preference options
        """
        response = self.client.open(
            '/people/preferences',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_other_identity_types_get(self):
        """Test case for people_profile_other_identity_types_get

        List of People Profile Other Identity Type options
        """
        response = self.client.open(
            '/people/profile/other-identity-types',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_preferences_get(self):
        """Test case for people_profile_preferences_get

        List of People Profile Preference options
        """
        response = self.client.open(
            '/people/profile/preferences',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_professional_page_types_get(self):
        """Test case for people_profile_professional_page_types_get

        List of People Profile Professional Page Type options
        """
        response = self.client.open(
            '/people/profile/professional-page-types',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_social_page_types_get(self):
        """Test case for people_profile_social_page_types_get

        List of People Profile Social Page Type options
        """
        response = self.client.open(
            '/people/profile/social-page-types',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_uuid_get(self):
        """Test case for people_uuid_get

        Person details by UUID
        """
        query_string = [('as_self', false)]
        response = self.client.open(
            '/people/{uuid}'.format(uuid='uuid_example'),
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_uuid_patch(self):
        """Test case for people_uuid_patch

        Update Person details as Self
        """
        body = PeoplePatch()
        response = self.client.open(
            '/people/{uuid}'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_uuid_profile_patch(self):
        """Test case for people_uuid_profile_patch

        Update Person Profile details as Self
        """
        body = PeopleProfilePatch()
        response = self.client.open(
            '/people/{uuid}/profile'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
