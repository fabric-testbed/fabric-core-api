# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.models.core_api_metrics_events import CoreApiMetricsEvents  # noqa: E501
from swagger_server.models.core_api_metrics_events_membership import CoreApiMetricsEventsMembership  # noqa: E501
from swagger_server.models.core_api_metrics_people import CoreApiMetricsPeople  # noqa: E501
from swagger_server.models.core_api_metrics_people_one import CoreApiMetricsPeopleOne  # noqa: E501
from swagger_server.models.core_api_metrics_projects import CoreApiMetricsProjects  # noqa: E501
from swagger_server.models.core_api_metrics_projects_one import CoreApiMetricsProjectsOne  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCoreApiMetricsController(BaseTestCase):
    """CoreApiMetricsController integration test stubs"""

    def test_core_api_metrics_events_get(self):
        """Test case for core_api_metrics_events_get

        Core API metrics events
        """
        query_string = [('event_type', 'all'),
                        ('start_date', 'start_date_example'),
                        ('end_date', 'end_date_example')]
        response = self.client.open(
            '/core-api-metrics/events',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_events_people_membership_uuid_get(self):
        """Test case for core_api_metrics_events_people_membership_uuid_get

        Core API metrics people membership by UUID
        """
        response = self.client.open(
            '/core-api-metrics/events/people-membership/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_events_projects_membership_uuid_get(self):
        """Test case for core_api_metrics_events_projects_membership_uuid_get

        Core API metrics projects membership by UUID
        """
        response = self.client.open(
            '/core-api-metrics/events/projects-membership/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_overview_get(self):
        """Test case for core_api_metrics_overview_get

        Core API metrics overview
        """
        response = self.client.open(
            '/core-api-metrics/overview',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_people_details_uuid_get(self):
        """Test case for core_api_metrics_people_details_uuid_get

        Core API metrics people details by UUID
        """
        response = self.client.open(
            '/core-api-metrics/people-details/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_people_get(self):
        """Test case for core_api_metrics_people_get

        Core API metrics people
        """
        response = self.client.open(
            '/core-api-metrics/people',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_projects_details_uuid_get(self):
        """Test case for core_api_metrics_projects_details_uuid_get

        Core API metrics projects details by UUID
        """
        response = self.client.open(
            '/core-api-metrics/projects-details/{uuid}'.format(uuid='uuid_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_core_api_metrics_projects_get(self):
        """Test case for core_api_metrics_projects_get

        Core API metrics projects
        """
        response = self.client.open(
            '/core-api-metrics/projects',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
