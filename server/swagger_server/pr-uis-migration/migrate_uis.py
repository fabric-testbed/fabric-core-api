"""
migrate UIS people and sshkey data to core-api

People (match by oidc_claim_sub)
- uuid: update core-api to match UIS value
- registered_on: update core-api to match UIS value

SshKeys (match by person_uuid)
- ADD sshkey if fingerprint for key from UIS does not exist in core-api

"""
import json
import logging
from datetime import datetime

from swagger_server.__main__ import app, db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.sshkeys import FabricSshKeys

logger = logging.getLogger(__name__)
app.app_context().push()

# load uis_people.py and uis_sshkeys.py
uis_people_file = 'data/uis_people.json'
uis_sshkeys_file = 'data/uis_sshkeys.json'

with open(uis_people_file, "r") as f:
    f_dict = json.load(f)
    uis_people = f_dict.get('uis_people', None)

with open(uis_sshkeys_file, "r") as f:
    f_dict = json.load(f)
    uis_sshkeys = f_dict.get('uis_sshkeys', None)


def date_parser(text) -> datetime:
    # format: 2022-05-11 17:19:00+00:00 or 2021-09-10 21:03:22.730968+00:00
    for fmt in ["%Y-%m-%d %H:%M:%S%z", "%Y-%m-%d %H:%M:%S.%f%z"]:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    raise ValueError('No valid date format found')


# update fab_person from UIS
def update_person_from_uis(fab_person: FabricPeople, uis_person: dict):
    """
    OIDC Claims, COmanage Registry attributes and external table links (* denotes required)
    - * active - account status
    - bastion_login - generated from email:email and openid:sub
    - co_person_id - COmanage CoPersonId
    - created - timestamp created (TimestampMixin)
    - * display_name - initially OIDC scope: profile:name
    - email_addresses = array of COmanage EmailAddresses
    - eppn - edu person principle name
    - fabric_id - unique FABRIC ID set at enrollment
    - id - primary key (BaseMixin)
    - modified - timestamp modified (TimestampMixin)
    - oidc_claim_email - OIDC scope email:email
    - oidc_claim_family_name - OIDC scope profile:family_name
    - oidc_claim_given_name - OIDC scope profile:given_name
    - oidc_claim_name - OIDC scope profile:name
    - oidc_claim_sub - OIDC scope openid:sub
    - org_affiliation - foreignkey link to people_organizations table
    - preferences - array of preference booleans
    - * preferred_email - initially OIDC scope: email:email
    - profile - one-to-one relationship with profiles_people table
    - publications - array of publications
    - registered_on - timestamp user was registered on
    - roles - array of fabric_roles
    - sshkeys - array of sshkeys
    - updated - timestamp user was last updated against COmanage
    - * uuid - unique universal identifier
    """
    # update uuid
    logger.info('- uuid: {0} --> {1}'.format(str(fab_person.uuid), uis_p.get('uuid')))
    fab_person.uuid = uis_person.get('uuid')
    db.session.commit()
    # update registered_on
    logger.info('- registered_on: {0} --> {1}'.format(str(fab_person.registered_on), uis_person.get('registered_on')))
    fab_person.registered_on = date_parser(uis_person.get('registered_on'))
    db.session.commit()
    # update sshkeys
    add_sshkey_to_person(fab_person=fab_person, uis_person=uis_person)


# add sshkeys to people in fabric-core-api
def add_sshkey_to_person(fab_person: FabricPeople, uis_person: dict):
    """
    SshKeys - Bastion and Sliver keys (* denotes required)
    - comment:
    - * created - timestamp created (TimestampMixin)
    - #created_on:
    - deactivated_on:
    - deactivation_reason:
    - description:
    - * expires_on:
    - * fabric_key_type: [bastion, sliver]
    - fingerprint:
    - * id - primary key (BaseMixin)
    - key_uuid:
    - modified - timestamp modified (TimestampMixin)
    - * people_id - foreignkey link to people table
    - public_key:
    - public_openssh:
    - * ssh_key_type:
    - * status: [active, deactivated, expired]
    - * uuid - unique universal identifier
    """
    sshkeys = [cdict for cdict in uis_sshkeys if cdict['owner_uuid'] == uis_person.get('uuid')]
    if sshkeys:
        for sshkey in sshkeys:
            # check for duplicate key
            if sshkey.get('fingerprint') in [k.fingerprint for k in fab_person.sshkeys]:
                logger.info('- sshkeys: DUPLICATE {0}'.format(sshkey.get('fingerprint')))
            # create new fabric key object
            else:
                fab_sshkey = FabricSshKeys()
                fab_sshkey.comment = sshkey.get('comment')
                fab_sshkey.created = date_parser(sshkey.get('created_on'))
                fab_sshkey.description = sshkey.get('description')
                fab_sshkey.expires_on = date_parser(sshkey.get('expires_on'))
                fab_sshkey.fabric_key_type = sshkey.get('fabric_key_type')
                fab_sshkey.fingerprint = sshkey.get('fingerprint')
                fab_sshkey.people_id = fab_person.id
                fab_sshkey.public_key = sshkey.get('public_key')
                fab_sshkey.ssh_key_type = sshkey.get('ssh_key_type')
                fab_sshkey.uuid = sshkey.get('key_uuid')
                db.session.add(fab_sshkey)
                db.session.commit()
                logger.info('- sshkeys: ADD {0}'.format(sshkey.get('key_uuid')))


# migrate UIS data to core-api
for uis_p in uis_people:
    person = FabricPeople.query.filter_by(oidc_claim_sub=uis_p.get('oidc_claim_sub')).first()
    if person:
        logger.info('FOUND: {0}'.format(uis_p.get('oidc_claim_sub')))
        update_person_from_uis(fab_person=person, uis_person=uis_p)
    else:
        logger.warning('NOT FOUND: {0}'.format(uis_p.get('oidc_claim_sub')))
