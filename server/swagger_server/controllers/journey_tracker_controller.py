import connexion
import six

from swagger_server.models.journey_tracker_people import JourneyTrackerPeople  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import journey_tracker_controller as rc


def journey_tracker_people_get(since_date, until_date=None):  # noqa: E501
    """Get people information for Journey Tracker

    Get people information for Journey Tracker # noqa: E501

    :param since_date: starting date to search from
    :type since_date: str
    :param until_date: ending date to search to
    :type until_date: str

    :rtype: JourneyTrackerPeople
    """
    return rc.journey_tracker_people_get(since_date, until_date)
