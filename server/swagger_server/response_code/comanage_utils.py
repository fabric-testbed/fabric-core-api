import logging
import os
from datetime import datetime

from comanage_api import ComanageApi

from swagger_server.database.db import db
from swagger_server.database.models.people import EmailAddresses, FabricGroups, FabricPeople, FabricRoles, Organizations

logger = logging.getLogger(__name__)

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


def create_comanage_group(name: str, description: str = None, parent_cou_id: int = None) -> int:
    try:
        if parent_cou_id:
            cou = api.cous_add(name=name, description=description, parent_id=parent_cou_id)
        else:
            cou = api.cous_add(name=name, description=description)
        if cou:
            fab_group = FabricGroups()
            fab_group.co_cou_id = cou.get('Id')
            if parent_cou_id:
                fab_group.co_parent_cou_id = parent_cou_id
            fab_group.description = description
            fab_group.name = name
            db.session.add(fab_group)
            db.session.commit()
            logger.info(
                "CREATE: entry in 'groups' table for co_cou_id: {0}".format(cou.get('Id')))
            return cou.get('Id')
        else:
            return -1
    except Exception as exc:
        details = 'Oops! something went wrong with create_comanage_group(): {0}'.format(exc)
        logger.error(details)
        return -1


def delete_comanage_group(co_cou_id: int) -> bool:
    try:
        co_cou = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
        if co_cou:
            # delete roles associated to the FABRIC group
            roles = FabricRoles.query.filter_by(co_cou_id=co_cou_id)
            for role in roles:
                delete_comanage_role(co_person_role_id=role.co_person_role_id)
            # delete COU in COmanage
            is_deleted = api.cous_delete(cou_id=co_cou_id)
            # delete group in FABRIC
            if is_deleted:
                logger.info(
                    "DELETE: entry in 'groups' table for co_cou_id: {0}".format(
                        co_cou.co_cou_id))
                FabricGroups.query.filter_by(id=co_cou.id).delete()
                db.session.commit()
            return is_deleted
    except Exception as exc:
        details = 'Oops! something went wrong with delete_comanage_group(): {0}'.format(exc)
        logger.error(details)
        return False


def update_comanage_group(co_cou_id: int, name: str = None, description: str = None, parent_cou_id: int = None) -> bool:
    try:
        fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
        if fab_group:
            # update COmanage COU
            is_updated = api.cous_edit(
                cou_id=co_cou_id,
                name=name if name else None,
                description=description if description else None,
                parent_id=parent_cou_id if parent_cou_id else None
            )
            # update FabricGroup
            if is_updated:
                if description:
                    fab_group.description = description
                if name:
                    fab_group.name = name
                if parent_cou_id:
                    fab_group.co_parent_cou_id = parent_cou_id
                db.session.commit()
            return is_updated
        else:
            return False
    except Exception as exc:
        details = 'Oops! something went wrong with update_comanage_group(): {0}'.format(exc)
        logger.error(details)
        return False


