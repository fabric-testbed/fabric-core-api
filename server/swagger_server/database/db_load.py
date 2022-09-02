import os
from datetime import datetime
from uuid import uuid4

from comanage_api import ComanageApi

from swagger_server.__main__ import app, db, logger
from swagger_server.database.models.people import EmailAddresses, FabricGroups, FabricPeople, FabricRoles, Organizations
from swagger_server.database.models.preferences import FabricPreferences
from swagger_server.database.models.profiles import FabricProfilesPeople, FabricProfilesProjects
from swagger_server.database.models.projects import FabricProjects
from swagger_server.response_code import PEOPLE_PREFERENCES, PEOPLE_PROFILE_PREFERENCES, PROJECTS_PREFERENCES, \
    PROJECTS_PROFILE_PREFERENCES
from swagger_server.response_code.comanage_utils import update_groups, update_organizations
from swagger_server.response_code.people_utils import create_fabric_person_from_co_person_id, update_fabric_person
from swagger_server.response_code.projects_utils import create_fabric_project_from_uuid

app.app_context().push()

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def load_email_addresses(co_person_id: int, fab_person: FabricPeople) -> None:
    """
    __tablename__ = 'email_addresses'

    co_email_address_id = db.Column(db.Integer)
    email = db.Column(db.String())
    type = db.Column(db.String())
    people_id = db.Column(db.Integer, db.ForeignKey(PEOPLE_ID), nullable=False)
    """
    co_emails = api.email_addresses_view_per_person(
        person_type='copersonid',
        person_id=co_person_id
    ).get('EmailAddresses', [])
    for e in co_emails:
        co_email_address_id = e.get('Id')
        fab_email = EmailAddresses.query.filter_by(co_email_address_id=co_email_address_id).first()
        if not fab_email:
            logger.info("CREATE: entry in 'email_addresses' table for co_person_id: {0}".format(co_person_id))
            fab_email = EmailAddresses()
            fab_email.co_email_address_id = co_email_address_id
            fab_email.email = e.get('Mail')
            fab_email.type = e.get('Type')
            fab_email.people_id = fab_person.id
            db.session.add(fab_email)
            db.session.commit()


def load_identifiers(co_person_id: int, fab_person: FabricPeople) -> None:
    """
    oidc_claim_sub
    fabricid
    eppn
    """
    # set oidc_claim_sub and fabricid
    co_identifiers = api.identifiers_view_per_entity(
        entity_type='copersonid',
        entity_id=co_person_id
    ).get('Identifiers', [])
    for i in co_identifiers:
        if i.get('Type', None) == 'oidcsub' and not fab_person.oidc_claim_sub:
            logger.info("UPDATE: entry in 'people' table for 'oidc_claim_sub': {0}".format(fab_person.display_name))
            fab_person.oidc_claim_sub = i.get('Identifier', '')
        if i.get('Type', None) == 'eppn' and not fab_person.oidc_claim_eppn:
            logger.info("UPDATE: entry in 'people' table for 'oidc_claim_eppn': {0}".format(fab_person.display_name))
            fab_person.oidc_claim_eppn = i.get('Identifier', '')
        if i.get('Type', None) == os.getenv('CORE_API_CO_USER_IDENTIFIER', 'registryid') and not fab_person.fabric_id:
            logger.info(
                "UPDATE: entry in 'people' table for '{0}': {1}".format(os.getenv('CORE_API_CO_USER_IDENTIFIER'),
                                                                        fab_person.display_name))
            fab_person.fabric_id = i.get('Identifier', '')
    db.session.commit()


def load_org_affiliation(co_person_id: int, fab_person: FabricPeople) -> None:
    co_orgidentity_links = api.coorg_identity_links_view_by_identity(
        identity_type='copersonid',
        identity_id=co_person_id
    ).get('CoOrgIdentityLinks', [])
    for org_link in co_orgidentity_links:
        org = Organizations.query.filter_by(org_identity_id=org_link.get('OrgIdentityId')).one_or_none()
        if org:
            fab_person.org_affiliation = org.id
            db.session.commit()


