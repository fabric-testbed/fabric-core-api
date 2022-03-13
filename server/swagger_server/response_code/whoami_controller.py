import connexion
import six

from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.whoami import Whoami  # noqa: E501
from swagger_server import util
from swagger_server.response_code import whoami_controller as rc


def whoami_get():  # noqa: E501
    """Who am I?

    Who am I? # noqa: E501


    :rtype: Whoami
    """
    return 'do some magic!'
