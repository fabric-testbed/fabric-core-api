# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.facility_update_patch import FacilityUpdatePatch  # noqa: E501
from swagger_server.models.facility_update_post import FacilityUpdatePost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.updates import Updates  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUpdatesController(BaseTestCase):
    """UpdatesController integration test stubs"""

    def test_updates_get(self):
        """Test case for updates_get

        Facility Updates (placeholder)
        """
        response = self.client.open(
            '/updates',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_updates_post(self):
        """Test case for updates_post

        Facility Updates (placeholder)
        """
        body = FacilityUpdatePost()
        response = self.client.open(
            '/updates',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_updates_uuid_delete(self):
        """Test case for updates_uuid_delete

        Facility Updates (placeholder)
        """
        response = self.client.open(
            '/updates/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_updates_uuid_get(self):
        """Test case for updates_uuid_get

        Facility Updates (placeholder)
        """
        response = self.client.open(
            '/updates/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_updates_uuid_patch(self):
        """Test case for updates_uuid_patch

        Facility Updates (placeholder)
        """
        body = FacilityUpdatePatch()
        response = self.client.open(
            '/updates/{uuid}'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
