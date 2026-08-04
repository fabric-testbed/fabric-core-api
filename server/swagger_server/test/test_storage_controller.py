# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.storage import Storage  # noqa: E501
from swagger_server.models.storage_many import StorageMany  # noqa: E501
from swagger_server.models.storage_patch import StoragePatch  # noqa: E501
from swagger_server.models.storage_post import StoragePost  # noqa: E501
from swagger_server.test import BaseTestCase


class TestStorageController(BaseTestCase):
    """StorageController integration test stubs"""

    def test_storage_get(self):
        """Test case for storage_get

        Get active Storage allocations
        """
        query_string = [('offset', 1),
                        ('limit', 200),
                        ('project_uuid', 'project_uuid_example')]
        response = self.client.open(
            '/storage',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_storage_post(self):
        """Test case for storage_post

        Create a Storage allocation
        """
        body = StoragePost()
        response = self.client.open(
            '/storage',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_storage_sites_get(self):
        """Test case for storage_sites_get

        List of Storage site options
        """
        query_string = [('search', 'search_example')]
        response = self.client.open(
            '/storage/sites',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_storage_uuid_delete(self):
        """Test case for storage_uuid_delete

        Delete Storage allocation by UUID
        """
        response = self.client.open(
            '/storage/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_storage_uuid_get(self):
        """Test case for storage_uuid_get

        Storage allocation details by UUID
        """
        response = self.client.open(
            '/storage/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_storage_uuid_patch(self):
        """Test case for storage_uuid_patch

        Update existing Storage allocation
        """
        body = StoragePatch()
        response = self.client.open(
            '/storage/{uuid}'.format(uuid='uuid_example'),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
