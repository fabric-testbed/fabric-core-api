# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.bastionkeys import Bastionkeys  # noqa: E501
from swagger_server.models.sshkey_pair import SshkeyPair  # noqa: E501
from swagger_server.models.sshkeys import Sshkeys  # noqa: E501
from swagger_server.models.sshkeys_post import SshkeysPost  # noqa: E501
from swagger_server.models.sshkeys_put import SshkeysPut  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestSshkeysController(BaseTestCase):
    """SshkeysController integration test stubs"""

    def test_bastionkeys_get(self):
        """Test case for bastionkeys_get

        Get active SSH Keys
        """
        query_string = [('secret', 'secret_example'),
                        ('since_date', 'since_date_example')]
        response = self.client.open(
            '/bastionkeys',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sshkeys_get(self):
        """Test case for sshkeys_get

        Get active SSH Keys
        """
        query_string = [('person_uuid', 'person_uuid_example')]
        response = self.client.open(
            '/sshkeys',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sshkeys_post(self):
        """Test case for sshkeys_post

        Create a public/private SSH Key Pair
        """
        body = SshkeysPost()
        response = self.client.open(
            '/sshkeys',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sshkeys_put(self):
        """Test case for sshkeys_put

        Add a public SSH Key
        """
        body = SshkeysPut()
        response = self.client.open(
            '/sshkeys',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sshkeys_uuid_delete(self):
        """Test case for sshkeys_uuid_delete

        Delete SSH Key by UUID
        """
        response = self.client.open(
            '/sshkeys/{uuid}'.format(uuid='uuid_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sshkeys_uuid_get(self):
        """Test case for sshkeys_uuid_get

        SSH Key details by UUID
        """
        response = self.client.open(
            '/sshkeys/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
