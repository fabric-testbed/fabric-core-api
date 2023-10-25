import os
from datetime import datetime, timezone

from sqlalchemy import func

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.preferences import EnumPreferenceTypes, FabricPreferences
from swagger_server.database.models.profiles import FabricProfilesProjects
from swagger_server.database.models.projects import FabricProjects
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.profile_projects import ProfileProjects
from swagger_server.models.projects import Project, Projects  # noqa: E501
from swagger_server.models.projects_creators_patch import ProjectsCreatorsPatch
from swagger_server.models.projects_details import ProjectsDetails, ProjectsOne  # noqa: E501
from swagger_server.models.projects_expires_on_patch import ProjectsExpiresOnPatch
from swagger_server.models.projects_members_patch import ProjectsMembersPatch
from swagger_server.models.projects_owners_patch import ProjectsOwnersPatch
from swagger_server.models.projects_patch import ProjectsPatch
from swagger_server.models.projects_personnel_patch import ProjectsPersonnelPatch
from swagger_server.models.projects_post import ProjectsPost
from swagger_server.models.projects_tags_patch import ProjectsTagsPatch
from swagger_server.models.projects_token_holders_patch import ProjectsTokenHoldersPatch
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.models.status200_ok_paginated import Status200OkPaginatedLinks
from swagger_server.response_code import PROJECTS_PREFERENCES, PROJECTS_PROFILE_PREFERENCES, PROJECTS_TAGS
from swagger_server.response_code.comanage_utils import delete_comanage_group, update_comanage_group
from swagger_server.response_code.core_api_utils import normalize_date_to_utc
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_423, cors_500
from swagger_server.response_code.decorators import login_or_token_required, login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.preferences_utils import delete_projects_preferences
from swagger_server.response_code.profiles_utils import delete_profile_projects, get_profile_projects, \
    update_profiles_projects_keywords, update_profiles_projects_references
from swagger_server.response_code.projects_utils import create_fabric_project_from_api, get_project_membership, \
    get_project_tags, get_projects_personnel, get_projects_storage, update_projects_personnel, update_projects_tags, \
    update_projects_token_holders
from swagger_server.response_code.response_utils import is_valid_url

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


@login_or_token_required
def projects_get(search=None, exact_match=None, offset=None, limit=None, person_uuid=None, sort_by=None,
                 order_by=None) -> Projects:  # noqa: E501
    """Search for FABRIC Projects

    Search for FABRIC Projects by name # noqa: E501

    :param search: search term applied
    :type search: str
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
        # set sort_by and order_by
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
        # get paginated results
        is_public_check = (
                FabricProjects.is_public.is_(True) |
                FabricProjects.project_creators.any(FabricPeople.id == api_user.id) |
                FabricProjects.project_owners.any(FabricPeople.id == api_user.id) |
                FabricProjects.project_members.any(FabricPeople.id == api_user.id) |
                api_user.is_facility_operator()
        )
        if not search and not person_uuid:
            base = '{0}/projects?{1}'.format(_SERVER_URL, _sort_order_path)
            results_page = FabricProjects.query.filter(
                is_public_check &
                FabricProjects.active.is_(True)
            ).order_by(_sort_order_query).paginate(
                page=_page, per_page=limit, error_out=False)
        elif search and not person_uuid:
            base = '{0}/projects?search={1}&{2}'.format(_SERVER_URL, search, _sort_order_path)
            if exact_match:
                search_term = func.lower(search)
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    (FabricProjects.active.is_(True)) &
                    ((func.lower(FabricProjects.name) == search_term) |
                     (func.lower(FabricProjects.description) == search_term) |
                     (func.lower(FabricProjects.uuid) == search_term))
                ).order_by(_sort_order_query).paginate(page=_page, per_page=limit, error_out=False)
            else:
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    (FabricProjects.active.is_(True)) &
                    ((FabricProjects.name.ilike("%" + search + "%")) |
                     (FabricProjects.description.ilike("%" + search + "%")) |
                     (FabricProjects.uuid == search))
                ).order_by(_sort_order_query).paginate(page=_page, per_page=limit, error_out=False)
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
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    FabricProjects.active.is_(True) &
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
                results_page = FabricProjects.query.filter(
                    is_public_check &
                    FabricProjects.active.is_(True) &
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
            project.created = str(item.created)
            project.description = item.description
            project.facility = item.facility
            project.is_public = item.is_public
            if as_self:
                project.memberships = get_project_membership(fab_project=item, fab_person=api_user)
            else:
                project.memberships = get_project_membership(fab_project=item, fab_person=fab_person)
            project.name = item.name
            if api_user.is_facility_operator():
                project.tags = get_project_tags(fab_project=item, fab_person=api_user)
            elif as_self and (
                    project.memberships.is_creator or project.memberships.is_member or project.memberships.is_owner):
                project.tags = get_project_tags(fab_project=item, fab_person=api_user)
            else:
                project.tags = []
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
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active or not api_user.is_project_lead():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PROJECT_LEADS')))
        # create Project
        fab_project = create_fabric_project_from_api(body=body, project_creator=api_user)
        fab_project.active = True
        db.session.commit()
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
def projects_uuid_delete(uuid: str):  # noqa: E501
    """Delete Project as owner

    Delete Project as owner # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # verify active project_creator, project_owner or facility-operator
        if not api_user.active or not api_user.is_facility_operator() and \
                not api_user.is_project_creator(str(fab_project.uuid)) and \
                not api_user.is_project_owner(str(fab_project.uuid)):
            return cors_403(
                details="User: '{0}' is not the creator of the project".format(api_user.display_name))
        # delete Tags
        update_projects_tags(api_user=api_user, fab_project=fab_project, tags=[])
        # delete Preferences
        delete_projects_preferences(fab_project=fab_project)
        # delete Profile
        delete_profile_projects(api_user=api_user, fab_project=fab_project)
        # remove project_creators
        update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[], personnel_type='creators',
                                  operation='batch')
        # remove project_members
        update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[], personnel_type='members',
                                  operation='batch')
        # remove project_owners
        update_projects_personnel(api_user=api_user, fab_project=fab_project, personnel=[], personnel_type='owners',
                                  operation='batch')
        # remove project_storage allocations
        for s in fab_project.project_storage:
            s.active = False
            fab_project.project_storage.remove(s)
            db.session.commit()
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
        api_user = get_person_by_login_claims()
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


