# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.quotas import Quotas  # noqa: E501
from swagger_server.models.quotas_details import QuotasDetails  # noqa: E501
from swagger_server.models.quotas_post import QuotasPost  # noqa: E501
from swagger_server.models.quotas_put import QuotasPut  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestQuotasController(BaseTestCase):
    """QuotasController integration test stubs"""

    def test_quotas_get(self):
        """Test case for quotas_get

        Get list of Resource Quotas
        """
        query_string = [('project_uuid', 'project_uuid_example'),
                        ('offset', 1),
                        ('limit', 200)]
        response = self.client.open(
            '/quotas',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_quotas_post(self):
        """Test case for quotas_post

        Create new Resource Quota
        """
        body = QuotasPost()
        response = self.client.open(
            '/quotas',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_quotas_uuid_delete(self):
        """Test case for quotas_uuid_delete

        Delete single Resource Quota by UUID
        """
        response = self.client.open(
            '/quotas/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_quotas_uuid_get(self):
        """Test case for quotas_uuid_get

        Get single Resource Quota by UUID
        """
        response = self.client.open(
            '/quotas/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_quotas_uuid_put(self):
        """Test case for quotas_uuid_put

        Update single Resource Quota by UUID
        """
        body = QuotasPut()
        response = self.client.open(
            '/quotas/{uuid}'.format(uuid='uuid_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
