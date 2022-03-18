import connexion
import six
from swagger_server.response_code.decorators import login_required

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import publications_controller as rc


def publications_classification_terms_get(search=None):  # noqa: E501
    """List of Classification Terms

    List of Classification Terms # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return 'do some magic!'


def publications_get(search=None, offset=None, limit=None):  # noqa: E501
    """Publications (placeholder)

    Search for Publications by author or title # noqa: E501

    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_post():  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501


    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_uuid_delete(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


def publications_uuid_get(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_uuid_patch(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'
