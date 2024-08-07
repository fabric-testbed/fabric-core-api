import connexion
import six

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.profile_projects import ProfileProjects  # noqa: E501
from swagger_server.models.projects import Projects  # noqa: E501
from swagger_server.models.projects_communities_patch import ProjectsCommunitiesPatch  # noqa: E501
from swagger_server.models.projects_creators_patch import ProjectsCreatorsPatch  # noqa: E501
from swagger_server.models.projects_details import ProjectsDetails  # noqa: E501
from swagger_server.models.projects_expires_on_patch import ProjectsExpiresOnPatch  # noqa: E501
from swagger_server.models.projects_funding_patch import ProjectsFundingPatch  # noqa: E501
from swagger_server.models.projects_members_patch import ProjectsMembersPatch  # noqa: E501
from swagger_server.models.projects_owners_patch import ProjectsOwnersPatch  # noqa: E501
from swagger_server.models.projects_patch import ProjectsPatch  # noqa: E501
from swagger_server.models.projects_personnel_patch import ProjectsPersonnelPatch  # noqa: E501
from swagger_server.models.projects_post import ProjectsPost  # noqa: E501
from swagger_server.models.projects_tags_patch import ProjectsTagsPatch  # noqa: E501
from swagger_server.models.projects_token_holders_patch import ProjectsTokenHoldersPatch  # noqa: E501
from swagger_server.models.projects_topics_patch import ProjectsTopicsPatch  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status423_locked import Status423Locked  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import projects_controller as rc


def projects_communities_get(search=None):  # noqa: E501
    """List of Projects Communities options

    List of Projects Communities options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_communities_get(search)


def projects_funding_agencies_get(search=None):  # noqa: E501
    """List of Projects Funding Agency options

    List of Projects Funding Agency options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_funding_agencies_get(search)


def projects_funding_directorates_get(search=None):  # noqa: E501
    """List of Projects Funding Directorate options

    List of Projects Funding Directorate options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_funding_directorates_get(search)


def projects_get(search=None, search_set=None, exact_match=None, offset=None, limit=None, person_uuid=None, sort_by=None, order_by=None):  # noqa: E501
    """Search for FABRIC Projects

    Search for FABRIC Projects by name # noqa: E501

    :param search: search term applied
    :type search: str
    :param search_set: search set
    :type search_set: str
    :param exact_match: Exact Match for Search term
    :type exact_match: bool
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int
    :param person_uuid: person uuid
    :type person_uuid: str
    :param sort_by: sort by
    :type sort_by: str
    :param order_by: order by
    :type order_by: str

    :rtype: Projects
    """
    return rc.projects_get(search, search_set, exact_match, offset, limit, person_uuid, sort_by, order_by)


def projects_post(body=None):  # noqa: E501
    """Create new Project

    Create new Project # noqa: E501

    :param body: Create new Project
    :type body: dict | bytes

    :rtype: ProjectsDetails
    """
    if connexion.request.is_json:
        body = ProjectsPost.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_post(body)


def projects_preferences_get(search=None):  # noqa: E501
    """List of Projects Preference options

    List of Projects Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_preferences_get(search)


def projects_profile_preferences_get(search=None):  # noqa: E501
    """List of Projects Profile Preference options

    List of Projects Profile Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_profile_preferences_get(search)


def projects_project_types_get(search=None):  # noqa: E501
    """List of Projects Type options

    List of Projects Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_project_types_get(search)


def projects_tags_get(search=None):  # noqa: E501
    """List of Projects Tags options

    List of Projects Tags options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    return rc.projects_tags_get(search)


def projects_uuid_communities_patch(uuid, body=None):  # noqa: E501
    """Update Project Communities as Project creator/owner

    Update Project Communities as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Communities as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsCommunitiesPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_communities_patch(uuid, body)


def projects_uuid_delete(uuid):  # noqa: E501
    """Delete Project as owner

    Delete Project as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return rc.projects_uuid_delete(uuid)


def projects_uuid_expires_on_patch(uuid, body=None):  # noqa: E501
    """Update Project expires on date as Facility Operator

    Update Project expires on date as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project expires on date as Facility Operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsExpiresOnPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_expires_on_patch(uuid, body)


def projects_uuid_get(uuid):  # noqa: E501
    """Project details by UUID

    Project details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: ProjectsDetails
    """
    return rc.projects_uuid_get(uuid)


def projects_uuid_patch(uuid, body=None):  # noqa: E501
    """Update Project details as owner

    Update Project details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_patch(uuid, body)


def projects_uuid_personnel_patch(uuid, body=None):  # noqa: E501
    """Update Project personnel as owner

    Update Project personnel as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project personnel as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsPersonnelPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_personnel_patch(uuid, body)


def projects_uuid_profile_patch(uuid, body=None):  # noqa: E501
    """Update Project Profile details as owner

    Update Project Profile details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Profile details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProfileProjects.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_profile_patch(uuid, body)


def projects_uuid_project_creators_patch(operation, uuid, body=None):  # noqa: E501
    """Update Project Creators as facility-operator

    Update Project Creators as facility-operator # noqa: E501

    :param operation: operation to be performed
    :type operation: str
    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Creators as facility-operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsCreatorsPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_project_creators_patch(operation, uuid, body)


def projects_uuid_project_funding_patch(uuid, body=None):  # noqa: E501
    """Update Project Funding as Project creator/owner

    Update Project Funding as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Funding Source as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsFundingPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_project_funding_patch(uuid, body)


def projects_uuid_project_members_patch(operation, uuid, body=None):  # noqa: E501
    """Update Project Members as project creator or owner

    Update Project Members as project creator or owner # noqa: E501

    :param operation: operation to be performed
    :type operation: str
    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Members as project owner or creator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsMembersPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_project_members_patch(operation, uuid, body)


def projects_uuid_project_owners_patch(operation, uuid, body=None):  # noqa: E501
    """Update Project Owners as project creator or owner

    Update Project Owners as project creator or owner # noqa: E501

    :param operation: operation to be performed
    :type operation: str
    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Owners as project owner or creator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsOwnersPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_project_owners_patch(operation, uuid, body)


def projects_uuid_tags_patch(uuid, body=None):  # noqa: E501
    """Update Project Tags as Facility Operator

    Update Project Tags as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Tags as Facility Operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsTagsPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_tags_patch(uuid, body)


def projects_uuid_token_holders_patch(operation, uuid, body=None):  # noqa: E501
    """Update Project Long-Lived Token Holders as facility-operator

    Update Project Long-Lived Token Holders as facility-operator # noqa: E501

    :param operation: operation to be performed
    :type operation: str
    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Long-Lived Token Holders as facility-operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsTokenHoldersPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_token_holders_patch(operation, uuid, body)


def projects_uuid_topics_patch(uuid, body=None):  # noqa: E501
    """Update Project Topics as Project creator/owner

    Update Project Topics as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Topics as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    if connexion.request.is_json:
        body = ProjectsTopicsPatch.from_dict(connexion.request.get_json())  # noqa: E501
    return rc.projects_uuid_topics_patch(uuid, body)
