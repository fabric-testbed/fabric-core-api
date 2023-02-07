import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fss_utils.sshkey import FABRICSSHKey

from swagger_server.api_logger import consoleLogger, metricsLogger
from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.sshkeys import EnumSshKeyStatus, EnumSshKeyTypes, FabricSshKeys
from swagger_server.models.bastionkeys import BastionkeysOne
from swagger_server.models.sshkey_pair import SshkeyPairResults
from swagger_server.models.sshkeys_one import SshkeysOne
from swagger_server.models.sshkeys_post import SshkeysPost
from swagger_server.models.sshkeys_put import SshkeysPut
from swagger_server.response_code.cors_response import cors_400, cors_500

# constants
TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"
DESCRIPTION_REGEX = r"^[\w\s\-'\.@_()/]{5,255}$"
COMMENT_LENGTH = 100


def create_sshkey(body: SshkeysPost, fab_person: FabricPeople) -> SshkeyPairResults:
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
    consoleLogger.info("Generating key of type '{0}' for '{1}' with comment '{2}'".format(
        body.keytype, fab_person.display_name, body.comment))
    try:
        sshkey = FABRICSSHKey.generate(body.comment, os.getenv('SSH_KEY_ALGORITHM'))
        response = SshkeyPairResults()
        if sshkey:
            now = datetime.now(timezone.utc)
            fab_sshkey = FabricSshKeys()
            fab_sshkey.comment = sshkey.comment
            fab_sshkey.created = now
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
            fab_sshkey.modified = now
            fab_sshkey.people_id = fab_person.id
            fab_sshkey.public_key = sshkey.public_key
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
            # metrics log - User SSH Key created:
            # 2022-09-06 19:45:56,022 User event usr:0000-0000-0000-0001 create sshkey KEYTYPE key:feed-beef-feed-beef
            log_msg = 'User event usr:{0} create sshkey \'{1}\' key:{2}'.format(
                str(fab_person.uuid),
                fab_sshkey.fabric_key_type.name,
                str(fab_sshkey.uuid))
            metricsLogger.info(log_msg)
        return response
    except Exception as exc:
        details = 'Oops! something went wrong with create_sshkey(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def put_sshkey(body: SshkeysPut, fab_person: FabricPeople) -> FabricSshKeys:
    # keytype: str, public_openssh: str, description: str
    consoleLogger.info("PUT key of type '{0}'".format(body.keytype))
    try:
        fssh = FABRICSSHKey(body.public_openssh)
        if fssh.get_fingerprint() in [k.fingerprint for k in fab_person.sshkeys]:
            details = "Fingerprint '{0}' is not unique".format(fssh.get_fingerprint())
            consoleLogger.error(details)
            return cors_400(details=details)
        # create new fabric key object
        fab_sshkey = FabricSshKeys()
        fab_sshkey.comment = fssh.comment
        fab_sshkey.created = datetime.now(timezone.utc)
        fab_sshkey.description = body.description
        if body.keytype == EnumSshKeyTypes.sliver.name:
            fab_sshkey.expires_on = datetime.now(timezone.utc) + \
                                    timedelta(days=float(os.getenv('SSH_SLIVER_KEY_VALIDITY_DAYS')))
            fab_sshkey.fabric_key_type = EnumSshKeyTypes.sliver
        else:
            fab_sshkey.expires_on = datetime.now(timezone.utc) + \
                                    timedelta(days=float(os.getenv('SSH_BASTION_KEY_VALIDITY_DAYS')))
        fab_sshkey.fabric_key_type = body.keytype
        fab_sshkey.fingerprint = fssh.get_fingerprint()
        fab_sshkey.people_id = fab_person.id
        fab_sshkey.public_key = fssh.public_key
        fab_sshkey.ssh_key_type = fssh.name
        fab_sshkey.uuid = uuid4()
        db.session.add(fab_sshkey)
        db.session.commit()
        return fab_sshkey
    except Exception as exc:
        details = 'Oops! something went wrong with put_sshkey(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def delete_sshkey(fab_person: FabricPeople, fab_sshkey: FabricSshKeys):
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
    consoleLogger.info("Delete key '{0}'".format(fab_sshkey.uuid))
    try:
        now = datetime.now(timezone.utc)
        # deactivate key
        fab_sshkey.deactivated_on = now
        fab_sshkey.deactivated_reason = 'User deactivated on {0}'.format(now)
        fab_sshkey.active = False
        fab_sshkey.status = EnumSshKeyStatus.deactivated
        # save db
        db.session.commit()
        # metrics log - User SSH Key deactivated:
        # 2022-09-06 19:45:56,022 User event usr:0000-0000-0000-0001 deactivate sshkey KEYTYPE key:feed-beef-feed-beef
        log_msg = 'User event usr:{0} deactivate sshkey \'{1}\' key:{2}'.format(
            str(fab_person.uuid),
            fab_sshkey.fabric_key_type.name,
            str(fab_sshkey.uuid))
        metricsLogger.info(log_msg)
    except Exception as exc:
        details = 'Oops! something went wrong with delete_sshkey(): {0}'.format(exc)
        consoleLogger.error(details)
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
    sshkey.uuid = str(fab_sshkey.uuid)
    return sshkey


