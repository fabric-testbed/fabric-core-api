import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople, FabricRoles
from swagger_server.database.models.projects import FabricProjects
from swagger_server.response_code.comanage_utils import api, update_email_addresses, update_org_affiliation, \
    update_people_identifiers, update_people_roles
from swagger_server.response_code.preferences_utils import create_people_preferences
from swagger_server.response_code.profiles_utils import create_profile_people
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims


def get_person_by_login_claims() -> FabricPeople:
    try:
        claims = vouch_get_custom_claims()
        fab_person = FabricPeople.query.filter(
            FabricPeople.oidc_claim_sub == str(claims.get('sub'))
        ).one_or_none()
        if not fab_person:
            fab_person = create_fabric_person_from_login(claims=claims)
    except Exception as exc:
        details = 'Oops! something went wrong with get_person_by_login_claims(): {0}'.format(exc)
        consoleLogger.error(details)
        fab_person = FabricPeople()

    return fab_person


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
        if claims.get('given_name') and claims.get('family_name') and claims.get('email'):
            co_person = api.copeople_match(
                given=claims.get('given'),
                family=claims.get('family'),
                mail=claims.get('email')).get('CoPeople', [])
            if co_person:
                fab_person = create_fabric_person_from_co_person_id(co_person_id=co_person[0].get('Id'))
                fab_person.oidc_claim_email = claims.get('email')
                fab_person.oidc_claim_family_name = claims.get('family_name')
                fab_person.oidc_claim_given_name = claims.get('given_name')
                fab_person.oidc_claim_name = claims.get('name')
                fab_person.oidc_claim_sub = claims.get('sub')
                fab_person.preferred_email = claims.get('email')
                fab_person.updated = datetime.now(timezone.utc) - timedelta(seconds=int(
                    os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')))
                db.session.commit()
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
                fab_person.created = datetime.now(timezone.utc)
                fab_person.registered_on = datetime.now(timezone.utc)
            fab_person.updated = datetime.now(timezone.utc) - timedelta(seconds=int(
                os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')))
            fab_person.uuid = uuid4()
            db.session.add(fab_person)
            db.session.commit()
            create_people_preferences(fab_person=fab_person)
            create_profile_people(fab_person=fab_person)
            update_people_identifiers(fab_person_id=fab_person.id, co_person_id=co_person_id)
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
        # check co_person_id
        if not fab_person.co_person_id:
            co_person = api.copeople_match(
                mail=fab_person.oidc_claim_email
            ).get('CoPeople', [])
            if len(co_person) == 1:
                fab_person.co_person_id = co_person[0].get('Id')
                db.session.commit()
        # check email_addresses
        update_email_addresses(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # check co_person_roles
        update_people_roles(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # check identifiers
        update_people_identifiers(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # check org affiliation
        update_org_affiliation(fab_person_id=fab_person.id, co_person_id=fab_person.co_person_id)
        # check claims and bastion_login
        claims = vouch_get_custom_claims()
        if claims.get('sub'):
            fab_person.bastion_login = fab_person.bastion_login()
            fab_person.oidc_claim_email = claims.get('email')
            fab_person.oidc_claim_family_name = claims.get('family_name')
            fab_person.oidc_claim_given_name = claims.get('given_name')
            fab_person.oidc_claim_name = claims.get('name')
            fab_person.oidc_claim_sub = claims.get('sub')
        # determine if active
        fab_person.active = False
        for role in fab_person.roles:
            if role.name == os.getenv('COU_NAME_ACTIVE_USERS') and role.status == 'Active':
                fab_person.active = True
                break
        # set updated
        fab_person.updated = datetime.now(timezone.utc)
        # commit changes
        db.session.commit()
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
        if r.name[-3:] in ['-pc', '-pm', '-po']:
            fab_project = FabricProjects.query.filter_by(uuid=r.name[0:-3]).one_or_none()
            if fab_project.is_public:
                roles.append({'name': r.name, 'description': r.description})
        else:
            roles.append({'name': r.name, 'description': r.description})
    roles = sorted(roles, key=lambda d: (d.get('name')).casefold())
    return roles
