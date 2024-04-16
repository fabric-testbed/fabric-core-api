# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.people import People  # noqa: E501
from swagger_server.models.people_details import PeopleDetails  # noqa: E501
from swagger_server.models.people_patch import PeoplePatch  # noqa: E501
from swagger_server.models.profile_people import ProfilePeople  # noqa: E501
from swagger_server.models.service_auth_details import ServiceAuthDetails  # noqa: E501
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
                        ('exact_match', false),
                        ('offset', 1),
                        ('limit', 200)]
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
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/people/preferences',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_otheridentity_types_get(self):
        """Test case for people_profile_otheridentity_types_get

        List of People Profile Other Identity Type options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/people/profile/otheridentity-types',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_personalpage_types_get(self):
        """Test case for people_profile_personalpage_types_get

        List of People Profile Personal Page Type options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/people/profile/personalpage-types',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_profile_preferences_get(self):
        """Test case for people_profile_preferences_get

        List of People Profile Preference options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/people/profile/preferences',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_people_services_auth_get(self):
        """Test case for people_services_auth_get

        Service authorization details by OIDC sub
        """
        query_string = [('sub', 'sub_example')]
        response = self.client.open(
            '/people/services-auth',
            method='GET',
            query_string=query_string)
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
        body = ProfilePeople()
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