def sshkeys_from_fab_person(fab_person: FabricPeople, is_self: bool = False) -> [SshkeysOne]:
    """
    Return
    - sliver:active to authenticated users
    - sliver:active/deactivated/expired to owner
    - bastion:active/deactivated/expired to owner
    """
    sshkeys = []
    fab_key_types = [EnumSshKeyTypes.sliver]
    fab_key_status = [EnumSshKeyStatus.active]
    if is_self:
        fab_key_types.append(EnumSshKeyTypes.bastion)
        # fab_key_status.append(EnumSshKeyStatus.deactivated)
        # fab_key_status.append(EnumSshKeyStatus.expired)
    for k in fab_person.sshkeys:
        if k.fabric_key_type in fab_key_types and k.status in fab_key_status:
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
            sshkey.uuid = str(k.uuid)
            sshkeys.append(sshkey)
    return sshkeys


def sskeys_count_by_fabric_key_type(fab_person: FabricPeople, keytype: EnumSshKeyTypes) -> int:
    key_count = FabricSshKeys.query.filter(
        FabricSshKeys.fabric_key_type == keytype,
        FabricSshKeys.status == EnumSshKeyStatus.active,
        FabricSshKeys.people_id == fab_person.id
    ).count()
    return key_count


def bastionkeys_by_since_date(since_date: datetime = None) -> [BastionkeysOne]:
    bastionkeys = []
    results = FabricSshKeys.query.filter(
        FabricSshKeys.fabric_key_type == EnumSshKeyTypes.bastion,
        ((FabricSshKeys.created >= since_date) | (FabricSshKeys.deactivated_on >= since_date))
    ).order_by('created').all()
    for r in results:
        try:
            fab_person = FabricPeople.query.filter_by(id=r.people_id).one_or_none()
            if fab_person:
                bkey = BastionkeysOne()
                bkey.status = r.status.name
                bkey.login = fab_person.bastion_login()
                bkey.gecos = fab_person.gecos()
                ts = r.expires_on.strftime("_(%Y-%m-%d_%H:%M:%S%z)_")
                bastion_comment = r.comment.strip()[0:COMMENT_LENGTH - len(ts)] + ts
                bkey.public_openssh = " ".join([r.ssh_key_type, r.public_key, bastion_comment])
                bastionkeys.append(bkey)
        except Exception as exc:
            consoleLogger.error('sshkeys_utils.bastionkeys_by_since_date: {0}'.format(exc))
    consoleLogger.info('sshkeys_utils.bastionkeys_by_since_date: {0} keys returned'.format(len(bastionkeys)))
    return bastionkeys


def deactivate_expired_keys():
    """
    Scan the keys and deactivate those that are expired.
    """
    now = datetime.now(timezone.utc)
    expired_keys = FabricSshKeys.query.filter(
        FabricSshKeys.expires_on < now,
        FabricSshKeys.active.__eq__(True)
    ).order_by('created').all()
    for k in expired_keys:
        try:
            fab_person = FabricPeople.query.filter(FabricPeople.id == k.people_id).one_or_none()
            k.deactivated_on = now
            k.deactivated_reason = 'Key automatically expired on {0}'.format(now)
            k.active = False
            k.status = EnumSshKeyStatus.expired
            # save db
            db.session.commit()
            consoleLogger.info('deactivate sshkey:{0} from usr:{1}'.format(str(k.uuid), str(fab_person.uuid)))
            # metrics log - User SSH Key deactivated:
            # 2022-09-06 19:45:56,022 User event usr:0000-0000-0000-0001 deactivate sshkey KEYTYPE key:feed-beef-feed-beef
            log_msg = 'User event usr:{0} deactivate sshkey \'{1}\' key:{2}'.format(
                str(fab_person.uuid),
                k.fabric_key_type.name,
                str(k.uuid))
            metricsLogger.info(log_msg)
        except Exception as exc:
            consoleLogger.error('sshkeys_utils.deactivate_expired_keys: {0}'.format(exc))


def garbage_collect_expired_keys():
    """
    Delete deactivated keys older than specified period
    """
    now = datetime.now(timezone.utc)
    gc_delta = timedelta(days=float(os.getenv('SSH_GARBAGE_COLLECT_AFTER_DAYS')))
    check_instant = now - gc_delta
    garbage_keys = FabricSshKeys.query.filter(
        FabricSshKeys.deactivated_on < check_instant,
        FabricSshKeys.active.__eq__(False)
    ).order_by('created').all()
    for k in garbage_keys:
        try:
            fab_person = FabricPeople.query.filter(FabricPeople.id == k.people_id).one_or_none()
            # remove key from person
            fab_person.sshkeys.remove(k)
            consoleLogger.info('garbage collect sshkey:{0} from usr:{1}'.format(str(k.uuid), str(fab_person.uuid)))
            # metrics log - User SSH Key deleted:
            # 2022-09-06 19:45:56,022 User event usr:0000-0000-0000-0001 delete sshkey KEYTYPE key:feed-beef-feed-beef
            log_msg = 'User event usr:{0} delete sshkey \'{1}\' key:{2}'.format(
                str(fab_person.uuid),
                k.fabric_key_type.name,
                str(k.uuid))
            metricsLogger.info(log_msg)
            # delete key
            db.session.delete(k)
            # save db
            db.session.commit()
        except Exception as exc:
            consoleLogger.error('sshkeys_utils.garbage_collect_expired_keys: {0}'.format(exc))