@login_or_token_required
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
        # get project by uuid
        fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
        if not fab_project:
            return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
        # check if the project has exceeded expiry date
        if fab_project.expires_on < datetime.now(timezone.utc):
            fab_project.is_locked = True
            db.session.commit()
        # set ProjectsOne object
        project_one = ProjectsOne()
        # set required attributes for any uuid
        project_one.created = str(fab_project.created)
        project_one.description = fab_project.description
        project_one.expires_on = str(fab_project.expires_on)
        project_one.facility = fab_project.facility
        project_one.is_locked = fab_project.is_locked
        project_one.is_public = fab_project.is_public
        project_one.memberships = get_project_membership(fab_project=fab_project, fab_person=api_user)
        project_one.name = fab_project.name
        project_one.uuid = fab_project.uuid
        # set remaining attributes for project_creators, project_owners and project_members
        if project_one.memberships.is_creator or project_one.memberships.is_owner or project_one.memberships.is_member \
                or api_user.is_facility_operator():
            project_one.active = fab_project.active
            project_one.modified = str(fab_project.modified)
            project_one.preferences = {p.key: p.value for p in fab_project.preferences}
            project_one.profile = get_profile_projects(
                profile_projects_id=fab_project.profile.id,
                as_owner=(project_one.memberships.is_creator or project_one.memberships.is_owner))
            project_one.project_creators = get_projects_personnel(fab_project=fab_project, personnel_type='creators')
            project_one.project_members = get_projects_personnel(fab_project=fab_project, personnel_type='members')
            project_one.project_owners = get_projects_personnel(fab_project=fab_project, personnel_type='owners')
            project_one.project_storage = get_projects_storage(fab_project=fab_project)
            project_one.tags = [t.tag for t in fab_project.tags]
            project_one.token_holders = get_projects_personnel(fab_project=fab_project, personnel_type='tokens')
        # set remaining attributes for everyone else
        else:
            if not fab_project.is_public:
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
                                                                  personnel_type='creators')
            project_one.project_members = get_projects_personnel(fab_project=fab_project,
                                                                 personnel_type='members') if project_prefs.get(
                'show_project_members') else None
            project_one.project_owners = get_projects_personnel(fab_project=fab_project,
                                                                personnel_type='owners') if project_prefs.get(
                'show_project_owners') else None
            project_one.tags = []
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
    try:
        # get api_user
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
        api_user = get_person_by_login_claims()
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
