import logging
import os

from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.projects import FabricProjects
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.projects import Project, Projects  # noqa: E501
from swagger_server.models.projects_details import ProjectsOne, ProjectsDetails  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status200_ok_paginated import Status200OkPaginatedLinks
from swagger_server.response_code import PROJECTS_PREFERENCES, PROJECTS_PROFILE_PREFERENCES, PROJECTS_TAGS
from swagger_server.response_code.cors_response import cors_200, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.profiles_utils import get_profile_projects
from swagger_server.response_code.projects_utils import get_project_membership, get_projects_personnel

logger = logging.getLogger(__name__)

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


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

    {
        "created": "string",
        "description": "string",
        "facility": "string",
        "is_public": true,
        "memberships": {
            "is_creator": false,
            "is_member": false,
            "is_owner": false
        },
        "name": "string",
        "uuid": "string"
    }
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        as_self = True
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # check for person_uuid
        if person_uuid:
            fab_person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
            if not fab_person:
                return cors_404(details="No match for Person with uuid = '{0}'".format(person_uuid))
        else:
            fab_person = None
        # set page to retrieve
        _page = int((offset + limit) / limit)
        # get paginated results
        if not search and not person_uuid:
            base = '{0}/projects?'.format(_SERVER_URL)
            data_page = FabricProjects.query.filter(
                FabricProjects.active.is_(True)
            ).order_by(FabricProjects.name).paginate(
                page=_page, per_page=limit, error_out=False)
        elif search and not person_uuid:
            base = '{0}/projects?search={1}&'.format(_SERVER_URL, search)
            data_page = FabricProjects.query.filter(
                (FabricProjects.active.is_(True)) &
                (FabricProjects.name.ilike("%" + search + "%")) |
                (FabricProjects.description.ilike("%" + search + "%"))
            ).order_by(FabricProjects.name).paginate(page=_page, per_page=limit, error_out=False)
        elif not search and person_uuid:
            base = '{0}/projects?person_uuid={1}&'.format(_SERVER_URL, person_uuid)
            if api_user.uuid == person_uuid:
                data_page = FabricProjects.query.filter(
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in api_user.roles])
                ).order_by(FabricProjects.name).paginate(
                    page=_page, per_page=limit, error_out=False)
            else:
                as_self = False
                data_page = FabricProjects.query.filter(
                    FabricProjects.active.is_(True) &
                    FabricProjects.is_public.is_(True) &
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles])
                ).order_by(FabricProjects.name).paginate(
                    page=_page, per_page=limit, error_out=False)
        else:
            base = '{0}/projects?search={1}&person_uuid={2}&'.format(_SERVER_URL, search, person_uuid)
            if api_user.uuid == person_uuid:
                data_page = FabricProjects.query.filter(
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in api_user.roles])
                ).order_by(FabricProjects.name).paginate(
                    page=_page, per_page=limit, error_out=False)
            else:
                as_self = False
                data_page = FabricProjects.query.filter(
                    FabricProjects.active.is_(True) &
                    FabricProjects.is_public.is_(True) &
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles]) &
                    (FabricProjects.name.ilike("%" + search + "%") |
                     FabricProjects.description.ilike("%" + search + "%"))
                ).order_by(FabricProjects.name).paginate(
                    page=_page, per_page=limit, error_out=False)
        # set projects response
        response = Projects()
        response.data = []
        for item in data_page.items:
            project = Project()
            # set project attributes
            project.created = str(item.created)
            project.description = item.description
            project.facility = item.facility
            project.is_public = item.is_public
            if as_self:
                project.memberships = get_project_membership(fab_project=item, fab_person=api_user)
            else:
                project.memberships = get_project_membership(fab_project=item, fab_person=fab_person)
            project.name = item.name
            project.uuid = item.uuid
            # add project to projects data
            response.data.append(project)
        # set links
        response.links = Status200OkPaginatedLinks()
        _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
        response.links.first = _URL_OFFSET_LIMIT.format(base, 0, limit) if data_page.pages > 0 else None
        response.links.last = _URL_OFFSET_LIMIT.format(base, int((data_page.pages - 1) * limit),
                                                       limit) if data_page.pages > 0 else None
        response.links.next = _URL_OFFSET_LIMIT.format(base, int(offset + limit), limit) if data_page.has_next else None
        response.links.prev = _URL_OFFSET_LIMIT.format(base, int(offset - limit), limit) if data_page.has_prev else None
        # set offset, limit and size
        response.limit = limit
        response.offset = offset
        response.total = data_page.total
        response.size = len(response.data)
        response.type = 'projects'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with projects_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


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
def projects_uuid_delete(uuid: str):  # noqa: E501
    """Delete Project as owner

    Delete Project as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def projects_uuid_get(uuid: str) -> ProjectsDetails:  # noqa: E501
    """Project details by UUID

    Project details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: ProjectsDetails
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get person by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # set ProjectsOne object
        project_one = ProjectsOne()
        # set required attributes for any uuid
        project_one.created = str(fab_project.created)
        project_one.description = fab_project.description
        project_one.facility = fab_project.facility
        project_one.is_public = fab_project.is_public
        project_one.memberships = get_project_membership(fab_project=fab_project, fab_person=api_user)
        project_one.name = fab_project.name
        project_one.uuid = fab_project.uuid
        # set remaining attributes for project_creators and project_owners
        if project_one.memberships.is_creator or project_one.memberships.is_owner:
            project_one.active = fab_project.active
            project_one.modified = str(fab_project.modified)
            project_one.preferences = {p.key: p.value for p in fab_project.preferences}
            project_one.profile = get_profile_projects(
                profile_projects_id=fab_project.profile.id,
                as_owner=(project_one.memberships.is_creator or project_one.memberships.is_owner))
            project_one.project_creators = get_projects_personnel(fab_project=fab_project, personnel_type='creators')
            project_one.project_members = get_projects_personnel(fab_project=fab_project, personnel_type='members')
            project_one.project_owners = get_projects_personnel(fab_project=fab_project, personnel_type='owners')
            project_one.publications = []
            project_one.tags = [t.tag for t in fab_project.tags]
        # set remaining attributes for everyone else
        else:
            if not fab_project.is_public and not project_one.memberships.is_member:
                return cors_403(
                    details="User: '{0}' does not have access to this private project".format(api_user.display_name))
            project_prefs = {p.key: p.value for p in fab_project.preferences}
            project_one.active = fab_project.active
            project_one.modified = str(fab_project.modified)
            project_one.profile = get_profile_projects(
                profile_projects_id=fab_project.profile.id,
                as_owner=(project_one.memberships.is_creator or project_one.memberships.is_owner)) if project_prefs.get(
                'show_profile') else None
            project_one.project_creators = get_projects_personnel(fab_project=fab_project,
                                                                  personnel_type='creators') if project_prefs.get(
                'show_project_creators') else None
            project_one.project_members = get_projects_personnel(fab_project=fab_project,
                                                                 personnel_type='members') if project_prefs.get(
                'show_project_members') else None
            project_one.project_owners = get_projects_personnel(fab_project=fab_project,
                                                                personnel_type='owners') if project_prefs.get(
                'show_project_owners') else None
            project_one.publications = []
            project_one.tags = [t.tag for t in fab_project.tags]
        # set project_details response
        response = ProjectsDetails()
        response.data = [project_one]
        response.size = len(response.data)
        response.status = 200
        response.type = 'projects.details'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


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
