import connexion
import six

from swagger_server.models.check_cookie import CheckCookie  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import check_cookie_controller as rc


def check_cookie_get():  # noqa: E501
    """Check Cookie

    Check Cookie # noqa: E501


    :rtype: CheckCookie
    """
    return rc.check_cookie_get()
