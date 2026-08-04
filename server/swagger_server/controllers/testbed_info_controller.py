import connexion
import six

from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.testbed_info import TestbedInfo  # noqa: E501
from swagger_server.models.testbed_info_post import TestbedInfoPost  # noqa: E501
from swagger_server import util
from swagger_server.response_code import testbed_info_controller as rc


def testbed_info_get():  # noqa: E501
    """Testbed Information

    Testbed Information # noqa: E501


    :rtype: TestbedInfo
    """
    return rc.testbed_info_get()


def testbed_info_post(body=None):  # noqa: E501
    """Create Testbed Information

    Create Testbed Information # noqa: E501

    :param body: Create Testbed Information
    :type body: dict | bytes

    :rtype: TestbedInfo
    """
    if connexion.request.is_json:
        body = TestbedInfoPost.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.testbed_info_post(body)
