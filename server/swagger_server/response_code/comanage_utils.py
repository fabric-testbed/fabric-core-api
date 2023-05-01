import os
from datetime import datetime

from comanage_api import ComanageApi

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import EmailAddresses, FabricGroups, FabricPeople, FabricRoles, \
    Organizations, UserOrgAffiliations, UserSubjectIdentifiers
from swagger_server.response_code.response_utils import array_difference

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
            consoleLogger.info(
                "CREATE: entry in 'groups' table for co_cou_id: {0}".format(cou.get('Id')))
            return cou.get('Id')
        else:
            return -1
    except Exception as exc:
        details = 'Oops! something went wrong with create_comanage_group(): {0}'.format(exc)
        consoleLogger.error(details)
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
                consoleLogger.info(
                    "DELETE: entry in 'groups' table for co_cou_id: {0}".format(
                        co_cou.co_cou_id))
                FabricGroups.query.filter_by(id=co_cou.id).delete()
                db.session.commit()
            return is_deleted
    except Exception as exc:
        details = 'Oops! something went wrong with delete_comanage_group(): {0}'.format(exc)
        consoleLogger.error(details)
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
        consoleLogger.error(details)
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
            try:
                db.session.add(fab_role)
                db.session.commit()
                consoleLogger.info(
                    "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role.get('Id')))
            except Exception as exc:
                consoleLogger.error('DUPLICATE ROLE: {0}'.format(exc))
                db.session.rollback()
                return False

            return True
    except Exception as exc:
        details = 'Oops! something went wrong with create_comanage_role(): {0}'.format(exc)
        consoleLogger.error(details)
        return False


def delete_comanage_role(co_person_role_id: int) -> bool:
    try:
        co_person_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
        if co_person_role:
            # delete co_person_role in COmanage
            is_deleted = api.coperson_roles_delete(coperson_role_id=co_person_role_id)
            # delete co_person_role in FABRIC
            if is_deleted:
                consoleLogger.info(
                    "DELETE: entry in 'roles' table for co_person_role_id: {0}".format(
                        co_person_role.co_person_role_id))
                FabricRoles.query.filter_by(id=co_person_role.id).delete()
                db.session.commit()
            return is_deleted
    except Exception as exc:
        details = 'Oops! something went wrong with delete_comanage_role(): {0}'.format(exc)
        consoleLogger.error(details)
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
        consoleLogger.error(details)


def update_org_affiliation(fab_person_id: int, co_person_id: int) -> None:
    try:
        fab_person = FabricPeople.query.filter_by(id=fab_person_id).one_or_none()
        co_orgidentity_links = api.coorg_identity_links_view_by_identity(
            identity_type='copersonid',
            identity_id=co_person_id
        ).get('CoOrgIdentityLinks', [])
        for org_link in co_orgidentity_links:
            org_identity_id = org_link.get('OrgIdentityId')
            fab_org = Organizations.query.filter_by(org_identity_id=org_identity_id).one_or_none()
            if not fab_org:
                org_identity = api.org_identities_view_one(org_identity_id=org_identity_id).get('OrgIdentities', [])
                for oi in org_identity:
                    organization = oi.get('O', None)
                    affiliation = oi.get('Affiliation', None)
                    if org_identity_id and organization and affiliation and not oi.get('Deleted'):
                        try:
                            fab_org = Organizations()
                            fab_org.org_identity_id = org_identity_id
                            fab_org.organization = organization
                            fab_org.affiliation = affiliation
                            db.session.add(fab_org)
                            db.session.commit()
                            fab_person.org_affiliation = fab_org.id
                            db.session.commit()
                            consoleLogger.info(
                                "CREATE: entry in 'organizations' table for org_identity_id: {0}".format(
                                    oi.get('Id', None)))
                        except Exception as exc:
                            consoleLogger.error(exc)
                            continue
                    else:
                        consoleLogger.warning('[NEEDS REVIEW] org_identity_id = {0}'.format(org_identity_id))
            else:
                fab_person.org_affiliation = fab_org.id
                db.session.commit()

    except Exception as exc:
        details = 'Oops! something went wrong with update_org_affiliation(): {0}'.format(exc)
        consoleLogger.error(details)


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
        fab_person = FabricPeople.query.filter_by(id=fab_person_id).one_or_none()
        co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id).get('CoPersonRoles', [])
        fab_roles = fab_person.roles
        co_role_ids = [r.get('Id') for r in co_roles]
        fab_role_ids = [str(r.co_person_role_id) for r in fab_roles]
        roles_added = array_difference(co_role_ids, fab_role_ids)
        roles_removed = array_difference(fab_role_ids, co_role_ids)
        # remove old Fabric roles
        for role_id in roles_removed:
            fab_role = FabricRoles.query.filter_by(co_person_role_id=int(role_id)).one_or_none()
            if fab_role:
                consoleLogger.info("DELETE: entry in 'roles' table for fabric_role_id: {0}".format(fab_role.id))
                FabricRoles.query.filter_by(id=fab_role.id).delete()
                db.session.commit()
        # add new COmanage roles
        for co_role in co_roles:
            co_person_role_id = co_role.get('Id', None)
            co_cou_id = co_role.get('CouId')
            fab_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
            fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
            if fab_group:
                if not fab_role:
                    if co_person_role_id in roles_added and str(co_role.get('Status')).casefold() == 'active':
                        fab_role = FabricRoles()
                        fab_role.affiliation = co_role.get('Affiliation', 'member')
                        fab_role.co_cou_id = co_cou_id
                        fab_role.co_person_id = co_person_id
                        fab_role.co_person_role_id = co_person_role_id
                        fab_role.name = fab_group.name
                        fab_role.description = fab_group.description
                        fab_role.people_id = fab_person_id
                        fab_role.status = co_role.get('Status')
                        try:
                            db.session.add(fab_role)
                            db.session.commit()
                            consoleLogger.info(
                                "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                        except Exception as exc:
                            consoleLogger.error('DUPLICATE ROLE: {0}'.format(exc))
                            db.session.rollback()
                            continue
                        # metrics log - User role added:
                        # 2022-09-06 19:45:56,022 User event usr:dead-beef-dead-beef modify-add role ROLE
                        log_msg = 'User event usr:{0} modify-add role \'{1}\''.format(
                            str(fab_person.uuid),
                            fab_role.name)
                        metricsLogger.info(log_msg)
                else:
                    fab_role.affiliation = co_role.get('Affiliation', 'member')
                    fab_role.name = fab_group.name
                    fab_role.description = fab_group.description
                    fab_role.status = co_role.get('Status', 'Pending')
                    db.session.commit()
                    consoleLogger.info(
                        "UPDATE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                    if fab_role.status == 'Deleted':
                        consoleLogger.info(
                            "DELETE: entry in 'roles' table for co_person_role_id: {0}".format(co_person_role_id))
                        # metrics log - User role removed:
                        # 2022-09-06 19:45:56,022 User event usr:dead-beef-dead-beef modify-remove role ROLE
                        log_msg = 'User event usr:{0} modify-remove role \'{1}\''.format(
                            str(fab_person.uuid),
                            fab_role.name)
                        metricsLogger.info(log_msg)
                        FabricRoles.query.filter_by(id=fab_role.id).delete()
                        db.session.commit()
            else:
                consoleLogger.warning(
                    "ERROR: unable to locate co_cou_id {0} in the 'groups' table".format(co_cou_id))
    except Exception as exc:
        details = 'Oops! something went wrong with update_people_roles(): {0}'.format(exc)
        consoleLogger.error(details)


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
                consoleLogger.info(
                    'CREATE EmailAddress: email={0}, fab_person_id={1}'.format(fab_email.email, fab_email.people_id))
            else:
                fab_email.email = co_email.get('Mail')
                fab_email.type = co_email.get('Type')
                db.session.commit()
                consoleLogger.info(
                    'UPDATE EmailAddress: email={0}, fab_person_id={1}'.format(fab_email.email, fab_email.people_id))
    except Exception as exc:
        details = 'Oops! something went wrong with update_email_addresses(): {0}'.format(exc)
        consoleLogger.error(details)


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
                consoleLogger.info("CREATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
            else:
                fab_group.co_parent_cou_id = co_cou.get('ParentId', None)
                fab_group.deleted = co_cou.get('Deleted')
                fab_group.description = co_cou.get('Description')
                fab_group.name = co_cou.get('Name')
                db.session.commit()
                consoleLogger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
                if fab_group.deleted:
                    consoleLogger.info("DELETE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
                    FabricGroups.query.filter_by(id=fab_group.id).delete()
                    db.session.commit()
    except Exception as exc:
        details = 'Oops! something went wrong with update_groups(): {0}'.format(exc)
        consoleLogger.error(details)


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
                    consoleLogger.info(
                        "CREATE: entry in 'organizations' table for org_identity_id: {0}".format(org_identity_id))
                    fab_org = Organizations()
                    fab_org.org_identity_id = org_identity_id
                    fab_org.organization = organization
                    fab_org.affiliation = affiliation
                    db.session.add(fab_org)
                    db.session.commit()
                else:
                    consoleLogger.info(
                        "FOUND: entry in 'organizations' table for org_identity_id: {0}".format(org_identity_id))
    except Exception as exc:
        details = 'Oops! something went wrong with update_organizations(): {0}'.format(exc)
        consoleLogger.error(details)


def update_user_subject_identities(fab_person: FabricPeople):
    try:
        entity_identifiers = api.identifiers_view_per_entity(
            entity_type='copersonid',
            entity_id=fab_person.co_person_id
        ).get('Identifiers', [])
        sub_new = []
        for i in entity_identifiers:
            if i.get('Type') == 'oidcsub':
                sub_new.append(i.get('Identifier'))

        sub_orig = [p.sub for p in fab_person.user_sub_identities]
        sub_add = array_difference(sub_new, sub_orig)
        sub_remove = array_difference(sub_orig, sub_new)
        # add user subject identities
        for sub in sub_add:
            fab_sub = UserSubjectIdentifiers.query.filter(
                UserSubjectIdentifiers.people_id == fab_person.id, UserSubjectIdentifiers.sub == sub).one_or_none()
            if not fab_sub:
                fab_sub = UserSubjectIdentifiers()
                fab_sub.people_id = fab_person.id
                fab_sub.sub = sub
                fab_person.user_sub_identities.append(fab_sub)
                db.session.commit()
                # metrics log - People sub added:
                # 2022-09-06 19:45:56,022 People event usr:dead-beef-dead-beef modify-add sub <sub> by usr:fead-beaf-fead-beaf
                log_msg = 'People event usr:{0} modify-add sub \'{1}\' by usr:{2}'.format(str(fab_person.uuid), sub,
                                                                                          str(fab_person.uuid))
                metricsLogger.info(log_msg)
        # remove user subject identities
        for sub in sub_remove:
            fab_sub = UserSubjectIdentifiers.query.filter(
                UserSubjectIdentifiers.people_id == fab_person.id, UserSubjectIdentifiers.sub == sub).one_or_none()
            if fab_sub:
                fab_person.user_sub_identities.remove(fab_sub)
                db.session.delete(fab_sub)
                db.session.commit()
                # metrics log - People sub removed:
                # 2022-09-06 19:45:56,022 People event usr:dead-beef-dead-beef modify-remove sub <sub> by usr:fead-beaf-fead-beaf
                log_msg = 'People event usr:{0} modify-remove sub \'{1}\' by usr:{2}'.format(str(fab_person.uuid), sub,
                                                                                             str(fab_person.uuid))
                metricsLogger.info(log_msg)
    except Exception as exc:
        details = 'Oops! something went wrong with update_user_subject_identities(): {0}'.format(exc)
        consoleLogger.error(details)


def update_user_org_affiliations(fab_person: FabricPeople):
    try:
        co_orgidentity_links = api.coorg_identity_links_view_by_identity(
            identity_type='copersonid',
            identity_id=fab_person.co_person_id
        ).get('CoOrgIdentityLinks', [])
        org_new = []
        for org_link in co_orgidentity_links:
            org_identity_id = org_link.get('OrgIdentityId')
            fab_org = Organizations.query.filter_by(org_identity_id=org_identity_id).one_or_none()
            if not fab_org:
                org_identity = api.org_identities_view_one(org_identity_id=org_identity_id).get('OrgIdentities', [])
                for oi in org_identity:
                    organization = oi.get('O', None)
                    affiliation = oi.get('Affiliation', None)
                    if org_identity_id and organization and affiliation and not oi.get('Deleted'):
                        try:
                            fab_org = Organizations()
                            fab_org.org_identity_id = org_identity_id
                            fab_org.organization = organization
                            fab_org.affiliation = affiliation
                            db.session.add(fab_org)
                            db.session.commit()
                            consoleLogger.info(
                                "CREATE: entry in 'organizations' table for org_identity_id: {0}".format(
                                    oi.get('Id', None)))
                            org_new.append(fab_org.organization)
                        except Exception as exc:
                            consoleLogger.error(exc)
                            continue
                    else:
                        consoleLogger.warning('[NEEDS REVIEW] org_identity_id = {0}'.format(org_identity_id))
            else:
                org_new.append(fab_org.organization)
        org_orig = [p.affiliation for p in fab_person.user_org_affiliations]
        org_add = array_difference(org_new, org_orig)
        org_remove = array_difference(org_orig, org_new)
        # add user subject identities
        for org in org_add:
            fab_org = UserOrgAffiliations.query.filter(
                UserOrgAffiliations.people_id == fab_person.id, UserOrgAffiliations.affiliation == org).one_or_none()
            if not fab_org:
                fab_org = UserOrgAffiliations()
                fab_org.people_id = fab_person.id
                fab_org.affiliation = org
                fab_person.user_org_affiliations.append(fab_org)
                db.session.commit()
                # metrics log - People affiliation added:
                # 2022-09-06 19:45:56,022 People event usr:dead-beef-dead-beef modify-add affiliation <sub> by usr:fead-beaf-fead-beaf
                log_msg = 'People event usr:{0} modify-add affiliation \'{1}\' by usr:{2}'.format(str(fab_person.uuid),
                                                                                                  org,
                                                                                                  str(fab_person.uuid))
                metricsLogger.info(log_msg)
        # remove user subject identities
        for org in org_remove:
            fab_org = UserOrgAffiliations.query.filter(
                UserOrgAffiliations.people_id == fab_person.id, UserOrgAffiliations.affiliation == org).one_or_none()
            if fab_org:
                fab_person.user_org_affiliations.remove(fab_org)
                db.session.delete(fab_org)
                db.session.commit()
                # metrics log - People affiliation removed:
                # 2022-09-06 19:45:56,022 People event usr:dead-beef-dead-beef modify-remove affiliation <sub> by usr:fead-beaf-fead-beaf
                log_msg = 'People event usr:{0} modify-remove affiliation \'{1}\' by usr:{2}'.format(
                    str(fab_person.uuid), org,
                    str(fab_person.uuid))
                metricsLogger.info(log_msg)
    except Exception as exc:
        details = 'Oops! something went wrong with update_user_subject_identities(): {0}'.format(exc)
        consoleLogger.error(details)
