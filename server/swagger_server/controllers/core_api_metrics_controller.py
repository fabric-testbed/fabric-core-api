import connexion
import six

from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import core_api_metrics_controller as rc


def core_api_metrics_overview_get():  # noqa: E501
    """Core API metrics overview

    Core API metrics overview # noqa: E501


    :rtype: CoreApiMetrics
    """
    return rc.core_api_metrics_overview_get()
