import connexion
import six

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.storage import Storage  # noqa: E501
from swagger_server.models.storage_many import StorageMany  # noqa: E501
from swagger_server.models.storage_patch import StoragePatch  # noqa: E501
from swagger_server.models.storage_post import StoragePost  # noqa: E501
from swagger_server import util
from swagger_server.response_code import storage_controller as rc


def storage_get(offset=None, limit=None, project_uuid=None):  # noqa: E501
    """Get active Storage allocations

    Get active Storage allocations # noqa: E501

    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int
    :param project_uuid: project uuid
    :type project_uuid: str

    :rtype: StorageMany
    """
    return rc.storage_get(offset, limit, project_uuid)


def storage_post(body=None):  # noqa: E501
    """Create a Storage allocation

    Create a Storage allocation # noqa: E501

    :param body: Create a Storage allocation
    :type body: dict | bytes

    :rtype: Storage
    """
    if connexion.request.is_json:
        body = StoragePost.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.storage_post(body)


def storage_sites_get(search=None):  # noqa: E501
    """List of Storage site options

    List of Storage site options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.storage_sites_get(search)


def storage_uuid_delete(uuid):  # noqa: E501
    """Delete Storage allocation by UUID

    Delete Storage allocation by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return rc.storage_uuid_delete(uuid)


def storage_uuid_get(uuid):  # noqa: E501
    """Storage allocation details by UUID

    Storage allocation details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Storage
    """
    return rc.storage_uuid_get(uuid)


def storage_uuid_patch(uuid, body=None):  # noqa: E501
    """Update existing Storage allocation

    Update existing Storage allocation # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update an existing Storage allocation
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = StoragePatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.storage_uuid_patch(uuid, body)
