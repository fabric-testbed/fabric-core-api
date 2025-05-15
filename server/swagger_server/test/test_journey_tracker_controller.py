# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.journey_tracker_people import JourneyTrackerPeople  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestJourneyTrackerController(BaseTestCase):
    """JourneyTrackerController integration test stubs"""

    def test_journey_tracker_people_get(self):
        """Test case for journey_tracker_people_get

        Get people information for Journey Tracker
        """
        query_string = [('start_date', 'start_date_example'),
                        ('end_date', 'end_date_example')]
        response = self.client.open(
            '/journey-tracker/people',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
