import connexion
import six

from swagger_server.models.bastionkeys import Bastionkeys  # noqa: E501
from swagger_server.models.sshkey_pair import SshkeyPair  # noqa: E501
from swagger_server.models.sshkeys import Sshkeys  # noqa: E501
from swagger_server.models.sshkeys_post import SshkeysPost  # noqa: E501
from swagger_server.models.sshkeys_put import SshkeysPut  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import sshkeys_controller as rc


def bastionkeys_get(secret, since_date):  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param secret: unique secret token
    :type secret: dict | bytes
    :param since_date: starting date to search from
    :type since_date: str

    :rtype: Bastionkeys
    """
    return 'do some magic!'


def sshkeys_get(person_uuid=None):  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param person_uuid: person uuid
    :type person_uuid: str

    :rtype: Sshkeys
    """
    return 'do some magic!'


def sshkeys_post(body=None):  # noqa: E501
    """Create a public/private SSH Key Pair

    Create a public/private SSH Key Pair # noqa: E501

    :param body: Create a public/private SSH Key Pair
    :type body: dict | bytes

    :rtype: SshkeyPair
    """
    return 'do some magic!'


def sshkeys_put(body=None):  # noqa: E501
    """Add a public SSH Key

    Add a public SSH Key # noqa: E501

    :param body: Add a public SSH Key
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


def sshkeys_uuid_delete(uuid):  # noqa: E501
    """Delete SSH Key by UUID

    Delete SSH Key by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


def sshkeys_uuid_get(uuid):  # noqa: E501
    """SSH Key details by UUID

    SSH Key details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'
