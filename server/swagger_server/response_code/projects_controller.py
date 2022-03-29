import connexion
import six
import logging
from swagger_server.response_code.decorators import login_required

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.projects import Projects  # noqa: E501
from swagger_server.models.projects_details import ProjectsDetails  # noqa: E501
from swagger_server.models.projects_patch import ProjectsPatch  # noqa: E501
from swagger_server.models.projects_personnel_patch import ProjectsPersonnelPatch  # noqa: E501
from swagger_server.models.projects_post import ProjectsPost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import PROJECTS_PREFERENCES, PROJECTS_PROFILE_PREFERENCES, PROJECTS_TAGS
from swagger_server.response_code.cors_response import cors_200, cors_500

logger = logging.getLogger(__name__)


@login_required
def projects_get(search=None, offset=None, limit=None, person_uuid=None):  # noqa: E501
    """Search for FABRIC Projects

    Search for FABRIC Projects by name # noqa: E501

    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int
    :param person_uuid: person uuid
    :type person_uuid: str

    :rtype: Projects
    """
    return 'do some magic!'


@login_required
def projects_post(body=None):  # noqa: E501
    """Create new Project

    Create new Project # noqa: E501

    :param body: Create new Project
    :type body: dict | bytes

    :rtype: ProjectsDetails
    """
    return 'do some magic!'


def projects_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Preference options

    List of Projects Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PROJECTS_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PROJECTS_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PROJECTS_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("projects_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Preferences.Get()')


def projects_profile_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Profile Preference options

    List of Projects Profile Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PROJECTS_PROFILE_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PROJECTS_PROFILE_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PROJECTS_PROFILE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("projects_profile_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Profile.Preferences.Get()')


def projects_tags_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Tags options

    List of Projects Tags options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PROJECTS_TAGS.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PROJECTS_TAGS.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PROJECTS_TAGS.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("projects_tags_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Tags.Get()')


@login_required
def projects_uuid_delete(uuid):  # noqa: E501
    """Delete Project as owner

    Delete Project as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def projects_uuid_get(uuid):  # noqa: E501
    """Project details by UUID

    Project details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: ProjectsDetails
    """
    return 'do some magic!'


@login_required
def projects_uuid_patch(uuid, body=None):  # noqa: E501
    """Update Project details as owner

    Update Project details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def projects_uuid_personnel_patch(uuid, body=None):  # noqa: E501
    """Update Project personnel as owner

    Update Project personnel as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project personnel as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def projects_uuid_profile_patch(uuid, body=None):  # noqa: E501
    """Update Project Profile details as owner

    Update Project Profile details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Profile details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def projects_uuid_tags_patch(uuid, body=None):  # noqa: E501
    """Update Projects Tags as Facility Operator

    Update Projects Tags as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Tags as Facility Operator
    :type body: List[]

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'