def create_comanage_role(fab_person: FabricPeople, fab_group: FabricGroups) -> bool:
    status = 'Active'
    affiliation = 'member'
    try:
        co_person_role = api.coperson_roles_add(
            coperson_id=fab_person.co_person_id, cou_id=fab_group.co_cou_id, status=status, affiliation=affiliation)
        if co_person_role:
            fab_role = FabricRoles()
            fab_role.affiliation = affiliation
            fab_role.co_cou_id = fab_group.co_cou_id
            fab_role.co_person_id = fab_person.co_person_id
            fab_role.co_person_role_id = co_person_role.get('Id')
            fab_role.name = fab_group.name
            fab_role.description = fab_group.description
            fab_role.people_id = fab_person.id
            fab_role.status = status
            db.session.add(fab_role)
            db.session.commit()
            logger.info(
                "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role.get('Id')))
            return True
    except Exception as exc:
        details = 'Oops! something went wrong with create_comanage_role(): {0}'.format(exc)
        logger.error(details)
        return False


def delete_comanage_role(co_person_role_id: int) -> bool:
    try:
        co_person_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
        if co_person_role:
            # delete co_person_role in COmanage
            is_deleted = api.coperson_roles_delete(coperson_role_id=co_person_role_id)
            # delete co_person_role in FABRIC
            if is_deleted:
                logger.info(
                    "DELETE: entry in 'roles' table for co_person_role_id: {0}".format(
                        co_person_role.co_person_role_id))
                FabricRoles.query.filter_by(id=co_person_role.id).delete()
                db.session.commit()
            return is_deleted
    except Exception as exc:
        details = 'Oops! something went wrong with delete_comanage_role(): {0}'.format(exc)
        logger.error(details)
        return False


def update_people_identifiers(fab_person_id: int, co_person_id: int) -> None:
    try:
        fab_person = FabricPeople.query.filter_by(id=fab_person_id).one_or_none()
        co_identifiers = api.identifiers_view_per_entity(
            entity_type='copersonid', entity_id=co_person_id).get('Identifiers', [])
        for ident in co_identifiers:
            if ident.get('Type', None) == 'eppn':
                fab_person.eppn = ident.get('Identifier', '')
            if ident.get('Type', None) == os.getenv('CORE_API_CO_USER_IDENTIFIER', 'fabricid'):
                fab_person.fabric_id = ident.get('Identifier', '')
            if ident.get('Type', None) == 'oidcsub':
                fab_person.oidc_claim_sub = ident.get('Identifier', '')
        db.session.commit()
    except Exception as exc:
        details = 'Oops! something went wrong with update_people_identifiers(): {0}'.format(exc)
        logger.error(details)


def update_org_affiliation(fab_person_id: int, co_person_id: int) -> None:
    try:
        fab_person = FabricPeople.query.filter_by(id=fab_person_id).one_or_none()
        co_orgidentity_links = api.coorg_identity_links_view_by_identity(
            identity_type='copersonid',
            identity_id=co_person_id
        ).get('CoOrgIdentityLinks', [])
        for org_link in co_orgidentity_links:
            org = Organizations.query.filter_by(org_identity_id=org_link.get('OrgIdentityId')).one_or_none()
            if org:
                fab_person.org_affiliation = org.id
                db.session.commit()
    except Exception as exc:
        details = 'Oops! something went wrong with update_people_identifiers(): {0}'.format(exc)
        logger.error(details)


def update_people_roles(fab_person_id: int, co_person_id: int) -> None:
    """
    CoPersonRoles - from COmanage
    - affiliation - role affiliation type
    - co_cou_id - COmanage COU Id
    - co_person_id - CoPerson Id
    - co_person_role_id - CoPersonRoles Id
    - name - COU name
    - description - COU description
    - people_id - foreignkey link to people table
    - status - role status
    """
    try:
        co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id).get('CoPersonRoles', [])
        for co_role in co_roles:
            co_person_role_id = co_role.get('Id', None)
            co_cou_id = co_role.get('CouId')
            fab_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
            fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
            if fab_group:
                if not fab_role:
                    fab_role = FabricRoles()
                    fab_role.affiliation = co_role.get('Affiliation', 'member')
                    fab_role.co_cou_id = co_cou_id
                    fab_role.co_person_id = co_person_id
                    fab_role.co_person_role_id = co_person_role_id
                    fab_role.name = fab_group.name
                    fab_role.description = fab_group.description
                    fab_role.people_id = fab_person_id
                    fab_role.status = co_role.get('Status', 'Pending')
                    db.session.add(fab_role)
                    db.session.commit()
                    logger.info(
                        "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                else:
                    fab_role.affiliation = co_role.get('Affiliation', 'member')
                    fab_role.name = fab_group.name
                    fab_role.description = fab_group.description
                    fab_role.status = co_role.get('Status', 'Pending')
                    db.session.commit()
                    logger.info(
                        "UPDATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                    if fab_role.status == 'Deleted':
                        logger.info(
                            "DELETE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                        FabricRoles.query.filter_by(id=fab_role.id).delete()
                        db.session.commit()
            else:
                logger.warning(
                    "ERROR: unable to locate co_cou_id {0} in the 'groups' table".format(co_cou_id))
    except Exception as exc:
        details = 'Oops! something went wrong with update_people_roles(): {0}'.format(exc)
        logger.error(details)


def update_email_addresses(fab_person_id: int, co_person_id: int) -> None:
    """
    EmailAddresses - from COmanage
    - co_email_address_id - EmailAddress Id as integer in COmanage
    - email - email address as string
    - people_id - foreignkey link to people table
    - type - type of email address as string
    """
    try:
        co_email_addresses = api.email_addresses_view_per_person(
            person_type='copersonid', person_id=co_person_id).get('EmailAddresses', [])
        for co_email in co_email_addresses:
            fab_email = EmailAddresses.query.filter_by(
                co_email_address_id=co_email.get('Id')
            ).one_or_none()
            if not fab_email:
                fab_email = EmailAddresses()
                fab_email.co_email_address_id = co_email.get('Id')
                fab_email.email = co_email.get('Mail')
                fab_email.people_id = fab_person_id
                fab_email.type = co_email.get('Type')
                db.session.add(fab_email)
                db.session.commit()
                logger.info(
                    'CREATE EmailAddress: email={0}, fab_person_id={1}'.format(fab_email.email, fab_email.people_id))
            else:
                fab_email.email = co_email.get('Mail')
                fab_email.type = co_email.get('Type')
                db.session.commit()
                logger.info(
                    'UPDATE EmailAddress: email={0}, fab_person_id={1}'.format(fab_email.email, fab_email.people_id))
    except Exception as exc:
        details = 'Oops! something went wrong with update_email_addresses(): {0}'.format(exc)
        logger.error(details)


def update_groups():
    """
    Cous - from COmanage
    - co_cou_id - Cous Id
    - co_parent_cou_id - Cous Parent Id
    - deleted - COU status (false == active)
    - description - COU description
    - name - COU name
    """
    try:
        cous = api.cous_view_per_co().get('Cous', [])
        for co_cou in cous:
            co_cou_id = co_cou.get('Id')
            fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
            if not fab_group:
                fab_group = FabricGroups()
                fab_group.co_cou_id = co_cou_id
                fab_group.co_parent_cou_id = co_cou.get('ParentId', None)
                fab_group.created = datetime.strptime(co_cou.get('Created'), '%Y-%m-%d %H:%M:%S')
                fab_group.deleted = co_cou.get('Deleted')
                fab_group.description = co_cou.get('Description')
                fab_group.name = co_cou.get('Name')
                db.session.add(fab_group)
                db.session.commit()
                logger.info("CREATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
            else:
                fab_group.co_parent_cou_id = co_cou.get('ParentId', None)
                fab_group.deleted = co_cou.get('Deleted')
                fab_group.description = co_cou.get('Description')
                fab_group.name = co_cou.get('Name')
                db.session.commit()
                logger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
                if fab_group.deleted:
                    logger.info("DELETE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
                    FabricGroups.query.filter_by(id=fab_group.id).delete()
                    db.session.commit()
    except Exception as exc:
        details = 'Oops! something went wrong with update_groups(): {0}'.format(exc)
        logger.error(details)


def update_organizations() -> None:
    """
    OrgIdentities - from COmanage
    - affiliation - type of affiliation
    - org_identitiy_id - COmanage Id
    - organization - name
    """
    try:
        co_orgs = api.org_identities_view_per_co().get('OrgIdentities', [])
        for org in co_orgs:
            org_identity_id = org.get('Id', None)
            organization = org.get('O', None)
            affiliation = org.get('Affiliation', None)
            if org_identity_id and organization and affiliation and not org.get('Deleted'):
                fab_org = Organizations.query.filter_by(org_identity_id=org_identity_id).one_or_none()
                if not fab_org:
                    logger.info(
                        "CREATE: entry in 'organizations' table for org_identity_id: {0}".format(org_identity_id))
                    fab_org = Organizations()
                    fab_org.org_identity_id = org_identity_id
                    fab_org.organization = organization
                    fab_org.affiliation = affiliation
                    db.session.add(fab_org)
                    db.session.commit()
    except Exception as exc:
        details = 'Oops! something went wrong with update_organizations(): {0}'.format(exc)
        logger.error(details)
