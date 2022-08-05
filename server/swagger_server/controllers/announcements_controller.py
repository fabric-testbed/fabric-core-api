import connexion
import six

from swagger_server.models.announcements import Announcements  # noqa: E501
from swagger_server.models.announcements_patch import AnnouncementsPatch  # noqa: E501
from swagger_server.models.announcements_post import AnnouncementsPost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import announcements_controller as rc


def announcements_get(type=None, is_active=None, search=None):  # noqa: E501
    """Search for FABRIC Announcements

    Search for FABRIC Announcements # noqa: E501

    :param type: announcement type
    :type type: str
    :param is_active: is active
    :type is_active: bool
    :param search: search term applied
    :type search: str

    :rtype: Announcements
    """
    return rc.announcements_get(type, is_active, search)


def announcements_post(body=None):  # noqa: E501
    """Create a new FABRIC Announcement

    Create a new FABRIC Announcement # noqa: E501

    :param body: Create an announcement
    :type body: dict | bytes

    :rtype: Announcements
    """
    if connexion.request.is_json:
        body = AnnouncementsPost.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.announcements_post(body)


def announcments_uuid_delete(uuid):  # noqa: E501
    """Delete Announcement as Portal Admin

    Delete Announcement as Portal Admin # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return rc.announcments_uuid_delete(uuid)


def announcments_uuid_get(uuid):  # noqa: E501
    """Announcement details by UUID

    Announcement details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Announcements
    """
    return rc.announcments_uuid_get(uuid)


def announcments_uuid_patch(uuid, body=None):  # noqa: E501
    """Update Announcement details as Portal Admin

    Update Announcement details as Portal Admin # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update an existing announcement
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = AnnouncementsPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.announcments_uuid_patch(uuid, body)
