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
from swagger_server.test import BaseTestCase


class TestPublicationsController(BaseTestCase):
    """PublicationsController integration test stubs"""

    def test_publications_category_types_get(self):
        """Test case for publications_category_types_get

        List of Category Type options
        """
        response = self.client.open(
            '/publications/category-types',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_publications_get(self):
        """Test case for publications_get

        Publications (placeholder)
        """
        query_string = [('search', 'search_example'),
                        ('offset', 1),
                        ('limit', 20)]
        response = self.client.open(
            '/publications',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_publications_post(self):
        """Test case for publications_post

        Publications (placeholder)
        """
        response = self.client.open(
            '/publications',
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_publications_uuid_delete(self):
        """Test case for publications_uuid_delete

        Publications (placeholder)
        """
        response = self.client.open(
            '/publications/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_publications_uuid_get(self):
        """Test case for publications_uuid_get

        Publications (placeholder)
        """
        response = self.client.open(
            '/publications/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_publications_uuid_patch(self):
        """Test case for publications_uuid_patch

        Publications (placeholder)
        """
        response = self.client.open(
            '/publications/{uuid}'.format(uuid='uuid_example'),
            method='PATCH')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
