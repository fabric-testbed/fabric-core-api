import enum
import os
from datetime import datetime, timezone

from sqlalchemy import func

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import EnumEvents, EnumEventTypes
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.preferences import EnumPreferenceTypes, FabricPreferences
from swagger_server.database.models.profiles import FabricProfilesProjects
from swagger_server.database.models.projects import EnumProjectTypes, FabricProjects, ProjectsCommunities, \
    ProjectsTopics
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.profile_projects import ProfileProjects
from swagger_server.models.projects import Project, Projects  # noqa: E501
from swagger_server.models.projects_communities_patch import ProjectsCommunitiesPatch
from swagger_server.models.projects_creators_patch import ProjectsCreatorsPatch
from swagger_server.models.projects_details import ProjectsDetails, ProjectsOne  # noqa: E501
from swagger_server.models.projects_expires_on_patch import ProjectsExpiresOnPatch
from swagger_server.models.projects_funding_patch_project_funding import ProjectsFundingPatchProjectFunding
from swagger_server.models.projects_members_patch import ProjectsMembersPatch
from swagger_server.models.projects_owners_patch import ProjectsOwnersPatch
from swagger_server.models.projects_patch import ProjectsPatch
from swagger_server.models.projects_personnel_patch import ProjectsPersonnelPatch
from swagger_server.models.projects_post import ProjectsPost
from swagger_server.models.projects_tags_patch import ProjectsTagsPatch
from swagger_server.models.projects_token_holders_patch import ProjectsTokenHoldersPatch
from swagger_server.models.projects_topics_patch import ProjectsTopicsPatch
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.models.status200_ok_paginated import Status200OkPaginatedLinks
from swagger_server.response_code import (PROJECTS_COMMUNITIES, PROJECTS_FUNDING_AGENCIES,
                                          PROJECTS_FUNDING_DIRECTORATES, PROJECTS_PREFERENCES,
                                          PROJECTS_PROFILE_PREFERENCES, PROJECTS_TAGS)
from swagger_server.response_code.comanage_utils import delete_comanage_group, update_comanage_group
from swagger_server.response_code.core_api_utils import add_core_api_event, normalize_date_to_utc
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_423, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.preferences_utils import delete_projects_preferences
from swagger_server.response_code.profiles_utils import delete_profile_projects, get_fabric_matrix, \
    get_profile_projects, update_profiles_projects_keywords, update_profiles_projects_references
from swagger_server.response_code.projects_utils import create_fabric_project_from_api, get_project_membership, \
    get_project_tags, get_projects_personnel, get_projects_quotas, get_projects_storage, projects_set_active, \
    update_projects_communities, update_projects_personnel, update_projects_project_funding, update_projects_tags, \
    update_projects_token_holders, update_projects_topics
from swagger_server.response_code.response_utils import is_valid_url

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


class EnumSearchSetTypes(enum.Enum):
    communities = 1
    description = 2
    topics = 3
    type = 4


def projects_communities_get(search=None):  # noqa: E501
    """List of Projects Communities options

    List of Projects Communities options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [pc for pc in PROJECTS_COMMUNITIES.search(search) if search.casefold() in pc.casefold()]
        else:
            results = PROJECTS_COMMUNITIES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_COMMUNITIES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_communities_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Communities.Get()')


def projects_funding_agencies_get(search=None):  # noqa: E501
    """List of Projects Funding Agency options

    List of Projects Funding Agency options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [fa for fa in PROJECTS_FUNDING_AGENCIES.search(search) if search.casefold() in fa.casefold()]
        else:
            results = PROJECTS_FUNDING_AGENCIES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_FUNDING_AGENCIES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_funding_agencies_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with projects_funding_agencies_get()')