def load_organizations() -> None:
    """
    affiliation = db.Column(db.String(), nullable=False)
    org_identity_id = db.Column(db.Integer)
    organization = db.Column(db.String(), nullable=False)
    """
    co_orgs = api.org_identities_view_per_co().get('OrgIdentities', [])
    for org in co_orgs:
        org_identity_id = org.get('Id', None)
        organization = org.get('O', None)
        affiliation = org.get('Affiliation', None)
        if org_identity_id and organization and affiliation and not org.get('Deleted'):
            fab_org = Organizations.query.filter_by(org_identity_id=org_identity_id).one_or_none()
            if not fab_org:
                try:
                    fab_org = Organizations()
                    fab_org.org_identity_id = org_identity_id
                    fab_org.organization = organization
                    fab_org.affiliation = affiliation
                    db.session.add(fab_org)
                    logger.info("CREATE: entry in 'organizations' table for org_identity_id: {0}".format(org_identity_id))
                except Exception as exc:
                    logger.error(exc)
                    continue
    db.session.commit()


def create_people_preferences(fab_person: FabricPeople) -> None:
    """
    key = db.Column(db.String(), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    profile_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    # profile_projects_id = db.Column(db.Integer, db.ForeignKey('profile_projects.id'), nullable=True)
    # projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    type = db.Column(db.Enum(PreferenceTypeEnum), default=PreferenceTypeEnum.people, nullable=False)
    value = db.Column(db.Boolean, default=True, nullable=False)
    """
    pref_type = 'people'
    for key in PEOPLE_PREFERENCES:
        pref = FabricPreferences()
        pref.key = key
        pref.value = True
        pref.type = pref_type
        pref.people_id = fab_person.id
        db.session.add(pref)
        fab_person.preferences.append(pref)
    db.session.commit()


def create_projects_preferences(fab_project: FabricProjects) -> None:
    """
    key = db.Column(db.String(), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    profile_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    profile_projects_id = db.Column(db.Integer, db.ForeignKey('profile_projects.id'), nullable=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    type = db.Column(db.Enum(PreferenceTypeEnum), default=PreferenceTypeEnum.people, nullable=False)
    value = db.Column(db.Boolean, default=True, nullable=False)
    """
    pref_type = 'projects'
    for key in PROJECTS_PREFERENCES:
        pref = FabricPreferences()
        pref.key = key
        pref.value = True
        pref.type = pref_type
        pref.projects_id = fab_project.id
        db.session.add(pref)
        fab_project.preferences.append(pref)
    db.session.commit()


def create_profile_people(fab_person: FabricPeople) -> None:
    fab_profile = FabricProfilesPeople()
    fab_profile.uuid = uuid4()
    fab_profile.people = fab_person
    db.session.add(fab_profile)
    db.session.commit()


def create_profile_projects(fab_project: FabricProjects) -> None:
    fab_profile = FabricProfilesProjects()
    fab_profile.uuid = uuid4()
    fab_profile.projects = fab_project
    db.session.add(fab_profile)
    db.session.commit()


def create_profile_people_preferences(fab_profile: FabricProfilesPeople) -> None:
    pref_type = 'profile_people'
    for key in PEOPLE_PROFILE_PREFERENCES:
        pref = FabricPreferences()
        pref.key = key
        pref.value = True
        pref.type = pref_type
        pref.profile_people_id = fab_profile.id
        db.session.add(pref)
        fab_profile.preferences.append(pref)
    db.session.commit()


def create_profile_projects_preferences(fab_profile: FabricProfilesProjects) -> None:
    pref_type = 'profile_projects'
    for key in PROJECTS_PROFILE_PREFERENCES:
        pref = FabricPreferences()
        pref.key = key
        pref.value = True
        pref.type = pref_type
        pref.profile_projects_id = fab_profile.id
        db.session.add(pref)
        fab_profile.preferences.append(pref)
    db.session.commit()


