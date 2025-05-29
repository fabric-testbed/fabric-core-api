import os
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import EnumEvents, EnumEventTypes
from swagger_server.database.models.people import FabricGroups, FabricPeople, FabricRoles, UserSubjectIdentifiers
from swagger_server.database.models.projects import FabricProjects
from swagger_server.response_code.comanage_utils import api, create_comanage_role, delete_comanage_role, \
    is_fabric_active_user, update_email_addresses, update_org_affiliation, update_people_identifiers, \
    update_people_roles, update_user_org_affiliations, update_user_subject_identities
from swagger_server.response_code.core_api_utils import add_core_api_event, is_valid_uuid
from swagger_server.response_code.preferences_utils import create_people_preferences
from swagger_server.response_code.profiles_utils import create_profile_people
from swagger_server.response_code.projects_utils import remove_project_token_holders
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims


def get_person_by_login_claims() -> tuple[FabricPeople | Any, Any | None]:
    """
    Attempt to get FABRIC person based on 'sub' claim

    Example claims
    {
        'aud': 'cilogon:/client_id/617cecdd74e32be4d818ca1151531dff',
        'email': 'michael.j.stealey@gmail.com',
        'family_name': 'J. Stealey',
        'given_name': 'Michael',
        'iss': 'https://cilogon.org',
        'name': 'Michael J. Stealey',
        'sub': 'http://cilogon.org/serverA/users/2911496'
    }
    """
    try:
        claims = vouch_get_custom_claims()
        claims_sub = claims.get('sub', None)
        if claims_sub:
            # search for existing fab_person by sub
            fab_person_id = UserSubjectIdentifiers.query.filter(
                UserSubjectIdentifiers.sub == claims_sub
            ).one_or_none()
            if fab_person_id and fab_person_id.sub == claims_sub:
                fab_person = FabricPeople.query.filter_by(
                    id=fab_person_id.people_id
                ).first()
            else:
                # check COmanage for user by sub
                co_person = api.copeople_view_per_identifier(
                    identifier=claims_sub, distinct_by_id=True
                ).get('CoPeople', [])
                if co_person:
                    # co_person exists - try to get fab_person by co_person_id
                    fab_person = FabricPeople.query.filter(
                        FabricPeople.co_person_id == co_person[0].get('Id')
                    ).one_or_none()
                    if fab_person:
                        # fab_person exists, update person to pick up new sub from COmanage
                        update_fabric_person(fab_person=fab_person)
                    else:
                        # fab_person does not exist, create a new user account from login
                        fab_person = create_fabric_person_from_login(claims=claims)
                else:
                    # co_person does not exist, return empty fab_person object
                    fab_person = FabricPeople()
                    consoleLogger.debug('OIDC - invalid sub: {0}'.format(claims))
        else:
            # sub value not part of claim information
            fab_person = FabricPeople()
    except Exception as exc:
        details = 'Oops! something went wrong with get_person_by_login_claims(): {0}'.format(exc)
        consoleLogger.error(details)
        claims = {'source': 'exception'}
        fab_person = FabricPeople()

    return fab_person, claims.get('source')