def projects_funding_directorates_get(search=None):  # noqa: E501
    """List of Projects Funding Directorate options

    List of Projects Funding Directorate options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [fd for fd in PROJECTS_FUNDING_DIRECTORATES.search(search) if search.casefold() in fd.casefold()]
        else:
            results = PROJECTS_FUNDING_DIRECTORATES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_FUNDING_DIRECTORATES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_funding_directorates_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Funding_Directorate.Get()')


# @login_or_token_required
def projects_get(search=None, search_set=None, exact_match=None, offset=None, limit=None, person_uuid=None,
                 sort_by=None, order_by=None) -> Projects:  # noqa: E501
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
    {
      "communities": [
        "string"
      ],
      "created": "string",
      "description": "string",
      "expires_on": "string",
      "facility": "string",
      "is_public": true,
      "memberships": {
        "is_creator": false,
        "is_member": false,
        "is_owner": false,
        "is_token_holder": false
      },
      "name": "string",
      "tags": [
        "string"
      ],
      "topics": [
        "string"
      ],
      "project_type": "string",
      "uuid": "string"
    }
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        as_self = True
        # establish if call is anonymous
        if not id_source:
            is_anonymous = True
            fab_person = None
            if person_uuid:
                return cors_400(
                    details='project_get(): anonymous api_user is not allowed to search projects by person_uuid')
        else:
            is_anonymous = False
            # check api_user active flag
            if not api_user.active:
                return cors_403(
                    details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
            # check for person_uuid
            if person_uuid:
                fab_person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
                if not fab_person:
                    return cors_404(details="No match for Person with uuid = '{0}'".format(person_uuid))
        # set page to retrieve
        _page = int((offset + limit) / limit)
        # sort_order query and path
        if sort_by.casefold() == 'created_time':
            if order_by.casefold() == 'asc':
                _sort_order_query = FabricProjects.created.asc()
                _sort_order_path = 'sort_by=created_time&order_by=asc&'
            else:
                _sort_order_query = FabricProjects.created.desc()
                _sort_order_path = 'sort_by=created_time&order_by=desc&'
        elif sort_by.casefold() == 'modified_time':
            if order_by.casefold() == 'asc':
                _sort_order_query = FabricProjects.modified.asc()
                _sort_order_path = 'sort_by=modified_time&order_by=asc&'
            else:
                _sort_order_query = FabricProjects.modified.desc()
                _sort_order_path = 'sort_by=modified_time&order_by=desc&'
        elif sort_by.casefold() == 'name':
            if order_by.casefold() == 'asc':
                _sort_order_query = FabricProjects.name.asc()
                _sort_order_path = 'sort_by=name&order_by=asc&'
            else:
                _sort_order_query = FabricProjects.name.desc()
                _sort_order_path = 'sort_by=name&order_by=desc&'
        else:
            _sort_order_query = FabricProjects.name.asc()
            _sort_order_path = 'sort_by=name&order_by=asc&'
        # is_public_check
        if not is_anonymous:
            is_public_check = (
                    FabricProjects.is_public.is_(True) |
                    FabricProjects.project_creators.any(FabricPeople.id == api_user.id) |
                    FabricProjects.project_owners.any(FabricPeople.id == api_user.id) |
                    FabricProjects.project_members.any(FabricPeople.id == api_user.id) |
                    api_user.is_facility_operator() |
                    api_user.is_facility_viewer()
            )
        else:
            is_public_check = (
                FabricProjects.is_public.is_(True)
            )
        # search by search_set
        if not search and not person_uuid:
            base = '{0}/projects?{1}'.format(_SERVER_URL, _sort_order_path)
            # anonymous users only get active projects
            if is_anonymous:
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    FabricProjects.active.is_(True)
                ).order_by(_sort_order_query).paginate(
                    page=_page, per_page=limit, error_out=False)
            # authenticated users get active / retired projects
            else:
                results_page = FabricProjects.query.filter(
                    is_public_check
                ).order_by(_sort_order_query).paginate(
                    page=_page, per_page=limit, error_out=False)
        elif search and not person_uuid:
            base = '{0}/projects?search={1}&{2}'.format(_SERVER_URL, search, _sort_order_path)
            # search_set
            if search_set == EnumSearchSetTypes.communities.name:
                # communities
                search_terms = [i.strip() for i in str(search).casefold().split(',')]
                project_ids = [p.projects_id for p in ProjectsCommunities.query.filter(
                    func.lower(ProjectsCommunities.community).in_(search_terms)
                ).all()]
                if exact_match:
                    project_ids = [p for p in project_ids if project_ids.count(p) == len(search_terms)]
                projects_query = (FabricProjects.id.in_(list(set(project_ids))))
            elif search_set == EnumSearchSetTypes.description.name:
                # description
                search_term = func.lower(search)
                if not exact_match:
                    projects_query = ((FabricProjects.name.ilike("%" + search + "%")) |
                                      (FabricProjects.description.ilike("%" + search + "%")) |
                                      (FabricProjects.uuid == search))
                else:
                    projects_query = ((func.lower(FabricProjects.name) == search_term) |
                                      (func.lower(FabricProjects.description) == search_term) |
                                      (func.lower(FabricProjects.uuid) == search_term))
            elif search_set == EnumSearchSetTypes.topics.name:
                # topics
                search_terms = [i.strip().replace(' ', '-') for i in str(search).casefold().split(',')]
                project_ids = [p.projects_id for p in ProjectsTopics.query.filter(
                    func.lower(ProjectsTopics.topic).in_(search_terms)
                ).all()]
                if exact_match:
                    project_ids = [p for p in project_ids if project_ids.count(p) == len(search_terms)]
                projects_query = (FabricProjects.id.in_(list(set(project_ids))))
            elif search_set == EnumSearchSetTypes.type.name:
                # types
                search_terms = [i.strip() for i in str(search).casefold().split(',')]
                valid_types = [e.name for e in EnumProjectTypes]
                for t in search_terms:
                    if t not in valid_types:
                        details = 'projects_get(): Invalid parameter for search_set = type, {0}'.format(t)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                projects_query = FabricProjects.project_type.in_(search_terms)
            else:
                # invalid search_set
                search_term = func.lower(search)
                projects_query = ((func.lower(FabricProjects.name) == search_term) |
                                  (func.lower(FabricProjects.description) == search_term) |
                                  (func.lower(FabricProjects.uuid) == search_term))
            try:
                # anonymous users only get active projects
                if is_anonymous:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        (FabricProjects.active.is_(True)) &
                        projects_query
                    ).order_by(_sort_order_query).paginate(page=_page, per_page=limit, error_out=False)
                # authenticated users get active / retired projects
                else:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        projects_query
                    ).order_by(_sort_order_query).paginate(page=_page, per_page=limit, error_out=False)
            except Exception as exc:
                details = 'Oops! something went wrong with projects_get(): {0}'.format(exc)
                consoleLogger.error(details)
                return cors_500(details=details)
        elif not search and person_uuid:
            base = '{0}/projects?person_uuid={1}&{2}'.format(_SERVER_URL, person_uuid, _sort_order_path)
            if api_user.uuid == person_uuid:
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in api_user.roles])
                ).order_by(_sort_order_query).paginate(
                    page=_page, per_page=limit, error_out=False)
            else:
                as_self = False
                if is_anonymous:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        FabricProjects.active.is_(True) &
                        FabricProjects.is_public.is_(True) &
                        FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles])
                    ).order_by(_sort_order_query).paginate(
                        page=_page, per_page=limit, error_out=False)
                else:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        FabricProjects.is_public.is_(True) &
                        FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles])
                    ).order_by(_sort_order_query).paginate(
                        page=_page, per_page=limit, error_out=False)
        else:
            base = '{0}/projects?search={1}&person_uuid={2}&{3}'.format(_SERVER_URL, search, person_uuid,
                                                                        _sort_order_path)
            if api_user.uuid == person_uuid:
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in api_user.roles]) &
                    ((FabricProjects.name.ilike("%" + search + "%")) |
                     (FabricProjects.description.ilike("%" + search + "%")) |
                     (FabricProjects.uuid.ilike("%" + search + "%")))
                ).order_by(_sort_order_query).paginate(
                    page=_page, per_page=limit, error_out=False)
            else:
                as_self = False
                if is_anonymous:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        FabricProjects.active.is_(True) &
                        FabricProjects.is_public.is_(True) &
                        FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles]) &
                        (FabricProjects.name.ilike("%" + search + "%") |
                         FabricProjects.description.ilike("%" + search + "%"))
                    ).order_by(_sort_order_query).paginate(
                        page=_page, per_page=limit, error_out=False)
                else:
                    results_page = FabricProjects.query.filter(
                        is_public_check &
                        FabricProjects.is_public.is_(True) &
                        FabricProjects.uuid.in_([r.name.rsplit('-', 1)[0] for r in fab_person.roles]) &
                        (FabricProjects.name.ilike("%" + search + "%") |
                         FabricProjects.description.ilike("%" + search + "%"))
                    ).order_by(_sort_order_query).paginate(
                        page=_page, per_page=limit, error_out=False)
        # set projects response
        response = Projects()
        response.results = []
        for item in results_page.items:
            project = Project()
            # set project attributes
            if not is_anonymous:
                project.active = bool(item.active)
                project.created = str(item.created)
                project.communities = [c.community for c in item.communities]
                project.description = item.description
                project.expires_on = str(item.expires_on)
                project.facility = item.facility
                project.is_public = item.is_public
                if as_self:
                    project.memberships = get_project_membership(fab_project=item, fab_person=api_user)
                else:
                    project.memberships = get_project_membership(fab_project=item, fab_person=fab_person)
                project.name = item.name
                project.retired_date = str(item.retired_date) if item.retired_date else None
                project.review_required = bool(item.review_required)
                project.project_type = item.project_type.name
                if api_user.is_facility_operator() or api_user.is_facility_viewer():
                    project.tags = get_project_tags(fab_project=item, fab_person=api_user)
                elif as_self and (
                        project.memberships.is_creator or project.memberships.is_member or project.memberships.is_owner):
                    project.tags = get_project_tags(fab_project=item, fab_person=api_user)
                else:
                    project.tags = []
                project.topics = [t.topic for t in item.topics]
                project.uuid = item.uuid
            else:
                # anonymous user project list
                project.active = bool(item.active)
                project.communities = [c.community for c in item.communities]
                project.description = item.description
                project.name = item.name
                project.project_type = item.project_type.name
                project.topics = [t.topic for t in item.topics]
                project.uuid = item.uuid
            # add project to results
            response.results.append(project)
        # set links
        response.links = Status200OkPaginatedLinks()
        _URL_OFFSET_LIMIT = '{0}offset={1}&limit={2}'
        response.links.first = _URL_OFFSET_LIMIT.format(base, 0, limit) if results_page.pages > 0 else None
        response.links.last = _URL_OFFSET_LIMIT.format(base, int((results_page.pages - 1) * limit),
                                                       limit) if results_page.pages > 0 else None
        response.links.next = _URL_OFFSET_LIMIT.format(base, int(offset + limit),
                                                       limit) if results_page.has_next else None
        response.links.prev = _URL_OFFSET_LIMIT.format(base, int(offset - limit),
                                                       limit) if results_page.has_prev else None
        # set offset, limit and size
        response.limit = limit
        response.offset = offset
        response.total = results_page.total
        response.size = len(response.results)
        response.type = 'projects'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with projects_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_post(body: ProjectsPost = None) -> ProjectsDetails:  # noqa: E501
    """Create new Project

    Create new Project # noqa: E501

    :param body: Create new Project
    :type body: dict | bytes

    :rtype: ProjectsDetails

    {
        "description": "string",
        "is_public": true,
        "name": "string",
        "project_members": [
            "string"
        ],
        "project_owners": [
            "string"
        ]
    }
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active or not api_user.is_project_lead():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PROJECT_LEADS')))
        # create Project
        fab_project = create_fabric_project_from_api(body=body, project_creator=api_user)
        # NOTE: projects must be reviewed by a facility-operator prior to becoming active (v1.8.1)
        fab_project.active = False
        db.session.commit()
        # add event project_create
        add_core_api_event(event=EnumEvents.project_create.name,
                           event_date=fab_project.created,
                           event_triggered_by=api_user.uuid,
                           event_type=EnumEventTypes.projects.name,
                           people_uuid=api_user.uuid,
                           project_is_public=fab_project.is_public,
                           project_uuid=fab_project.uuid
                           )
        # TODO: notification email project_create
        return projects_uuid_get(uuid=str(fab_project.uuid))
    except Exception as exc:
        details = 'Oops! something went wrong with projects_post(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Preference options

    List of Projects Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [tag for tag in PROJECTS_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            results = PROJECTS_PREFERENCES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Preferences.Get()')


@login_required
def projects_profile_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Profile Preference options

    List of Projects Profile Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [tag for tag in PROJECTS_PROFILE_PREFERENCES.search(search) if
                       search.casefold() in tag.casefold()]
        else:
            results = PROJECTS_PROFILE_PREFERENCES.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_PROFILE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_profile_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Profile.Preferences.Get()')


def projects_project_types_get(search=None):  # noqa: E501
    """List of Projects Type options

    List of Projects Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [e.name for e in EnumProjectTypes if search.casefold() in e.name]
        else:
            results = [e.name for e in EnumProjectTypes]
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = 'projects.project_types'
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_project_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with projects_project_types_get()')


@login_required
def projects_tags_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Projects Tags options

    List of Projects Tags options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [tag for tag in PROJECTS_TAGS.search(search) if search.casefold() in tag.casefold()]
        else:
            results = PROJECTS_TAGS.options
        response = ApiOptions()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PROJECTS_TAGS.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("projects_tags_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with Projects.Tags.Get()')


@login_required
def projects_uuid_communities_patch(uuid: str,
                                    body: ProjectsCommunitiesPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Projects Communities as Project creator/owner

    Update Projects Communities as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Communities as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_facility_viewer() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check for communities
        try:
            if len(body.communities) == 0:
                update_projects_communities(api_user=api_user, fab_project=fab_project, communities=body.communities)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, communities=[]')
            else:
                communities = body.communities
                for community in communities:
                    if community not in PROJECTS_COMMUNITIES.options:
                        details = "Attempting to add invalid community '{0}'".format(community)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                update_projects_communities(api_user=api_user, fab_project=fab_project, communities=body.communities)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, communities={1}'.format(
                    fab_project.uuid, [c.community for c in fab_project.communties]))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_communities_patch(): 'communities' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_communities_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_delete(uuid: str):  # noqa: E501
    """Delete Project as owner

    Delete Project as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not the creator/owner of the project".format(api_user.display_name))
        if os.getenv('CORE_API_DEPLOYMENT_TIER') in ['beta', 'production']:
            # retired - do not allow beta or production projects to be hard deleted
            now = datetime.now(timezone.utc)
            fab_project.active = False
            fab_project.expires_on = now if fab_project.expires_on > now else fab_project.expires_on
            fab_project.is_locked = True
            fab_project.modified = now
            fab_project.modified_by = api_user
            fab_project.retired_on = now
            fab_project.review_required = False
            db.session.commit()
            details = "Project: '{0}' has been successfully retired".format(fab_project.name)
            # add event project_retire
            add_core_api_event(event=EnumEvents.project_retire.name,
                               event_date=fab_project.retired_on,
                               event_triggered_by=api_user.uuid,
                               event_type=EnumEventTypes.projects.name,
                               people_uuid=api_user.uuid,
                               project_is_public=fab_project.is_public,
                               project_uuid=fab_project.uuid
                               )
            # TODO: notification email project_retire
        else:
            # deleted - alpha projects can be hard deleted
            # details = "Project: '{0}' has been successfully deleted".format(fab_project.name)
            # consoleLogger.error(details)
            # return cors_500(details=details)
            # delete Tags
            update_projects_tags(api_user=api_user, fab_project=fab_project, tags=[])
            # delete Preferences
            delete_projects_preferences(fab_project=fab_project)
            # delete Profile
            delete_profile_projects(api_user=api_user, fab_project=fab_project)
            # remove project_creators
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[],
                                      personnel_type='creators',
                                      operation='batch')
            # remove project_members
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[],
                                      personnel_type='members',
                                      operation='batch')
            # remove project_owners
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[], personnel_type='owners',
                                      operation='batch')
            # remove project_token_holders
            update_projects_token_holders(api_user=api_user, fab_project=fab_project, token_holders=[],
                                          operation='batch')
            # remove project_storage allocations
            for s in fab_project.project_storage:
                s.active = False
                fab_project.project_storage.remove(s)
                db.session.commit()
            # remove communities
            update_projects_communities(fab_project=fab_project, communities=[])
            # remove project funding
            update_projects_project_funding(fab_project=fab_project, project_funding=[])
            # delete COUs -pc, -pm, -po, -tk
            delete_comanage_group(co_cou_id=fab_project.co_cou_id_pc)
            delete_comanage_group(co_cou_id=fab_project.co_cou_id_pm)
            delete_comanage_group(co_cou_id=fab_project.co_cou_id_po)
            delete_comanage_group(co_cou_id=fab_project.co_cou_id_tk)
            # delete FabricProject
            details = "Project: '{0}' has been successfully deleted".format(fab_project.name)
            consoleLogger.info(details)
            db.session.delete(fab_project)
            db.session.commit()
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = details
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        # metrics log - Project was deleted:
        # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef delete by usr:dead-beef-dead-beef
        log_msg = 'Project event prj:{0} delete by usr:{1}'.format(
            str(fab_project.uuid),
            str(api_user.uuid))
        metricsLogger.info(log_msg)
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_delete(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_expires_on_patch(uuid: str,
                                   body: ProjectsExpiresOnPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Project expires on date as Facility Operator

    Update Project expires on date as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project expires on date as Facility Operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active facility-operators role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # check for expires_on
        try:
            # validate expires_on
            try:
                expires_on = normalize_date_to_utc(date_str=body.expires_on)
            except ValueError as exc:
                details = 'Exception: expires_on: {0}'.format(exc)
                consoleLogger.error(details)
                return cors_400(details=details)
            # update project expires_on and set is_locked
            fab_project.expires_on = expires_on
            if expires_on < datetime.now(timezone.utc):
                fab_project.is_locked = True
            else:
                fab_project.is_locked = False
            db.session.commit()
            # metrics log - Project expires_on was modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify expires_on by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify \'expires_on={1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                str(fab_project.expires_on),
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_expires_on_patch(): 'expires_on' - {0}".format(exc))
        # update project active status
        projects_set_active(fab_project=fab_project)
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_expires_on_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_project_funding_patch(uuid: str, body: ProjectsFundingPatchProjectFunding = None):  # noqa: E501
    """Update Project Funding as Project creator/owner

    Update Project Funding as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Funding Source as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check for project funding
        try:
            if len(body.project_funding) == 0:
                update_projects_project_funding(api_user=api_user, fab_project=fab_project,
                                                project_funding=body.project_funding)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, project_funding=[]'.format(fab_project.uuid))
            else:
                project_funding = body.project_funding
                for fs in project_funding:
                    # agency must be from the pre-defined list
                    if fs.agency not in PROJECTS_FUNDING_AGENCIES.options:
                        details = "Attempting to add invalid funding agency '{0}'".format(fs.agency)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                    # agency_other can only be used when agency = Other
                    if fs.agency_other and str(fs.agency).casefold() != "other":
                        details = "Attempting to add invalid funding agency for Other '{0}'".format(fs.agency)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                update_projects_project_funding(api_user=api_user, fab_project=fab_project,
                                                project_funding=body.project_funding)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, project_funding={1}'.format(
                    fab_project.uuid, [fs.agency for fs in fab_project.project_funding]))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_project_funding_patch(): 'project_funding' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_project_funding_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


# @login_or_token_required
def projects_uuid_get(uuid: str) -> ProjectsDetails:  # noqa: E501
    """Project details by UUID

    Project details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: ProjectsDetails
    """
    # TODO: active, retired_date, review_required
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # establish if call is anonymous
        if not id_source:
            is_anonymous = True
        else:
            is_anonymous = False
        # check api_user active flag
        if not is_anonymous and not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # update active status as needed
        projects_set_active(fab_project=fab_project)
        # set ProjectsOne object
        project_one = ProjectsOne()
        if not is_anonymous:
            # set required attributes for any uuid
            project_one.active = bool(fab_project.active)
            project_one.communities = [c.community for c in fab_project.communities]
            project_one.created = str(fab_project.created)
            project_one.description = fab_project.description
            project_one.expires_on = str(fab_project.expires_on)
            project_one.fabric_matrix = get_fabric_matrix(project_id=fab_project.id)
            project_one.facility = fab_project.facility
            project_one.is_locked = fab_project.is_locked
            project_one.is_public = fab_project.is_public
            project_one.memberships = get_project_membership(fab_project=fab_project, fab_person=api_user)
            project_one.name = fab_project.name
            project_one.project_funding = [
                {"agency": pf.agency, "agency_other": pf.agency_other, "award_amount": pf.award_amount,
                 "award_number": pf.award_number, "directorate": pf.directorate}
                for pf in fab_project.project_funding]
            project_one.project_type = fab_project.project_type.name
            project_one.retired_date = str(fab_project.retired_date) if fab_project.retired_date else None
            project_one.review_required = bool(fab_project.review_required)
            project_one.topics = [t.topic for t in fab_project.topics]
            project_one.uuid = fab_project.uuid
            # set remaining attributes for project_creators, project_owners and project_members
            if project_one.memberships.is_creator or project_one.memberships.is_owner or project_one.memberships.is_member \
                    or api_user.is_facility_operator() or api_user.is_facility_viewer():
                project_one.active = fab_project.active
                project_one.modified = str(fab_project.modified)
                project_one.preferences = {p.key: p.value for p in fab_project.preferences}
                project_one.profile = get_profile_projects(
                    profile_projects_id=fab_project.profile.id,
                    as_owner=(project_one.memberships.is_creator or project_one.memberships.is_owner))
                project_one.project_creators = get_projects_personnel(fab_project=fab_project,
                                                                      personnel_type='creators')
                project_one.project_members = get_projects_personnel(fab_project=fab_project, personnel_type='members')
                project_one.project_owners = get_projects_personnel(fab_project=fab_project, personnel_type='owners')
                project_one.project_storage = get_projects_storage(fab_project=fab_project)
                project_one.quotas = get_projects_quotas(fab_project=fab_project)
                project_one.tags = [t.tag for t in fab_project.tags]
                project_one.token_holders = get_projects_personnel(fab_project=fab_project, personnel_type='tokens')
            # set remaining attributes for everyone else
            else:
                if not fab_project.is_public:
                    return cors_403(
                        details="User: '{0}' does not have access to this private project".format(
                            api_user.display_name))
                project_prefs = {p.key: p.value for p in fab_project.preferences}
                project_one.active = fab_project.active
                project_one.modified = str(fab_project.modified)
                project_one.profile = get_profile_projects(
                    profile_projects_id=fab_project.profile.id,
                    as_owner=(
                            project_one.memberships.is_creator or project_one.memberships.is_owner)) if project_prefs.get(
                    'show_profile') else None
                project_one.project_creators = get_projects_personnel(fab_project=fab_project,
                                                                      personnel_type='creators')
                project_one.project_members = get_projects_personnel(fab_project=fab_project,
                                                                     personnel_type='members') if project_prefs.get(
                    'show_project_members') else None
                project_one.project_owners = get_projects_personnel(fab_project=fab_project,
                                                                    personnel_type='owners') if project_prefs.get(
                    'show_project_owners') else None
                project_one.tags = []
        else:
            # anonymous user project details
            project_one.active = bool(fab_project.active)
            project_one.communities = [c.community for c in fab_project.communities]
            project_one.description = fab_project.description
            project_one.fabric_matrix = get_fabric_matrix(project_id=fab_project.id)
            project_one.is_public = fab_project.is_public
            project_one.name = fab_project.name
            project_one.project_funding = [
                {"agency": pf.agency, "agency_other": pf.agency_other, "award_amount": pf.award_amount,
                 "award_number": pf.award_number, "directorate": pf.directorate}
                for pf in fab_project.project_funding]
            project_one.project_type = fab_project.project_type.name
            project_one.uuid = fab_project.uuid
        # set project_details response
        response = ProjectsDetails()
        response.results = [project_one]
        response.size = len(response.results)
        response.status = 200
        response.type = 'projects.details'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_patch(uuid: str = None, body: ProjectsPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Project details as owner

    Update Project details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    # TODO: verify logic
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check for description
        try:
            if len(body.description) != 0:
                fab_project.description = body.description
                db.session.commit()
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, description={1}'.format(
                    fab_project.uuid, fab_project.description))
                # metrics log - Project description modified:
                # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify description DESC by usr:dead-beef-dead-beef
                log_msg = 'Project event prj:{0} modify description \'{1}\' by usr:{2}'.format(
                    str(fab_project.uuid),
                    fab_project.description,
                    str(api_user.uuid))
                metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_patch(): 'description' - {0}".format(exc))
        # check for is_public
        try:
            if body.is_public is not None:
                if body.is_public:
                    fab_project.is_public = True
                if not body.is_public:
                    fab_project.is_public = False
                db.session.commit()
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, is_public={1}'.format(
                    fab_project.uuid, fab_project.is_public))
                # metrics log - Project is_public modified:
                # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify is_public BOOL by usr:dead-beef-dead-beef
                log_msg = 'Project event prj:{0} modify is_public {1} by usr:{2}'.format(
                    str(fab_project.uuid),
                    str(fab_project.is_public),
                    str(api_user.uuid))
                metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_patch(): 'is_public' - {0}".format(exc))
        # check for name
        try:
            if len(body.name) != 0:
                is_pc_name = update_comanage_group(co_cou_id=fab_project.co_cou_id_pc, description=body.name)
                is_pm_name = update_comanage_group(co_cou_id=fab_project.co_cou_id_pm, description=body.name)
                is_po_name = update_comanage_group(co_cou_id=fab_project.co_cou_id_po, description=body.name)
                is_tk_name = update_comanage_group(co_cou_id=fab_project.co_cou_id_tk, description=body.name)
                if is_pc_name and is_pm_name and is_po_name and is_tk_name:
                    fab_project.name = body.name
                    db.session.commit()
                    consoleLogger.info(
                        'UPDATE: FabricProjects: uuid={0}, name={1}'.format(fab_project.uuid, fab_project.name))
                    # metrics log - Project name modified:
                    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify name NAME by usr:dead-beef-dead-beef
                    log_msg = 'Project event prj:{0} modify name \'{1}\' by usr:{2}'.format(
                        str(fab_project.uuid),
                        fab_project.name,
                        str(api_user.uuid))
                    metricsLogger.info(log_msg)
                else:
                    consoleLogger.error(
                        'ERROR: FabricProjects: uuid={0}, name={1}'.format(fab_project.uuid, fab_project.name))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_patch(): 'name' - {0}".format(exc))
        # check for preferences
        try:
            for key in body.preferences.keys():
                fab_pref = FabricPreferences.query.filter(
                    FabricPreferences.key == key,
                    FabricPreferences.projects_id == fab_project.id,
                    FabricPreferences.type == EnumPreferenceTypes.projects
                ).one_or_none()
                if not fab_pref:
                    if key in PROJECTS_PREFERENCES.options:
                        fab_pref = FabricPreferences()
                        fab_pref.key = key
                        fab_pref.value = body.preferences.get(key)
                        fab_pref.type = EnumPreferenceTypes.projects
                        fab_pref.projects_id = fab_project.id
                        db.session.add(fab_pref)
                        db.session.commit()
                        fab_project.preferences.append(fab_pref)
                        consoleLogger.info("CREATE: FabricProjects: uuid={0}, 'preferences.{1}' = {2}".format(
                            fab_project.uuid, fab_pref.key, fab_pref.value))
                    else:
                        details = "Projects Preferences: '{0}' is not a valid preference type".format(key)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                else:
                    fab_pref.value = body.preferences.get(key)
                    db.session.commit()
                    consoleLogger.info("UPDATE: FabricProjects: uuid={0}, 'preferences.{1}' = {2}".format(
                        fab_project.uuid, fab_pref.key, fab_pref.value))
                    # metrics log - Project preference modified:
                    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify PREF BOOL by usr:dead-beef-dead-beef
                    log_msg = 'Project event prj:{0} modify {1} {2} by usr:{3}'.format(
                        str(fab_project.uuid),
                        fab_pref.key,
                        str(fab_pref.value),
                        str(api_user.uuid))
                    metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_patch(): 'preferences' - {0}".format(exc))
        # check for project type
        try:
            if len(body.project_type) != 0:
                if body.project_type in [EnumProjectTypes.maintenance.name,
                                         EnumProjectTypes.industry.name] and not api_user.is_facility_operator():
                    details = 'Invalid project type: {0}, must be set by facility-operator'.format(body.project_type)
                    consoleLogger.error(details)
                    return cors_400(details=details)
                else:
                    fab_project.project_type = body.project_type
                    db.session.commit()
                    consoleLogger.info('UPDATE: FabricProjects: uuid={0}, description={1}'.format(
                        fab_project.uuid, fab_project.description))
                    # metrics log - Project description modified:
                    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify description DESC by usr:dead-beef-dead-beef
                    log_msg = 'Project event prj:{0} modify description \'{1}\' by usr:{2}'.format(
                        str(fab_project.uuid),
                        fab_project.description,
                        str(api_user.uuid))
                    metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_patch(): 'project_type' - {0}".format(exc))
        # update active status as needed
        projects_set_active(fab_project=fab_project)

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_personnel_patch(uuid: str = None,
                                  body: ProjectsPersonnelPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Project personnel as owner

    Update Project personnel as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project personnel as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for project_members
        try:
            if len(body.project_members) == 0:
                body.project_members = []
            # add project_members
            fab_project.is_locked = True
            db.session.commit()
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=body.project_members,
                                      personnel_type='members', operation='batch')
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_personnel_patch(): 'project_members' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # check for project_owners
        try:
            if len(body.project_owners) == 0:
                body.project_owners = []
            # add project_owners
            fab_project.is_locked = True
            db.session.commit()
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=body.project_owners,
                                      personnel_type='owners', operation='batch')
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_personnel_patch(): 'project_owners' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_personnel_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_profile_patch(uuid: str, body: ProfileProjects = None):  # noqa: E501
    """Update Project Profile details as owner

    Update Project Profile details as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Profile details as owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        fab_profile = FabricProfilesProjects.query.filter_by(id=fab_project.profile.id).one_or_none()
        # check for award_information
        try:
            if len(body.award_information) == 0:
                fab_profile.award_information = None
            else:
                fab_profile.award_information = body.award_information
            db.session.commit()
            consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, award_information={1}'.format(
                fab_profile.uuid, fab_profile.award_information))
            # metrics log - Project award_information modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify award_information INFO by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify award_information \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                fab_profile.award_information,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'award_information' - {0}".format(exc))
        # check for goals
        try:
            if len(body.goals) == 0:
                fab_profile.goals = None
            else:
                fab_profile.goals = body.goals
            db.session.commit()
            consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, goals={1}'.format(
                fab_profile.uuid, fab_profile.goals))
            # metrics log - Project goals modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify goals GOALS by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify goals \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                fab_profile.goals,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'goals' - {0}".format(exc))
        # check for keywords
        try:
            if len(body.keywords) == 0:
                update_profiles_projects_keywords(api_user=api_user, fab_project=fab_project, fab_profile=fab_profile,
                                                  keywords=body.keywords)
                consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, keywords=[]')
            else:
                update_profiles_projects_keywords(api_user=api_user, fab_project=fab_project, fab_profile=fab_profile,
                                                  keywords=body.keywords)
                consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, keywords={1}'.format(
                    fab_project.uuid, [k.keyword for k in fab_profile.keywords]))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'keywords' - {0}".format(exc))
        # check for notebooks
        # TODO - define notebooks
        # check for preferences
        try:
            for key in body.preferences.keys():
                fab_pref = FabricPreferences.query.filter(
                    FabricPreferences.key == key,
                    FabricPreferences.profiles_projects_id == fab_profile.id,
                    FabricPreferences.type == EnumPreferenceTypes.profiles_projects
                ).one_or_none()
                if not fab_pref:
                    if key in PROJECTS_PROFILE_PREFERENCES.options:
                        fab_pref = FabricPreferences()
                        fab_pref.key = key
                        fab_pref.value = body.preferences.get(key)
                        fab_pref.type = EnumPreferenceTypes.profiles_projects
                        fab_pref.profiles_projects_id = fab_profile.id
                        db.session.add(fab_pref)
                        db.session.commit()
                        fab_profile.preferences.append(fab_pref)
                        consoleLogger.info("CREATE: FabricProfilesProjects: uuid={0}, 'preferences.{1}' = '{2}'".format(
                            fab_project.uuid, fab_pref.key, fab_pref.value))
                    else:
                        details = "Projects Preferences: '{0}' is not a valid preference type".format(key)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                else:
                    fab_pref.value = body.preferences.get(key)
                    db.session.commit()
                    consoleLogger.info("UPDATE: FabricProfilesProjects: uuid={0}, 'preferences.{1}' = '{2}'".format(
                        fab_project.uuid, fab_pref.key, fab_pref.value))
                    # metrics log - Project preference modified:
                    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify PREF BOOL by usr:dead-beef-dead-beef
                    log_msg = 'Project event prj:{0} modify {1} {2} by usr:{3}'.format(
                        str(fab_project.uuid),
                        fab_pref.key,
                        str(fab_pref.value),
                        str(api_user.uuid))
                    metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'preferences' - {0}".format(exc))
        # check for project_status
        try:
            if len(body.project_status) == 0:
                fab_profile.project_status = None
            else:
                fab_profile.project_status = body.project_status
            db.session.commit()
            consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, project_status={1}'.format(
                fab_profile.uuid, fab_profile.project_status))
            # metrics log - Project project_status modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify project_status STATUS by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify project_status \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                fab_profile.project_status,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'project_status' - {0}".format(exc))
        # check for purpose
        try:
            if len(body.purpose) == 0:
                fab_profile.purpose = None
            else:
                fab_profile.purpose = body.purpose
            db.session.commit()
            consoleLogger.info('UPDATE: FabricProfilesProjects: uuid={0}, purpose={1}'.format(
                fab_profile.uuid, fab_profile.purpose))
            # metrics log - Project purpose modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify purpose PURPOSE by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify purpose \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                fab_profile.purpose,
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'purpose' - {0}".format(exc))
        # check for references
        try:
            for ref in body.references:
                if not is_valid_url(ref.url):
                    details = "References: '{0}' is not a valid URL type".format(ref.url)
                    consoleLogger.error(details)
                    return cors_400(details=details)
            update_profiles_projects_references(api_user=api_user, fab_project=fab_project,
                                                fab_profile=fab_project.profile,
                                                references=body.references)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_profile_patch(): 'references' - {0}".format(exc))

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Profile for Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_profile_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_project_creators_patch(operation: str = None, uuid: str = None,
                                         body: ProjectsCreatorsPatch = None) -> Status200OkNoContent:  # noqa: E501
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
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project creator or facility operator
        if not api_user.active or not (
                api_user.is_facility_operator() or api_user.is_project_creator(project_uuid=str(fab_project.uuid))):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not a project creator".format(
                    api_user.display_name))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for project_creators
        try:
            if len(body.project_creators) == 0:
                body.project_creators = []
            # add project_creators
            fab_project.is_locked = True
            db.session.commit()
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=body.project_creators,
                                      personnel_type='creators', operation=operation)
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_project_creators_patch(): 'project_creators' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_project_creators_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_project_members_patch(operation: str = None, uuid: str = None,
                                        body: ProjectsMembersPatch = None) -> Status200OkNoContent:  # noqa: E501
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
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project creator/owner or facility operator
        if not api_user.active or not (api_user.is_facility_operator() or api_user.is_project_creator(
                project_uuid=str(fab_project.uuid)) or api_user.is_project_owner(project_uuid=str(fab_project.uuid))):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not a project creator/owner".format(
                    api_user.display_name))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for project_members
        try:
            if len(body.project_members) == 0:
                body.project_members = []
            # add project_members
            fab_project.is_locked = True
            db.session.commit()
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=body.project_members,
                                      personnel_type='members', operation=operation)
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_project_members_patch(): 'project_members' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_project_members_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_project_owners_patch(operation: str = None, uuid: str = None,
                                       body: ProjectsOwnersPatch = None) -> Status200OkNoContent:  # noqa: E501
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
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project creator/owner or facility operator
        if not api_user.active or not (api_user.is_facility_operator() or api_user.is_project_creator(
                project_uuid=str(fab_project.uuid)) or api_user.is_project_owner(project_uuid=str(fab_project.uuid))):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not a project creator/owner".format(
                    api_user.display_name))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for project_owners
        try:
            if len(body.project_owners) == 0:
                body.project_owners = []
            # add project_owners
            fab_project.is_locked = True
            db.session.commit()
            update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=body.project_owners,
                                      personnel_type='owners', operation=operation)
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_project_owners_patch(): 'project_owners' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_project_owners_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def projects_uuid_review_required_patch(uuid, body=None):  # noqa: E501
    """Update Project review status as Facility Operator

    Update Project review status as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project review as Facility Operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active facility-operators role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # check for review_required
        try:
            # validate review_required
            invalid = False
            try:
                review_required = str(body.review_required)
                if review_required.casefold() not in ['true', 'false']:
                    invalid = True
            except ValueError as exc:
                details = 'Exception: review_required: {0}'.format(exc)
                consoleLogger.error(details)
                invalid = True
            if invalid:
                return cors_400(details='BooleanRequired: must be true or false, not {0}'.format(review_required))
            # update project review_required
            fab_project.review_required = bool(body.review_required)
            db.session.commit()
            # metrics log - Project expires_on was modified:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify expires_on by usr:dead-beef-dead-beef
            log_msg = 'Project event prj:{0} modify \'expires_on={1}\' by usr:{2}'.format(
                str(fab_project.uuid),
                str(fab_project.expires_on),
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_expires_on_patch(): 'expires_on' - {0}".format(exc))
        # update project active status
        projects_set_active(fab_project=fab_project)
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_expires_on_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_tags_patch(uuid: str, body: ProjectsTagsPatch = None) -> Status200OkNoContent:  # noqa: E501
    """Update Projects Tags as Facility Operator

    Update Projects Tags as Facility Operator # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Tags as Facility Operator
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active facility-operators role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for tags
        try:
            if len(body.tags) == 0:
                update_projects_tags(api_user=api_user, fab_project=fab_project, tags=body.tags)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, tags=[]')
            else:
                tags = body.tags
                for tag in tags:
                    if tag not in PROJECTS_TAGS.options:
                        details = "Attempting to add invalid tag '{0}'".format(tag)
                        consoleLogger.error(details)
                        return cors_400(details=details)
                update_projects_tags(api_user=api_user, fab_project=fab_project, tags=body.tags)
                consoleLogger.info('UPDATE: FabricProjects: uuid={0}, tags={1}'.format(
                    fab_project.uuid, [t.tag for t in fab_project.tags]))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_tags_patch(): 'tags' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def projects_uuid_token_holders_patch(operation: str = None, uuid: str = None,
                                      body: ProjectsTokenHoldersPatch = None) -> Status200OkNoContent:  # noqa: E501
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
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active facility-operator
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not a facility operator".format(
                    api_user.display_name))
        # ensure all users are valid project creators/members/owners
        for p_uuid in body.token_holders:
            if not FabricPeople.query.filter_by(uuid=p_uuid).one_or_none():
                return cors_404(details="No match for People with uuid = '{0}'".format(p_uuid))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # check for token_holders
        try:
            if len(body.token_holders) == 0:
                body.token_holders = []
            # add project_members
            fab_project.is_locked = True
            db.session.commit()
            update_projects_token_holders(api_user=api_user, fab_project=fab_project, token_holders=body.token_holders,
                                          operation=operation)
            fab_project.is_locked = False
            db.session.commit()
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_token_holders_patch(): 'token_holders' - {0}".format(exc))
            fab_project.is_locked = False
            db.session.commit()

        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_token_holders_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def projects_uuid_topics_patch(uuid: str,
                               body: ProjectsTopicsPatch = None) -> Status200OkNoContent:  # noqa: E501
    """
    NOTE: spaces between words in a single topic are replaced with dashes: " " --> "-"
    Update Project Topics as Project creator/owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Project Topics as Project creator/owner
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user, id_source = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # check if the project is locked or has exceeded expiry date
        if fab_project.is_locked or fab_project.expires_on < datetime.now(timezone.utc):
            return cors_423(
                details="Locked project, uuid = '{0}', expires_on = '{1}'".format(str(fab_project.uuid),
                                                                                  str(fab_project.expires_on)))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not an owner of the project".format(
                    api_user.display_name))
        # check for topics
        try:
            topics = [str(t.replace(" ", "-")).casefold() for t in body.topics]
            update_projects_topics(api_user=api_user, fab_project=fab_project,
                                   topics=topics)
            consoleLogger.info('UPDATE: FabricProjects: uuid={0}, topics={1}'.format(
                fab_project.uuid, [c.topic for c in fab_project.topics]))
        except Exception as exc:
            consoleLogger.info("NOP: projects_uuid_topics_patch(): 'communities' - {0}".format(exc))
        # create response
        patch_info = Status200OkNoContentResults()
        patch_info.details = "Project: '{0}' has been successfully updated".format(fab_project.name)
        response = Status200OkNoContent()
        response.results = [patch_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)

    except Exception as exc:
        details = 'Oops! something went wrong with projects_uuid_topics_patch(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)
