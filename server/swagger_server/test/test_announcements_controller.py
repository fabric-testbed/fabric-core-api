# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.announcements import Announcements  # noqa: E501
from swagger_server.models.announcements_details import AnnouncementsDetails  # noqa: E501
from swagger_server.models.announcements_patch import AnnouncementsPatch  # noqa: E501
from swagger_server.models.announcements_post import AnnouncementsPost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAnnouncementsController(BaseTestCase):
    """AnnouncementsController integration test stubs"""

    def test_announcements_get(self):
        """Test case for announcements_get

        Search for FABRIC Announcements
        """
        query_string = [('announcement_type', 'announcement_type_example'),
                        ('is_active', true),
                        ('search', 'search_example'),
                        ('offset', 1),
                        ('limit', 200)]
        response = self.client.open(
            '/announcements',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_announcements_post(self):
        """Test case for announcements_post

        Create a new FABRIC Announcement
        """
        body = AnnouncementsPost()
        response = self.client.open(
            '/announcements',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_announcements_uuid_delete(self):
        """Test case for announcements_uuid_delete

        Delete Announcement as Portal Admin
        """
        response = self.client.open(
            '/announcements/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_announcements_uuid_get(self):
        """Test case for announcements_uuid_get

        Announcement details by UUID
        """
        response = self.client.open(
            '/announcements/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_announcements_uuid_patch(self):
        """Test case for announcements_uuid_patch

        Update Announcement details as Portal Admin
        """
        body = AnnouncementsPatch()
        response = self.client.open(
            '/announcements/{uuid}'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