def load_people() -> None:
    """
    __tablename__ = 'people'

    * active = db.Column(db.Boolean, nullable=False, default=False)
    #bastion_login = db.Column(db.String(), nullable=True)
    * co_person_id = db.Column(db.Integer, nullable=True)
    * display_name = db.Column(db.String(), nullable=False)
    email_addresses = db.relationship('EmailAddresses', backref='people', lazy=True)
    * fabric_id = db.Column(db.String(), nullable=True)
    #oidc_claim_email = db.Column(db.String(), nullable=True)
    #oidc_claim_eppn = db.Column(db.String(), nullable=True)
    #oidc_claim_family_name = db.Column(db.String(), nullable=True)
    #oidc_claim_given_name = db.Column(db.String(), nullable=True)
    #oidc_claim_idp_name = db.Column(db.String(), nullable=True)
    #oidc_claim_name = db.Column(db.String(), nullable=True)
    * oidc_claim_sub = db.Column(db.String(), nullable=False)
    * org_affiliation = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=True)
    preferences = db.relationship('Preferences', backref='people', lazy=True)
    * preferred_email = db.Column(db.String(), nullable=False)
    profile = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    * registered_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    # roles = db.relationship('FabricRoles', backref='people', lazy=True)
    # sshkeys = db.relationship('SshKeys', backref='people', lazy=True)
    * uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    co_people = api.copeople_view_per_co().get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        person = FabricPeople.query.filter_by(co_person_id=co_person_id).first()
        if not person:
            logger.info("CREATE: entry in 'people' table for co_person_id: {0}".format(co_person_id))
            person = FabricPeople()
            # set uuid
            person.uuid = uuid4()
            # set co_person_id
            person.co_person_id = co_person_id
            # set display_name
            co_names = api.names_view_per_person(
                person_type='copersonid',
                person_id=co_person_id
            ).get('Names', [])
            for n in co_names:
                if n.get('PrimaryName', False):
                    person.oidc_claim_family_name = n.get('Family', '')
                    person.oidc_claim_given_name = n.get('Given', '')
                    person.display_name = n.get('Given', '') + ' ' + n.get('Family', '')
            # set preferred_email
            co_emails = api.email_addresses_view_per_person(
                person_type='copersonid',
                person_id=co_person_id
            ).get('EmailAddresses', [])
            for e in co_emails:
                if e.get('Type', None) == 'official':
                    person.preferred_email = e.get('Mail', '')
                    break
            db.session.add(person)
            db.session.commit()
            # create initial people preferences
            create_people_preferences(fab_person=person)
            # create people profile
            create_profile_people(fab_person=person)
            # create initial people profile preferences
            create_profile_people_preferences(fab_profile=person.profile)
        else:
            logger.info(
                "NO CHANGE: entry in 'people' table for co_person_id: {0}, name = '{1}'".format(co_person_id,
                                                                                                person.display_name))
        # set email_addresses
        load_email_addresses(co_person_id=co_person_id, fab_person=person)
        # set identifiers
        load_identifiers(co_person_id=co_person_id, fab_person=person)
        # set org_affiliation
        load_org_affiliation(co_person_id=co_person_id, fab_person=person)
        # active
        # TODO: check FabricRoles for member:active in fabric-active-users after CoPersonRoles are loaded


def load_people_roles():
    """
    __tablename__ = 'roles'

    affiliation = db.Column(db.String(), nullable=False)
    co_cou_id = db.Column(db.Integer, nullable=False)
    co_person_id = db.Column(db.Integer, nullable=False)
    co_person_role_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey(_PEOPLE_ID), nullable=False)
    status = db.Column(db.String(), nullable=False)
    """
    co_people = api.copeople_view_per_co().get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        fab_person = FabricPeople.query.filter_by(co_person_id=co_person_id).first()
        if fab_person:
            co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id)
            if co_roles:
                co_roles = co_roles.get('CoPersonRoles', [])
                for co_role in co_roles:
                    co_person_role_id = co_role.get('Id', None)
                    co_cou_id = co_role.get('CouId')
                    fab_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
                    fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
                    if not fab_role:
                        if fab_group:
                            fab_role = FabricRoles()
                            fab_role.affiliation = co_role.get('Affiliation', 'member')
                            fab_role.co_cou_id = co_cou_id
                            fab_role.co_person_id = co_person_id
                            fab_role.co_person_role_id = co_person_role_id
                            fab_role.name = fab_group.name
                            fab_role.description = fab_group.description
                            fab_role.people_id = fab_person.id
                            fab_role.status = co_role.get('Status', 'Pending')
                            try:
                                db.session.add(fab_role)
                                db.session.commit()
                                logger.info(
                                    "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(
                                        co_person_role_id))
                            except Exception as exc:
                                logger.error('DUPLICATE ROLE: {0}'.format(exc))
                                db.session.rollback()
                                continue
                        else:
                            logger.warning(
                                "ERROR: unable to locate co_cou_id {0} in the 'groups' table".format(co_cou_id))
                    else:
                        modified = False
                        if fab_role.name != fab_group.name:
                            logger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, name = '{1}'".format(
                                    co_person_role_id, fab_group.name))
                            fab_role.name = fab_group.name
                            db.session.commit()
                            modified = True
                        if fab_role.description != fab_group.description:
                            logger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, description = '{1}'".format(
                                    co_person_role_id, fab_group.description))
                            fab_role.description = fab_group.description
                            db.session.commit()
                            modified = True
                        if fab_role.status != co_role.get('Status'):
                            logger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, status = '{1}'".format(
                                    co_person_role_id, co_role.get('Status')))
                            fab_role.status = co_role.get('Status')
                            db.session.commit()
                            modified = True
                        if not modified:
                            logger.info(
                                "NO CHANGE: entry in 'roles' table for co_person_role_id: {0}".format(
                                    co_person_role_id))
        else:
            logger.warning("ERROR: unable to locate co_person_id {0} in the 'people' table".format(co_person_id))


def add_project_personnel(fab_project: FabricProjects = None, member_type: str = None) -> None:
    group = None
    if member_type == 'creator':
        group = FabricGroups.query.filter_by(name=fab_project.uuid + '-pc').one_or_none()
    elif member_type == 'owner':
        group = FabricGroups.query.filter_by(name=fab_project.uuid + '-po').one_or_none()
    elif member_type == 'member':
        group = FabricGroups.query.filter_by(name=fab_project.uuid + '-pm').one_or_none()
    if group:
        if member_type == 'creator':
            fab_project.co_cou_id_pc = group.co_cou_id
        elif member_type == 'owner':
            fab_project.co_cou_id_po = group.co_cou_id
        elif member_type == 'member':
            fab_project.co_cou_id_pm = group.co_cou_id
        people_group = FabricRoles.query.filter_by(co_cou_id=group.co_cou_id).all()
        for person in people_group:
            fab_person = FabricPeople.query.filter_by(id=person.people_id).one_or_none()
            if fab_person:
                if member_type == 'creator':
                    fab_project.project_creators.append(fab_person)
                elif member_type == 'owner':
                    fab_project.project_owners.append(fab_person)
                elif member_type == 'member':
                    fab_project.project_members.append(fab_person)
        db.session.commit()


def load_projects():
    """
    __tablename__ = 'projects'

    active = db.Column(db.Boolean, default=True, nullable=False)
    co_cou_id_pc = db.Column(db.Integer, nullable=True)
    co_cou_id_pm = db.Column(db.Integer, nullable=True)
    co_cou_id_po = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    facility = db.Column(db.String(), default=os.getenv('CORE_API_DEFAULT_FACILITY'), nullable=False)
    name = db.Column(db.String(), nullable=False)
    preferences = db.relationship('FabricPreferences', backref='projects', lazy=True)
    profile = db.relationship('FabricProfilesProjects', backref='projects', uselist=False, lazy=True)
    project_creators = db.relationship('FabricPeople', secondary=projects_creators, lazy='subquery',
                                       backref=db.backref('project_creators', lazy=True))
    project_members = db.relationship('FabricPeople', secondary=projects_members, lazy='subquery',
                                      backref=db.backref('project_members', lazy=True))
    project_owners = db.relationship('FabricPeople', secondary=projects_owners, lazy='subquery',
                                     backref=db.backref('project_owners', lazy=True))
    # publications = db.relationship('Publications', secondary=publications, lazy='subquery',
    #                                backref=db.backref('projects', lazy=True))
    tags = db.relationship('ProjectsTags', backref='projects', lazy=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    logger.info("Load database table 'projects' as FabricProjects")
    project_cous = FabricGroups.query.filter(
        FabricGroups.co_parent_cou_id == os.getenv('COU_ID_PROJECTS')).order_by(
        FabricGroups.name).all()
    for cou in project_cous:
        uuid = cou.name.rsplit('-', 1)[0]
        project = FabricProjects.query.filter(
            FabricProjects.uuid == uuid
        ).one_or_none()
        if not project:
            logger.info("CREATE: entry in 'projects' table for uuid: {0}".format(uuid))
            project = FabricProjects()
            project.active = not cou.deleted
            project.description = cou.description + ' (added by load script)'
            project.facility = os.getenv('CORE_API_DEFAULT_FACILITY')
            project.name = cou.description
            project.uuid = uuid
            db.session.add(project)
            db.session.commit()
            # add project creators
            add_project_personnel(fab_project=project, member_type='creator')
            # add project members
            add_project_personnel(fab_project=project, member_type='member')
            # add project owners
            add_project_personnel(fab_project=project, member_type='owner')
            # create initial projects preferences
            create_projects_preferences(fab_project=project)
            # create projects profile
            create_profile_projects(fab_project=project)
            # create initial projects profile preferences
            create_profile_projects_preferences(fab_profile=project.profile)
            db.session.commit()
        else:
            logger.info("NO CHANGE: entry in 'projects' table for uuid: {0}".format(uuid))


def load_groups():
    """
    __tablename__ = 'groups'

    co_cou_id = db.Column(db.Integer)
    co_parent_cou_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String())
    description = db.Column(db.Text)
    deleted = db.Column(db.Boolean, default=False)
    """
    cous = api.cous_view_per_co().get('Cous', [])
    for co_cou in cous:
        co_cou_id = co_cou.get('Id')
        fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
        if not fab_group:
            logger.info("CREATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
            fab_group = FabricGroups()
            fab_group.co_cou_id = co_cou_id
            fab_group.co_parent_cou_id = co_cou.get('ParentId', None)
            print(co_cou.get('Created'))
            fab_group.created = datetime.strptime(co_cou.get('Created'), '%d/%m/%y %H:%M:%S')
            fab_group.name = co_cou.get('Name')
            fab_group.description = co_cou.get('Description')
            fab_group.deleted = co_cou.get('Deleted')
            db.session.add(fab_group)
            db.session.commit()
        else:
            modified = False
            if fab_group.name != co_cou.get('Name'):
                logger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, name = '{1}'".format(
                    co_cou_id, fab_group.name))
                fab_group.name = co_cou.get('Name')
                db.session.commit()
                modified = True
            if fab_group.description != co_cou.get('Description'):
                logger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, description = '{1}'".format(
                    co_cou_id, fab_group.description))
                fab_group.description = co_cou.get('Description')
                db.session.commit()
                modified = True
            if fab_group.deleted != co_cou.get('Deleted'):
                logger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, deleted = '{1}'".format(
                    co_cou_id, fab_group.deleted))
                fab_group.deleted = co_cou.get('Deleted')
                db.session.commit()
                modified = True
            if not modified:
                logger.info("NO CHANGE: entry in 'groups' table for co_cou_id: {0}, name = '{1}'".format(
                    co_cou_id, fab_group.name))


