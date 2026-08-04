# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.testbed_info import TestbedInfo  # noqa: E501
from swagger_server.models.testbed_info_post import TestbedInfoPost  # noqa: E501
from swagger_server.test import BaseTestCase


class TestTestbedInfoController(BaseTestCase):
    """TestbedInfoController integration test stubs"""

    def test_testbed_info_get(self):
        """Test case for testbed_info_get

        Testbed Information
        """
        response = self.client.open(
            '/testbed-info',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_testbed_info_post(self):
        """Test case for testbed_info_post

        Create Testbed Information
        """
        body = TestbedInfoPost()
        response = self.client.open(
            '/testbed-info',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
