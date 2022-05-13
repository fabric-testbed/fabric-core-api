import os
import logging
from uuid import uuid4
from swagger_server.database.db import db
from collections import defaultdict
import re
from datetime import datetime, timedelta, timezone
from swagger_server.models.sshkey_pair import SshkeyPairResults
from swagger_server.models.sshkeys_one import SshkeysOne
from fss_utils.sshkey import FABRICSSHKey
from swagger_server.models.sshkeys_post import SshkeysPost
from swagger_server.database.models.people import FabricPeople
from swagger_server.response_code.cors_response import cors_500
from swagger_server.database.models.sshkeys import FabricSshKeys, EnumSshKeyTypes, EnumSshKeyStatus

logger = logging.getLogger(__name__)

# constants
TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"
DESCRIPTION_REGEX = r"^[\w\s\-'\.@_()/]{5,255}$"
COMMENT_LENGTH = 100


def create_ssh_key(body: SshkeysPost, fab_person: FabricPeople) -> SshkeyPairResults:
    """
    comment = db.Column(db.String())
    deactivated_on = db.Column(db.DateTime(timezone=True), nullable=True)
    deactivated_reason = db.Column(db.String())
    description = db.Column(db.String())
    expires_on = db.Column(db.DateTime(timezone=True), nullable=False)
    fabric_key_type = db.Column(db.Enum(EnumSshKeyTypes), default=EnumSshKeyTypes.sliver, nullable=False)
    fingerprint = db.Column(db.String())
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    public_key = db.Column(db.String())
    ssk_key_type = db.Column(db.Enum(EnumSshKeyTypes), default=EnumSshKeyTypes.sliver, nullable=False)
    status = db.Column(db.Enum(EnumSshKeyStatus), default=EnumSshKeyStatus.active, nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    logger.info("Generating key of type '{0}' for '{1}' with comment '{2}'".format(
        body.keytype, fab_person.display_name, body.comment))
    try:
        sshkey = FABRICSSHKey.generate(body.comment, os.getenv('SSH_KEY_ALGORITHM'))
        response = SshkeyPairResults()
        if sshkey:
            fab_sshkey = FabricSshKeys()
            fab_sshkey.comment = body.comment
            fab_sshkey.description = body.description
            if body.keytype == EnumSshKeyTypes.sliver.name:
                fab_sshkey.expires_on = datetime.now(timezone.utc) + \
                                        timedelta(days=float(os.getenv('SSH_SLIVER_KEY_VALIDITY_DAYS')))
                fab_sshkey.fabric_key_type = EnumSshKeyTypes.sliver
            else:
                fab_sshkey.expires_on = datetime.now(timezone.utc) + \
                                        timedelta(days=float(os.getenv('SSH_BASTION_KEY_VALIDITY_DAYS')))
                fab_sshkey.fabric_key_type = EnumSshKeyTypes.bastion
            fab_sshkey.fingerprint = sshkey.get_fingerprint()
            fab_sshkey.people_id = fab_person.id
            fab_sshkey.public_key = sshkey.as_keypair()[1]
            fab_sshkey.ssh_key_type = sshkey.name
            fab_sshkey.status = EnumSshKeyStatus.active
            fab_sshkey.uuid = uuid4()
            db.session.add(fab_sshkey)
            db.session.commit()
            # add sshkey to Fabric Person
            fab_person.sshkeys.append(fab_sshkey)
            db.session.commit()
            response.private_openssh = sshkey.as_keypair()[0]
            response.public_openssh = sshkey.as_keypair()[1]
        return response
    except Exception as exc:
        details = 'Oops! something went wrong with create_ssh_key(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


def sshkey_from_fab_sshkey(fab_sshkey: FabricSshKeys) -> SshkeysOne:
    sshkey = SshkeysOne()
    sshkey.comment = fab_sshkey.comment
    sshkey.created_on = str(fab_sshkey.created)
    sshkey.deactivated_on = str(fab_sshkey.deactivated_on) if fab_sshkey.deactivated_on else None
    sshkey.deactivated_reason = fab_sshkey.deactivated_reason
    sshkey.description = fab_sshkey.description
    sshkey.expires_on = str(fab_sshkey.expires_on)
    sshkey.fabric_key_type = fab_sshkey.fabric_key_type.name
    sshkey.fingerprint = fab_sshkey.fingerprint
    sshkey.public_key = fab_sshkey.public_key
    sshkey.ssh_key_type = fab_sshkey.ssh_key_type
    sshkey.uuid = fab_sshkey.uuid
    return sshkey


def sshkeys_from_fab_person(fab_person: FabricPeople) -> [SshkeysOne]:
    sshkeys = []
    for k in fab_person.sshkeys:
        sshkey = SshkeysOne()
        sshkey.comment = k.comment
        sshkey.created_on = str(k.created)
        sshkey.deactivated_on = str(k.deactivated_on) if k.deactivated_on else None
        sshkey.deactivated_reason = k.deactivated_reason
        sshkey.description = k.description
        sshkey.expires_on = str(k.expires_on)
        sshkey.fabric_key_type = k.fabric_key_type.name
        sshkey.fingerprint = k.fingerprint
        sshkey.public_key = k.public_key
        sshkey.ssh_key_type = k.ssh_key_type
        sshkey.uuid = k.uuid
        sshkeys.append(sshkey)
    return sshkeys


def sskeys_count_by_fabric_key_type(fab_person: FabricPeople, keytype: EnumSshKeyTypes) -> int:
    fab_sshkeys = fab_person.sshkeys
    d = defaultdict(int)
    for k in fab_sshkeys: d[k.fabric_key_type] += 1

    print(d)
    return d.get(keytype)


