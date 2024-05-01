# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCoreApiMetricsController(BaseTestCase):
    """CoreApiMetricsController integration test stubs"""

    def test_core_api_metrics_overview_get(self):
        """Test case for core_api_metrics_overview_get

        Core API metrics overview
        """
        response = self.client.open(
            '/core-api-metrics/overview',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
