# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.whoami import Whoami  # noqa: E501
from swagger_server.test import BaseTestCase


class TestWhoamiController(BaseTestCase):
    """WhoamiController integration test stubs"""

    def test_whoami_get(self):
        """Test case for whoami_get

        Who am I?
        """
        response = self.client.open(
            '/whoami',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