def create_fabric_person_from_login(claims: dict = None) -> FabricPeople:
    """
    Create a new FABRIC user if the user had previously enrolled, otherwise prompt to enroll

    Create by login attributes
    - created - timestamp created (TimestampMixin)
    - display_name - initially OIDC scope: profile:name
    - id - primary key (BaseMixin)
    - oidc_claim_email - OIDC scope email:email
    - oidc_claim_family_name - OIDC scope profile:family_name
    - oidc_claim_given_name - OIDC scope profile:given_name
    - oidc_claim_name - OIDC scope profile:name
    - oidc_claim_sub - OIDC scope openid:sub
    - preferences - array of preference booleans
    - preferred_email - initially OIDC scope: email:email
    - profile - one-to-one relationship with profiles_people table
    - registered_on - timestamp user was registered on
    - uuid - unique universal identifier
    """
    fab_person = FabricPeople()
    try:
        if claims.get('sub'):
            # search for person by sub
            co_person = api.copeople_view_per_identifier(
                identifier=claims.get('sub'), distinct_by_id=True
            ).get('CoPeople', [])
            # get official email address            
            if claims.get('email'):
                fab_person_email = claims.get('email')
            else:
                try:
                    per_person_email_addresses = api.email_addresses_view_per_person(
                        person_type='copersonid',
                        person_id=co_person[0].get('Id')
                    )
                    fab_person_email = per_person_email_addresses.get('EmailAddresses')[0].get('Mail')
                    consoleLogger.info('OIDC_CLAIM_EMAIL: not found, retrieved from COmanage')
                except Exception as exc:
                    # set fab_person_email to None which will not allow a user account to be created
                    consoleLogger.error('OIDC_CLAIM_EMAIL: not found, unable to retrieve from COmanage', exc)
                    fab_person_email = None
            if co_person and is_fabric_active_user(co_person_id=co_person[0].get('Id')):
                fab_person = create_fabric_person_from_co_person_id(co_person_id=co_person[0].get('Id'))
                fab_person.oidc_claim_email = fab_person_email
                fab_person.oidc_claim_sub = claims.get('sub')
                fab_person.preferred_email = fab_person_email
                fab_person.updated = datetime.now(timezone.utc) - timedelta(seconds=int(
                    os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')))
                # generate bastion_login
                fab_person.bastion_login = generate_bastion_login(fab_person=fab_person)
                # generate gecos
                fab_person.gecos = generate_gecos(fab_person=fab_person)
                db.session.commit()
                # update user
                update_fabric_person(fab_person=fab_person)
                # add event people_create
                add_core_api_event(event=EnumEvents.people_create.name,
                                   event_date=fab_person.registered_on,
                                   event_triggered_by=fab_person.uuid,
                                   event_type=EnumEventTypes.people.name,
                                   people_uuid=fab_person.uuid,
                                   project_is_public=None,
                                   project_uuid=None
                                   )
                # TODO: notification email people_create
    except Exception as exc:
        details = 'Oops! something went wrong with create_fabric_person_from_login(): {0}'.format(exc)
        consoleLogger.error(details)

    return fab_person


def find_fabric_person_by_oidcsub_identifier(co_person_id: int = None) -> FabricPeople | None:
    identity = dict()
    co_identifiers = api.identifiers_view_per_entity(
        entity_type='copersonid', entity_id=co_person_id).get('Identifiers', [])
    for ident in co_identifiers:
        if ident.get('Type', None) == 'eppn':
            identity['eppn'] = ident.get('Identifier', '')
        if ident.get('Type', None) == os.getenv('CORE_API_CO_USER_IDENTIFIER', 'fabricid'):
            identity['fabric_id'] = ident.get('Identifier', '')
        if ident.get('Type', None) == 'oidcsub':
            identity['oidc_claim_sub'] = ident.get('Identifier', '')
    fab_person = FabricPeople.query.filter_by(oidc_claim_sub=identity.get('oidc_claim_sub', None)).one_or_none()
    if fab_person:
        return fab_person
    else:
        return None


def create_fabric_person_from_co_person_id(co_person_id: int = None) -> FabricPeople:
    """
    Create by co_person_id attributes
    - co_person_id - COmanage CoPersonId
    - created - timestamp created (TimestampMixin)
    - display_name - initially OIDC scope: profile:name
    - eppn - edu person principle name
    - fabric_id - unique FABRIC ID set at enrollment
    - id - primary key (BaseMixin)
    - oidc_claim_family_name - OIDC scope profile:family_name
    - oidc_claim_given_name - OIDC scope profile:given_name
    - oidc_claim_sub - OIDC scope openid:sub
    - org_affiliation - foreignkey link to people_organizations table
    - preferences - array of preference booleans
    - preferred_email - initially OIDC scope: email:email
    - profile - one-to-one relationship with profiles_people table
    - registered_on - timestamp user was registered on
    - uuid - unique universal identifier
    """
    fab_person = find_fabric_person_by_oidcsub_identifier(co_person_id=co_person_id)
    if fab_person:
        # set co_person_id if missing
        if not fab_person.co_person_id:
            fab_person.co_person_id = co_person_id
            db.session.commit()
        consoleLogger.info('FOUND FabricPeople: name={0}, uuid={1}'.format(fab_person.display_name, fab_person.uuid))
    else:
        now = datetime.now(timezone.utc)
        fab_person = FabricPeople()
        try:
            fab_person.co_person_id = co_person_id
            co_person = api.copeople_view_one(coperson_id=co_person_id).get('CoPeople', [])
            co_names = api.names_view_per_person(
                person_type='copersonid',
                person_id=co_person_id
            ).get('Names', [])
            for n in co_names:
                if n.get('PrimaryName', False):
                    fab_person.oidc_claim_family_name = n.get('Family', '')
                    fab_person.oidc_claim_given_name = n.get('Given', '')
                    fab_person.display_name = n.get('Given', '') + ' ' + n.get('Family', '')
            co_emails = api.email_addresses_view_per_person(
                person_type='copersonid',
                person_id=co_person_id
            ).get('EmailAddresses', [])
            for e in co_emails:
                if e.get('Type', None) == 'official':
                    fab_person.preferred_email = e.get('Mail', '')
                    break
            if co_person:
                co_person_created = datetime.strptime(co_person[0].get('Created'), "%Y-%m-%d %H:%M:%S")
                fab_person.created = co_person_created
                fab_person.registered_on = co_person_created
            else:
                fab_person.created = now
                fab_person.registered_on = now
            fab_person.updated = now - timedelta(seconds=int(
                os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')))
            fab_person.modified = now
            fab_person.uuid = uuid4()
            db.session.add(fab_person)
            db.session.commit()
            create_people_preferences(fab_person=fab_person)
            create_profile_people(fab_person=fab_person)
            update_people_identifiers(fab_person_id=fab_person.id, co_person_id=co_person_id)
            update_org_affiliation(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
            consoleLogger.info(
                'CREATE FabricPeople: name={0}, uuid={1}'.format(fab_person.display_name, fab_person.uuid))
            # metrics log - User was created:
            # 2022-09-06 19:45:56,022 User event usr:deaf-bead-deaf-bead create
            log_msg = 'User event usr:{0} create'.format(str(fab_person.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            details = 'Oops! something went wrong with create_fabric_person_from_co_person_id(): {0}'.format(exc)
            consoleLogger.error(details)

    return fab_person


def update_fabric_person(fab_person: FabricPeople = None):
    """
    Updated attributes if found to be missing or different than expected
    - bastion_login - generated from email:email and openid:sub
    - email_addresses = array of COmanage EmailAddresses
    - eppn - edu person principle name
    - fabric_id - unique FABRIC ID set at enrollment
    - modified - timestamp modified (TimestampMixin)
    - oidc_claim_email - OIDC scope email:email
    - oidc_claim_family_name - OIDC scope profile:family_name
    - oidc_claim_given_name - OIDC scope profile:given_name
    - oidc_claim_name - OIDC scope profile:name
    - oidc_claim_sub - OIDC scope openid:sub
    - org_affiliation - foreignkey link to people_organizations table
    - roles - array of fabric_roles
    - updated - timestamp user was last updated against COmanage
    """
    try:
        # update email_addresses
        update_email_addresses(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # update co_person_roles
        update_people_roles(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # update user subject identifiers
        update_user_subject_identities(fab_person=fab_person)
        # update user org affiliation
        update_user_org_affiliations(fab_person=fab_person)
        # ensure project roles are properly set
        for role in fab_person.roles:
            proj_uuid = role.name[:-3]
            if is_valid_uuid(proj_uuid):
                # validate that the person is in the project group
                fab_project = FabricProjects.query.filter_by(uuid=proj_uuid).one_or_none()
                if fab_project:
                    # add person to appropriate project role if missing
                    if role.name[-2:] == 'pc':
                        if fab_person not in fab_project.project_creators:
                            fab_project.project_creators.append(fab_person)
                    if role.name[-2:] == 'pm':
                        if fab_person not in fab_project.project_members:
                            fab_project.project_members.append(fab_person)
                    if role.name[-2:] == 'po':
                        if fab_person not in fab_project.project_owners:
                            fab_project.project_owners.append(fab_person)
                    if role.name[-2:] == 'tk':
                        if fab_person not in fab_project.token_holders:
                            fab_project.token_holders.append(fab_person)
        # check for token holders that are no longer project members
        verify_token_holder_membership(fab_person=fab_person)
        # determine if user is active
        fab_person.active = False
        for role in fab_person.roles:
            if role.name == os.getenv('COU_NAME_ACTIVE_USERS') and role.status == 'Active':
                fab_person.active = True
                break
        # set updated timestamp
        fab_person.updated = datetime.now(timezone.utc)
        # commit changes
        db.session.commit()
        # set Jupyterhub role
        fab_group = FabricGroups.query.filter_by(name=os.getenv('COU_NAME_JUPYTERHUB')).one_or_none()
        roles = [r.name for r in fab_person.roles]
        in_a_project = any([is_valid_uuid(r[:-3]) for r in roles])
        in_jupyterhub = os.getenv('COU_NAME_JUPYTERHUB') in roles
        if in_a_project and not in_jupyterhub:
            create_comanage_role(fab_person=fab_person, fab_group=fab_group)
        elif not in_a_project and in_jupyterhub:
            jupyter_role = FabricRoles.query.filter(
                FabricRoles.name == os.getenv('COU_NAME_JUPYTERHUB'),
                FabricRoles.people_id == fab_person.id
            ).one_or_none()
            if jupyter_role:
                delete_comanage_role(co_person_role_id=jupyter_role.co_person_role_id)
            else:
                details = 'Unable to remove Jupyterhub role for user: {0}'.format(fab_person.uuid)
                consoleLogger.error(details)
    except Exception as exc:
        details = 'Oops! something went wrong with update_fabric_person(): {0}'.format(exc)
        consoleLogger.error(details)


def get_people_roles_as_self(people_roles: [FabricRoles] = None) -> [object]:
    """
    Return all roles if the api_user is the user being queried
    - Global roles
    - Project roles are returned regardless of being public or private
    """
    roles = []
    for r in people_roles:
        roles.append({'name': r.name, 'description': r.description})
    roles = sorted(roles, key=lambda d: (d.get('name')).casefold())
    return roles


def get_people_roles_as_other(people_roles: [FabricRoles] = None) -> [object]:
    """
    Return partial roles if the api_user is not the user being queried
    - Global roles
    - Project roles are returned only if the project is public
    """
    roles = []
    for r in people_roles:
        if r.name[-3:] in ['-pc', '-pm', '-po', '-tk']:
            try:
                fab_project = FabricProjects.query.filter_by(uuid=r.name[0:-3]).one_or_none()
                if fab_project and fab_project.is_public:
                    roles.append({'name': r.name, 'description': r.description})
            except Exception as exc:
                print('get_people_roles_as_other - role: {0}, error: {1}'.format(r.name, exc))
        else:
            roles.append({'name': r.name, 'description': r.description})
    roles = sorted(roles, key=lambda d: (d.get('name')).casefold())
    return roles


def generate_bastion_login(fab_person: FabricPeople) -> Optional[str]:
    """
    Build a bastion login from oidc claim sub and email
    """
    if fab_person.oidc_claim_sub and fab_person.oidc_claim_email:
        oidcsub_id = str(fab_person.oidc_claim_sub).rsplit('/', 1)[1]
        prefix = fab_person.oidc_claim_email.split('@', 1)[0]
        prefix = prefix.replace('.', '_').replace('-', '_').lower()
        suffix = oidcsub_id.zfill(10)
        bastion_login = prefix[0:20] + '_' + suffix
        return bastion_login
    else:
        return None


def generate_gecos(fab_person: FabricPeople) -> str:
    """
    Produce a GECOS-formatted string based on db person info
    """
    try:
        full_name = fab_person.oidc_claim_given_name.strip() + ' ' + fab_person.oidc_claim_family_name.strip()
    except Exception as exc:
        consoleLogger.error('people.FabricPeople.gecos: full_name: {0}'.format(exc))
        full_name = 'UnknownName'
    try:
        oidc_email = fab_person.oidc_claim_email.strip()
    except Exception as exc:
        consoleLogger.error('people.FabricPeople.gecos: oidc_email: {0}'.format(exc))
        oidc_email = 'UnknownEmail'
    return ','.join([
        full_name,  # Full Name
        '',  # Building, room number
        '',  # Office telephone
        '',  # Home telephone
        oidc_email
        # external email or other contact info
    ])


def verify_token_holder_membership(fab_person: FabricPeople):
    """
    Remove user from token holders group if they no longer have a role in the project
    """
    role_names = [r.name for r in fab_person.roles]
    for role in fab_person.roles:
        if role.name.endswith('-tk'):
            project_uuid = role.name[:-3]
            p_count = sum(project_uuid in r for r in role_names)
            if p_count < 2:
                fab_project = FabricProjects.query.filter_by(uuid=project_uuid).one_or_none()
                fab_group = FabricGroups.query.filter_by(name=role.name).one_or_none()
                if fab_project and fab_group:
                    remove_project_token_holders(api_user=fab_person, fab_project=fab_project, fab_group=fab_group,
                                                 token_holders=[str(fab_person.uuid)])