def load_people_active():
    """
    Update FabricPeople 'active' status
    """
    fab_people = FabricPeople.query.all()
    for person in fab_people:
        roles = person.roles
        for role in roles:
            if role.co_cou_id == int(os.getenv('COU_ID_ACTIVE_USERS')) and str(role.status).casefold() == 'active':
                logger.info("UPDATE: FabricPeople: {0} - Active = True".format(person.display_name))
                person.active = True
                db.session.commit()
                break


def load_people_from_comanage():
    co_people = api.copeople_view_per_co().get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        fab_person = FabricPeople.query.filter_by(co_person_id=co_person_id).one_or_none()
        if not fab_person:
            fab_person = create_fabric_person_from_co_person_id(co_person_id=co_person_id)
        update_fabric_person(fab_person=fab_person)


def load_projects_from_groups():
    project_cous = FabricGroups.query.filter(
        FabricGroups.co_parent_cou_id == os.getenv('COU_ID_PROJECTS')).order_by(
        FabricGroups.name).all()
    for cou in project_cous:
        uuid = cou.name.rsplit('-', 1)[0]
        create_fabric_project_from_uuid(uuid=uuid)


if __name__ == '__main__':
    logger.info("--- Load database table 'groups' as FabricGroups ---")
    update_groups()
    logger.info("--- Load database table 'organizations' as Organizations ---")
    update_organizations()
    logger.info("--- Load database table 'people' as FabricPeople ---")
    load_people_from_comanage()
    logger.info("--- Load database table 'projects' as FabricProjects ---")
    load_projects_from_groups()
