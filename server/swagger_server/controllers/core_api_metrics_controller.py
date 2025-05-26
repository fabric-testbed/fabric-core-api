import connexion
import six

from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.models.core_api_metrics_events import CoreApiMetricsEvents  # noqa: E501
from swagger_server.models.core_api_metrics_events_membership import CoreApiMetricsEventsMembership  # noqa: E501
from swagger_server.models.core_api_metrics_people import CoreApiMetricsPeople  # noqa: E501
from swagger_server.models.core_api_metrics_people_one import CoreApiMetricsPeopleOne  # noqa: E501
from swagger_server.models.core_api_metrics_projects import CoreApiMetricsProjects  # noqa: E501
from swagger_server.models.core_api_metrics_projects_one import CoreApiMetricsProjectsOne  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import core_api_metrics_controller as rc


def core_api_metrics_events_get(event_type=None, start_date=None, end_date=None):  # noqa: E501
    """Core API metrics events

    Core API metrics events # noqa: E501

    :param event_type: event type
    :type event_type: str
    :param start_date: starting date to search from
    :type start_date: str
    :param end_date: end date to search to
    :type end_date: str

    :rtype: CoreApiMetricsEvents
    """
    return rc.core_api_metrics_events_get(event_type, start_date, end_date)


def core_api_metrics_events_people_uuid_get(uuid):  # noqa: E501
    """Core API metrics people event details by UUID

    Core API metrics people event details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsEventsMembership
    """
    return rc.core_api_metrics_events_people_uuid_get(uuid)


def core_api_metrics_events_projects_uuid_get(uuid):  # noqa: E501
    """Core API metrics projects event details by UUID

    Core API metrics projects event details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsEventsMembership
    """
    return rc.core_api_metrics_events_projects_uuid_get(uuid)


def core_api_metrics_overview_get():  # noqa: E501
    """Core API metrics overview

    Core API metrics overview # noqa: E501


    :rtype: CoreApiMetrics
    """
    return rc.core_api_metrics_overview_get()


def core_api_metrics_people_get():  # noqa: E501
    """Core API metrics people

    Core API metrics people # noqa: E501


    :rtype: CoreApiMetricsPeople
    """
    return rc.core_api_metrics_people_get()


def core_api_metrics_people_uuid_get(uuid):  # noqa: E501
    """Core API metrics people details by UUID

    Core API metrics people details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsPeopleOne
    """
    return rc.core_api_metrics_people_uuid_get(uuid)


def core_api_metrics_projects_get():  # noqa: E501
    """Core API metrics projects

    Core API metrics projects # noqa: E501


    :rtype: CoreApiMetricsProjects
    """
    return rc.core_api_metrics_projects_get()


def core_api_metrics_projects_uuid_get(uuid):  # noqa: E501
    """Core API metrics projects details by UUID

    Core API metrics projects details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsProjectsOne
    """
    return rc.core_api_metrics_projects_uuid_get(uuid)
