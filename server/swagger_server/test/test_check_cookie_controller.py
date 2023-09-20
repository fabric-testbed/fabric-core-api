# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.check_cookie import CheckCookie  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCheckCookieController(BaseTestCase):
    """CheckCookieController integration test stubs"""

    def test_check_cookie_get(self):
        """Test case for check_cookie_get

        Check Cookie
        """
        response = self.client.open(
            '/check-cookie',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
