import connexion
import six

from swagger_server.models.quotas import Quotas  # noqa: E501
from swagger_server.models.quotas_details import QuotasDetails  # noqa: E501
from swagger_server.models.quotas_post import QuotasPost  # noqa: E501
from swagger_server.models.quotas_put import QuotasPut  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import quotas_controller as rc


def quotas_get(project_uuid=None, offset=None, limit=None):  # noqa: E501
    """Get list of Resource Quotas

    Get list of Resource Quotas # noqa: E501

    :param project_uuid: project uuid
    :type project_uuid: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: Quotas
    """
    return rc.quotas_get(project_uuid, offset, limit)


def quotas_post(body=None):  # noqa: E501
    """Create new Resource Quota

    Create new Resource Quota # noqa: E501

    :param body: Create a new Resource Quota
    :type body: dict | bytes

    :rtype: Quotas
    """
    if connexion.request.is_json:
        body = QuotasPost.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.quotas_post(body)


def quotas_uuid_delete(uuid):  # noqa: E501
    """Delete single Resource Quota by UUID

    Delete single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return rc.quotas_uuid_delete(uuid)


def quotas_uuid_get(uuid):  # noqa: E501
    """Get single Resource Quota by UUID

    Get single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: QuotasDetails
    """
    return rc.quotas_uuid_get(uuid)


def quotas_uuid_put(uuid, body=None):  # noqa: E501
    """Update single Resource Quota by UUID

    Update single Resource Quota by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update a Resource Quota
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = QuotasPut.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.quotas_uuid_put(uuid, body)
