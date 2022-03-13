import connexion
import six

from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.version import Version  # noqa: E501
from swagger_server import util
from swagger_server.response_code import version_controller as rc


def version_get():  # noqa: E501
    """Version

    Version # noqa: E501


    :rtype: Version
    """
    return 'do some magic!'
