import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricGroups, FabricPeople, FabricRoles
from swagger_server.database.models.projects import FabricProjects, ProjectsCommunities, ProjectsFunding, \
    ProjectsTags
from swagger_server.models.person import Person
from swagger_server.models.project_membership import ProjectMembership
from swagger_server.models.projects_post import ProjectsPost
from swagger_server.models.storage_one import StorageOne
from swagger_server.response_code.comanage_utils import create_comanage_group, create_comanage_role, \
    delete_comanage_role
from swagger_server.response_code.preferences_utils import create_projects_preferences
from swagger_server.response_code.profiles_utils import create_profile_projects
from swagger_server.response_code.response_utils import array_difference


def project_funding_to_array(n):
    return [{'agency': x.agency, 'award_amount': x.award_amount,
             'award_number': x.award_number, 'directorate': x.directorate} for x in n]


def create_fabric_project_from_api(body: ProjectsPost, project_creator: FabricPeople) -> FabricProjects:
    """
    * Denotes required fields
    - *active
    - co_cou_id_pc
    - co_cou_id_pm
    - co_cou_id_po
    - *description
    - *facility
    - *is_public
    - *name
    - preferences
    - profile
    - project_creators
    - project_members
    - project_owners
    - tags
    - *uuid

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
    # create Project
    now = datetime.now(timezone.utc)
    fab_project = FabricProjects()
    fab_project.active = False
    fab_project.created = now
    fab_project.created_by_uuid = str(project_creator.uuid)
    fab_project.description = body.description
    fab_project.expires_on = now + timedelta(days=float(os.getenv('PROJECTS_RENEWAL_PERIOD_IN_DAYS')))
    fab_project.facility = os.getenv('CORE_API_DEFAULT_FACILITY')
    fab_project.is_locked = False
    fab_project.is_public = body.is_public
    fab_project.modified = now
    fab_project.modified_by_uuid = str(project_creator.uuid)
    fab_project.name = body.name
    fab_project.uuid = uuid4()
    db.session.add(fab_project)
    db.session.commit()
    # create COU groups
    # COU project creators
    fab_project.co_cou_id_pc = create_comanage_group(
        name=str(fab_project.uuid) + '-pc', description=fab_project.name,
        parent_cou_id=int(os.getenv('COU_ID_PROJECTS')))
    # COU project members
    fab_project.co_cou_id_pm = create_comanage_group(
        name=str(fab_project.uuid) + '-pm', description=fab_project.name,
        parent_cou_id=int(os.getenv('COU_ID_PROJECTS')))
    # COU project creators
    fab_project.co_cou_id_po = create_comanage_group(
        name=str(fab_project.uuid) + '-po', description=fab_project.name,
        parent_cou_id=int(os.getenv('COU_ID_PROJECTS')))
    # COU project token holders
    fab_project.co_cou_id_tk = create_comanage_group(
        name=str(fab_project.uuid) + '-tk', description=fab_project.name,
        parent_cou_id=int(os.getenv('COU_ID_PROJECTS')))
    db.session.commit()
    # create preferences
    create_projects_preferences(fab_project=fab_project)
    # create profile
    create_profile_projects(fab_project=fab_project)
    # add project_creators
    update_projects_personnel(api_user=project_creator, fab_project=fab_project,
                              personnel=[fab_project.created_by_uuid],
                              personnel_type='creators', operation="add")
    # check for project_members
    try:
        if len(body.project_members) == 0:
            print('NO MEMBERS')
    except Exception as exc:
        body.project_members = []
        consoleLogger.info("NOP: projects_post(): 'project_members' - {0}".format(exc))
    # add project_members
    update_projects_personnel(api_user=project_creator, fab_project=fab_project, personnel=body.project_members,
                              personnel_type='members', operation="add")
    # check for project_owners
    try:
        if len(body.project_owners) == 0:
            print('NO OWNERS')
            body.project_owners.append(str(project_creator.uuid))
        else:
            print('SOME OWNERS')
            body.project_owners.append(str(project_creator.uuid))
    except Exception as exc:
        body.project_owners = [str(project_creator.uuid)]
        consoleLogger.info("NOP: projects_post(): 'project_owners' - {0}".format(exc))
    # add project_owners
    update_projects_personnel(api_user=project_creator, fab_project=fab_project, personnel=body.project_owners,
                              personnel_type='owners', operation="add")
    db.session.commit()
    # metrics log - Project was created:
    # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef create by usr:dead-beef-dead-beef
    log_msg = 'Project event prj:{0} create by usr:{1}'.format(str(fab_project.uuid), str(project_creator.uuid))
    metricsLogger.info(log_msg)

    return fab_project


def create_fabric_project_from_uuid(uuid: str) -> FabricProjects:
    """
    * Denotes required fields
    - *active
    - co_cou_id_pc
    - co_cou_id_pm
    - co_cou_id_po
    - *description
    - *facility
    - *is_public
    - *name
    - preferences
    - profile
    - project_creators
    - project_members
    - project_owners
    - tags
    - *uuid
    """
    fab_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
    if not fab_project:
        fab_project = FabricProjects()
        co_cou_pc = FabricGroups.query.filter_by(name=uuid + '-pc').one_or_none()
        if co_cou_pc:
            now = datetime.now(timezone.utc)
            # set required fields
            fab_project.active = not co_cou_pc.deleted
            fab_project.created = co_cou_pc.created
            fab_project.description = co_cou_pc.description + ' (autogenerated by script)'
            fab_project.expires_on = now + timedelta(days=float(os.getenv('PROJECTS_RENEWAL_PERIOD_IN_DAYS')))
            fab_project.facility = os.getenv('CORE_API_DEFAULT_FACILITY')
            fab_project.is_locked = False
            fab_project.is_public = True
            fab_project.name = co_cou_pc.description
            fab_project.uuid = uuid
            db.session.add(fab_project)
            db.session.commit()
            consoleLogger.info('CREATE FabricProject: name={0}, uuid={1}'.format(fab_project.name, fab_project.uuid))
            # set optional fields
            fab_project.co_cou_id_pc = co_cou_pc.co_cou_id
            co_cou_pm = FabricGroups.query.filter_by(name=uuid + '-pm').one_or_none()
            if co_cou_pm:
                fab_project.co_cou_id_pm = co_cou_pm.co_cou_id
            co_cou_po = FabricGroups.query.filter_by(name=uuid + '-po').one_or_none()
            if co_cou_po:
                fab_project.co_cou_id_po = co_cou_po.co_cou_id
            # set project preferences
            create_projects_preferences(fab_project=fab_project)
            # set project profile
            create_profile_projects(fab_project=fab_project)
            # set project creators
            for pc_id in [x.people_id for x in FabricRoles.query.filter_by(name=co_cou_pc.name)]:
                pc = FabricPeople.query.filter_by(id=pc_id).one_or_none()
                if pc:
                    fab_project.project_creators.append(pc)
            # set project members
            for pm_id in [x.people_id for x in FabricRoles.query.filter_by(name=co_cou_pm.name)]:
                pm = FabricPeople.query.filter_by(id=pm_id).one_or_none()
                if pm:
                    fab_project.project_members.append(pm)
            # set project owners
            for po_id in [x.people_id for x in FabricRoles.query.filter_by(name=co_cou_po.name)]:
                po = FabricPeople.query.filter_by(id=po_id).one_or_none()
                if po:
                    fab_project.project_owners.append(po)
            db.session.commit()
        else:
            consoleLogger.warning(
                "NOT FOUND: create_fabric_project_from_uuid(): Unable to find cou with uuid: '{0}'".format(uuid))
    else:
        consoleLogger.info('FOUND FabricProject: name={0}, uuid={1}'.format(fab_project.name, fab_project.uuid))

    return fab_project


def get_project_membership(fab_project: FabricProjects, fab_person: FabricPeople) -> ProjectMembership:
    membership = ProjectMembership()
    person_roles = [r.name for r in fab_person.roles]
    membership.is_creator = str(fab_project.uuid) + '-pc' in person_roles
    membership.is_member = str(fab_project.uuid) + '-pm' in person_roles
    membership.is_owner = str(fab_project.uuid) + '-po' in person_roles
    membership.is_token_holder = str(fab_project.uuid) + '-tk' in person_roles

    return membership


def get_project_tags(fab_project: FabricProjects, fab_person: FabricPeople) -> [str]:
    tags = [t.tag for t in fab_project.tags]

    return tags


# Creators, Owners and Members - Projects
def get_projects_personnel(fab_project: FabricProjects = None, personnel_type: str = None) -> [Person]:
    """
    * Denotes required fields
    - email: <string>
    - * name: <string>
    - * uuid: <string>
    """
    personnel = []
    if personnel_type == 'creators':
        personnel = fab_project.project_creators
    elif personnel_type == 'owners':
        personnel = fab_project.project_owners
    elif personnel_type == 'members':
        personnel = fab_project.project_members
    elif personnel_type == 'tokens':
        personnel = fab_project.token_holders
    personnel_data = []
    for p in personnel:
        # get preferences (show_email)
        prefs = {pref.key: pref.value for pref in p.preferences}
        # set person attributes
        person = Person()
        person.email = p.preferred_email if prefs.get('show_email') else None
        person.name = p.display_name
        person.uuid = str(p.uuid)
        # add person to personnel_data
        personnel_data.append(person)

    return personnel_data


# Storage - Projects
def get_projects_storage(fab_project: FabricProjects = None) -> [StorageOne]:
    """
    Retrieve storage objects associated to the project
    """
    project_storage = []
    for stg in fab_project.project_storage:
        # set storage attributes
        storage = StorageOne()
        storage.active = stg.active
        storage.created_on = str(stg.created)
        storage.expires_on = str(stg.expires_on)
        # storage.project_name = fab_project.name  # <-- project name already known
        # storage.project_uuid = str(fab_project.uuid)  # <-- project uuid already known
        storage.requested_by_uuid = str(
            FabricPeople.query.filter_by(id=stg.requested_by_id).one_or_none().uuid)
        storage.site_list = [s.site for s in stg.sites]
        storage.uuid = str(stg.uuid)
        storage.volume_name = stg.volume_name
        storage.volume_size_gb = stg.volume_size_gb

        # add storage to project_storage
        project_storage.append(storage)

    return project_storage


def update_projects_personnel(api_user: FabricPeople = None, fab_project: FabricProjects = None,
                              personnel: [FabricPeople] = None,
                              personnel_type: str = None, operation: str = None) -> None:
    # get list of token holders to add/batch/remove
    personnel = list(set(personnel))
    # get FabricGroup information
    if personnel_type == 'creators':
        fab_group = FabricGroups.query.filter_by(name=str(fab_project.uuid) + '-pc').one_or_none()
    elif personnel_type == 'members':
        fab_group = FabricGroups.query.filter_by(name=str(fab_project.uuid) + '-pm').one_or_none()
    elif personnel_type == 'owners':
        fab_group = FabricGroups.query.filter_by(name=str(fab_project.uuid) + '-po').one_or_none()
    else:
        consoleLogger.error('Invalid personnel_type provided')
        fab_group = None
    # add
    if operation == 'add':
        if fab_group:
            # add token holders
            add_project_personnel(api_user, fab_project, fab_group, personnel, personnel_type)
    # batch
    elif operation == 'batch':
        # get p_orig information
        if personnel_type == 'creators':
            p_orig = [str(p.uuid) for p in fab_project.project_creators]
        elif personnel_type == 'members':
            p_orig = [str(p.uuid) for p in fab_project.project_members]
        elif personnel_type == 'owners':
            p_orig = [str(p.uuid) for p in fab_project.project_owners]
        else:
            p_orig = []
        p_add = array_difference(personnel, p_orig)
        p_remove = array_difference(p_orig, personnel)
        if fab_group:
            # add token holders
            add_project_personnel(api_user, fab_project, fab_group, p_add, personnel_type)
            # remove token holders
            remove_project_personnel(api_user, fab_project, fab_group, p_remove, personnel_type)
    # remove
    elif operation == 'remove':
        if fab_group:
            # remove token-holders
            remove_project_personnel(api_user, fab_project, fab_group, personnel, personnel_type)
    else:
        consoleLogger.error('Invalid operation provided')


def add_project_personnel(api_user: FabricPeople, fab_project: FabricProjects, fab_group: FabricGroups,
                          personnel: [str], personnel_type: str = None):
    # add personnel
    for uuid in personnel:
        p = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if personnel_type == 'creators' and not p.is_project_creator(project_uuid=fab_project.uuid):
            create_comanage_role(fab_person=p, fab_group=fab_group)
            fab_project.project_creators.append(p)
            db.session.commit()
            p_added = True
        elif personnel_type == 'members' and not p.is_project_member(project_uuid=fab_project.uuid):
            create_comanage_role(fab_person=p, fab_group=fab_group)
            fab_project.project_members.append(p)
            db.session.commit()
            p_added = True
        elif personnel_type == 'owners' and not p.is_project_owner(project_uuid=fab_project.uuid):
            create_comanage_role(fab_person=p, fab_group=fab_group)
            fab_project.project_owners.append(p)
            db.session.commit()
            p_added = True
        else:
            consoleLogger.warning(
                'AddProjectPersonnel: unable to add usr: {0} to project: {1} as creator/member/owner'.format(p.uuid,
                                                                                                             fab_project.uuid))
            p_added = False
        if p_added:
            # metrics log - Project creator/member/owner added:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add creator/member/owner usr:deaf-bead-deaf-bead: by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-add {1} usr:{2} by usr:{3}'.format(
                str(fab_project.uuid),
                personnel_type[:-1],
                str(p.uuid),
                str(api_user.uuid))
            metricsLogger.info(log_msg)


def remove_project_personnel(api_user: FabricPeople, fab_project: FabricProjects, fab_group: FabricGroups,
                             personnel: [str], personnel_type: str = None):
    # remove personnel
    for uuid in personnel:
        p = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        co_person_role = FabricRoles.query.filter(
            FabricRoles.co_person_id == p.co_person_id,
            FabricRoles.co_cou_id == fab_group.co_cou_id,
            FabricRoles.name == fab_group.name,
            FabricRoles.people_id == p.id
        ).one_or_none()
        if personnel_type == 'creators' and p.is_project_creator(project_uuid=fab_project.uuid):
            fab_project.project_creators.remove(p)
            delete_comanage_role(co_person_role_id=co_person_role.co_person_role_id)
            db.session.commit()
            p_removed = True
        elif personnel_type == 'members' and p.is_project_member(project_uuid=fab_project.uuid):
            fab_project.project_members.remove(p)
            delete_comanage_role(co_person_role_id=co_person_role.co_person_role_id)
            db.session.commit()
            p_removed = True
        elif personnel_type == 'owners' and p.is_project_owner(project_uuid=fab_project.uuid):
            fab_project.project_owners.remove(p)
            delete_comanage_role(co_person_role_id=co_person_role.co_person_role_id)
            db.session.commit()
            p_removed = True
        else:
            consoleLogger.warning(
                'RemoveProjectPersonnel: unable to remove usr: {0} from project: {1} as creator/member/owner'.format(
                    p.uuid,
                    fab_project.uuid))
            p_removed = False
        if p_removed:
            # metrics log - Project creator/member/owner removed:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-remove creator/member/owner usr:deaf-bead-deaf-bead: by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-remove {1} usr:{2} by usr:{3}'.format(
                str(fab_project.uuid),
                personnel_type[:-1],
                str(p.uuid),
                str(api_user.uuid))
            metricsLogger.info(log_msg)


def update_projects_communities(api_user: FabricPeople = None, fab_project: FabricProjects = None,
                                communities: [str] = None) -> None:
    comms_orig = [p.community for p in fab_project.communities]
    comms_new = communities
    comms_add = array_difference(comms_new, comms_orig)
    comms_remove = array_difference(comms_orig, comms_new)
    # add projects communities
    for comm in comms_add:
        fab_comm = ProjectsCommunities.query.filter(
            ProjectsCommunities.projects_id == fab_project.id, ProjectsCommunities.community == comm).one_or_none()
        if not fab_comm:
            fab_comm = ProjectsCommunities()
            fab_comm.projects_id = fab_project.id
            fab_comm.community = comm
            fab_project.communities.append(fab_comm)
            db.session.commit()
            # metrics log - Project community added:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add community Networks by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-add community \'{1}\' by usr:{2}'.format(str(fab_project.uuid),
                                                                                             comm,
                                                                                             str(api_user.uuid))
            metricsLogger.info(log_msg)
    # remove projects communities
    for comm in comms_remove:
        fab_comm = ProjectsCommunities.query.filter(
            ProjectsCommunities.projects_id == fab_project.id, ProjectsCommunities.community == comm).one_or_none()
        if fab_comm:
            fab_project.communities.remove(fab_comm)
            db.session.delete(fab_comm)
            db.session.commit()
            # metrics log - Project community removed:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add community Network by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-remove community \'{1}\' by usr:{2}'.format(str(fab_project.uuid),
                                                                                                comm,
                                                                                                str(api_user.uuid))
            metricsLogger.info(log_msg)


def update_projects_project_funding(api_user: FabricPeople = None, fab_project: FabricProjects = None,
                                    project_funding: [object] = None) -> None:
    fs_orig = project_funding_to_array(fab_project.project_funding)
    fs_new = project_funding_to_array(project_funding)
    fs_add = array_difference(fs_new, fs_orig)
    fs_remove = array_difference(fs_orig, fs_new)
    # add projects funding
    for fs in fs_add:
        agency = fs.get('agency', None)
        award_amount = fs.get('award_amount', None)
        award_number = fs.get('award_number', None)
        directorate = fs.get('directorate', None)
        fab_fs = ProjectsFunding.query.filter(
            ProjectsFunding.projects_id == fab_project.id,
            ProjectsFunding.agency == agency,
            ProjectsFunding.award_amount == award_amount,
            ProjectsFunding.award_number == award_number
        ).one_or_none()
        print(fab_fs)
        if not fab_fs:
            fab_fs = ProjectsFunding()
            fab_fs.projects_id = fab_project.id
            fab_fs.agency = agency
            fab_fs.award_amount = award_amount
            fab_fs.award_number = award_number
            fab_fs.directorate = directorate
            fab_project.project_funding.append(fab_fs)
            db.session.commit()
            # metrics log - project-funding added:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add project-funding NSF by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-add project-funding \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid), agency, str(api_user.uuid))
            metricsLogger.info(log_msg)

    # remove projects funding
    for fs in fs_remove:
        agency = fs.get('agency', None)
        award_amount = fs.get('award_amount', None)
        award_number = fs.get('award_number', None)
        fab_fs = ProjectsFunding.query.filter(
            ProjectsFunding.projects_id == fab_project.id,
            ProjectsFunding.agency == agency,
            ProjectsFunding.award_amount == award_amount,
            ProjectsFunding.award_number == award_number
        ).one_or_none()
        if fab_fs:
            fab_project.project_funding.remove(fab_fs)
            db.session.delete(fab_fs)
            db.session.commit()
            # metrics log - project-funding removed:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add project-funding NSF by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-remove project-funding \'{1}\' by usr:{2}'.format(
                str(fab_project.uuid), agency, str(api_user.uuid))
            metricsLogger.info(log_msg)


def update_projects_tags(api_user: FabricPeople = None, fab_project: FabricProjects = None, tags: [str] = None) -> None:
    tags_orig = [p.tag for p in fab_project.tags]
    tags_new = tags
    tags_add = array_difference(tags_new, tags_orig)
    tags_remove = array_difference(tags_orig, tags_new)
    # add projects tags
    for tag in tags_add:
        fab_tag = ProjectsTags.query.filter(
            ProjectsTags.projects_id == fab_project.id, ProjectsTags.tag == tag).one_or_none()
        if not fab_tag:
            fab_tag = ProjectsTags()
            fab_tag.projects_id = fab_project.id
            fab_tag.tag = tag
            fab_project.tags.append(fab_tag)
            db.session.commit()
            # metrics log - Project tag added:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add tag Net.Peering by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-add tag \'{1}\' by usr:{2}'.format(str(fab_project.uuid), tag,
                                                                                       str(api_user.uuid))
            metricsLogger.info(log_msg)
    # remove projects tags
    for tag in tags_remove:
        fab_tag = ProjectsTags.query.filter(
            ProjectsTags.projects_id == fab_project.id, ProjectsTags.tag == tag).one_or_none()
        if fab_tag:
            fab_project.tags.remove(fab_tag)
            db.session.delete(fab_tag)
            db.session.commit()
            # metrics log - Project tag removed:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add tag Net.Peering by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-remove tag \'{1}\' by usr:{2}'.format(str(fab_project.uuid), tag,
                                                                                          str(api_user.uuid))
            metricsLogger.info(log_msg)


def update_projects_token_holders(api_user: FabricPeople = None, fab_project: FabricProjects = None,
                                  token_holders: [FabricPeople] = None,
                                  operation: str = None) -> None:
    # get list of token holders to add/batch/remove
    token_holders = list(set(token_holders))
    # get FabricGroup information
    fab_group = FabricGroups.query.filter_by(name=str(fab_project.uuid) + '-tk').one_or_none()
    # add
    if operation == 'add':
        if fab_group:
            # add token holders
            add_project_token_holders(api_user, fab_project, fab_group, token_holders)
    # batch
    elif operation == 'batch':
        p_orig = [str(p.uuid) for p in fab_project.token_holders]
        p_new = token_holders
        p_add = array_difference(p_new, p_orig)
        p_remove = array_difference(p_orig, p_new)
        if fab_group:
            # add token holders
            add_project_token_holders(api_user, fab_project, fab_group, p_add)
            # remove token holders
            remove_project_token_holders(api_user, fab_project, fab_group, p_remove)
    # remove
    elif operation == 'remove':
        if fab_group:
            # remove token-holders
            remove_project_token_holders(api_user, fab_project, fab_group, token_holders)
    else:
        consoleLogger.error('Invalid operation provided')


def add_project_token_holders(api_user: FabricPeople, fab_project: FabricProjects, fab_group: FabricGroups,
                              token_holders: [str]):
    # add token holders
    for uuid in token_holders:
        p = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if p and not p.is_token_holder(project_uuid=fab_project.uuid) and (
                p.is_project_creator(project_uuid=fab_project.uuid) or p.is_project_member(
            project_uuid=fab_project.uuid) or p.is_project_owner(project_uuid=fab_project.uuid)):
            create_comanage_role(fab_person=p, fab_group=fab_group)
            fab_project.token_holders.append(p)
            db.session.commit()
            # metrics log - Project token-holder added:
            # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-add token-holder usr:deaf-bead-deaf-bead: by usr:fead-beaf-fead-beaf
            log_msg = 'Project event prj:{0} modify-add token-holder usr:{1} by usr:{2}'.format(
                str(fab_project.uuid),
                str(p.uuid),
                str(api_user.uuid))
            metricsLogger.info(log_msg)
        else:
            consoleLogger.error(
                'AddTokenHolder: unable to add usr: {0} to project: {1} as a token holder'.format(p.uuid,
                                                                                                  fab_project.uuid))


def remove_project_token_holders(api_user: FabricPeople, fab_project: FabricProjects, fab_group: FabricGroups,
                                 token_holders: [str]):
    # remove token-holders
    for uuid in token_holders:
        p = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
        if p.is_token_holder(project_uuid=fab_project.uuid):
            co_person_role = FabricRoles.query.filter(
                FabricRoles.co_person_id == p.co_person_id,
                FabricRoles.co_cou_id == fab_group.co_cou_id,
                FabricRoles.name == fab_group.name,
                FabricRoles.people_id == p.id
            ).one_or_none()
            if co_person_role:
                fab_project.token_holders.remove(p)
                delete_comanage_role(co_person_role_id=co_person_role.co_person_role_id)
                db.session.commit()
                # metrics log - Project token-holder removed:
                # 2022-09-06 19:45:56,022 Project event prj:dead-beef-dead-beef modify-remove token-holder usr:deaf-bead-deaf-bead: by usr:fead-beaf-fead-beaf
                log_msg = 'Project event prj:{0} modify-remove token-holder usr:{1} by usr:{2}'.format(
                    str(fab_project.uuid),
                    str(p.uuid),
                    str(api_user.uuid))
                metricsLogger.info(log_msg)
