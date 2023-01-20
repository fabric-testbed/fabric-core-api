import os
import os
import re
from datetime import datetime, timezone

from fss_utils.sshkey import FABRICSSHKey

from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.sshkeys import EnumSshKeyTypes, FabricSshKeys
from swagger_server.models.bastionkeys import Bastionkeys  # noqa: E501
from swagger_server.models.sshkey_pair import SshkeyPair
from swagger_server.models.sshkeys import Sshkeys  # noqa: E501
from swagger_server.models.sshkeys_post import SshkeysPost  # noqa: E501
from swagger_server.models.sshkeys_put import SshkeysPut
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, \
    Status200OkNoContentResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_required, secret_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.sshkeys_utils import bastionkeys_by_since_date, create_sshkey, delete_sshkey, \
    put_sshkey, sshkey_from_fab_sshkey, sshkeys_from_fab_person, sskeys_count_by_fabric_key_type, garbage_collect_expired_keys, deactivate_expired_keys

TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"
DESCRIPTION_REGEX = r"^[\w\s\-'\.@_()/]{5,255}$"
COMMENT_LENGTH = 100


@secret_required
def bastionkeys_get(secret, since_date):  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param secret: unique secret token
    :type secret: dict | bytes
    :param since_date: starting date to search from
    :type since_date: str

    :rtype: Bastionkeys
    """
    try:
        # validate since_time
        try:
            since_date = str(since_date).strip()
            # with +00:00
            if re.match(TZISO, since_date) is not None:
                pdate = datetime.fromisoformat(since_date)
            # with +0000
            elif re.match(TZPYTHON, since_date) is not None:
                pdate = datetime.strptime(since_date, "%Y-%m-%d %H:%M:%S%z")
            # perhaps no TZ info? add as if UTC
            else:
                pdate = datetime.strptime(since_date + "+0000", "%Y-%m-%d %H:%M:%S%z")
            # convert to UTC
            pdate = pdate.astimezone(timezone.utc)
        except ValueError as exc:
            details = 'Exception: since_date: {0}'.format(exc)
            consoleLogger.error(details)
            return cors_400(details=details)
        # check for expired keys and garbage collect
        deactivate_expired_keys()
        garbage_collect_expired_keys()
        # generate bastionkeys response
        response = Bastionkeys()
        response.results = bastionkeys_by_since_date(since_date=pdate)
        response.size = len(response.results)
        response.status = 200
        response.type = 'bastionkeys'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with bastionkeys_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_get(person_uuid=None) -> Sshkeys:  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param person_uuid: person uuid
    :type person_uuid: str

    :rtype: Sshkeys
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get FabricSshKey
        fab_person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for Person with uuid = '{0}'".format(person_uuid))
        people_prefs = {p.key: p.value for p in fab_person.preferences}
        # create response
        response = Sshkeys()
        if api_user is fab_person:
            response.results = sshkeys_from_fab_person(fab_person=fab_person, is_self=True)
        else:
            response.results = sshkeys_from_fab_person(
                fab_person=fab_person, is_self=False) if people_prefs.get('show_sshkeys') else []
        response.size = len(response.results)
        response.status = 200
        response.type = 'sshkeys'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_post(body: SshkeysPost = None) -> SshkeyPair:  # noqa: E501
    """Create a public/private SSH Key Pair

    Create a public/private SSH Key Pair # noqa: E501

    :param body: Create a public/private SSH Key Pair
    :type body: dict | bytes

    :rtype: SshkeyPair
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # check key count by fabric_key_type
        key_count = sskeys_count_by_fabric_key_type(
            fab_person=api_user,
            keytype=EnumSshKeyTypes.sliver if body.keytype == 'sliver' else EnumSshKeyTypes.bastion)
        if key_count >= int(os.getenv('SSH_KEY_QTY_LIMIT')):
            return cors_403(details="User: '{0}' already has max number of SSH Keys of type '{1}'".format(
                api_user.display_name, body.keytype))
        # create SSH Key Pair
        fab_sshkey = create_sshkey(body=body, fab_person=api_user)
        results = [fab_sshkey]
        # create response
        response = SshkeyPair()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = 'sshkeys.keypair'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_post(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_put(body: SshkeysPut = None):  # noqa: E501
    """Add a public SSH Key

    Add a public SSH Key # noqa: E501

    :param body: Add a public SSH Key
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # check key count by fabric_key_type
        key_count = sskeys_count_by_fabric_key_type(
            fab_person=api_user,
            keytype=EnumSshKeyTypes.sliver if body.keytype == 'sliver' else EnumSshKeyTypes.bastion)
        if key_count >= int(os.getenv('SSH_KEY_QTY_LIMIT')):
            return cors_403(details="User: '{0}' already has max number of SSH Keys of type '{1}'".format(
                api_user.display_name, body.keytype))
        # validate
        fssh = FABRICSSHKey(body.public_openssh)
        if fssh.get_fingerprint() in [k.fingerprint for k in api_user.sshkeys]:
            details = "Duplicate Key: Fingerprint '{0}' is not unique".format(fssh.get_fingerprint())
            consoleLogger.error(details)
            return cors_400(details=details)
        # put SSH public key
        try:
            fab_sshkey = put_sshkey(body=body, fab_person=api_user)
        except Exception as exc:
            details = 'Oops! something went wrong with sshkeys_put(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
        # create response
        put_info = Status200OkNoContentResults()
        put_info.details = "SSH Key: '{0}' has been successfully saved".format(fab_sshkey.fingerprint)
        response = Status200OkNoContent()
        response.results = [put_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_put(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_uuid_delete(uuid) -> Status200OkNoContent:  # noqa: E501
    """Delete SSH Key by UUID

    Delete SSH Key by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    try:
        # get FabricSshKey
        fab_sshkey = FabricSshKeys.query.filter_by(uuid=uuid).one_or_none()
        if not fab_sshkey:
            return cors_404(details="No match for SSH Key with uuid = '{0}'".format(uuid))
        # get api_user and verify ownership of key
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active or api_user.id != fab_sshkey.people_id:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or does not own SSH Key '{1}'".format(
                    api_user.display_name, fab_sshkey.uuid))
        # delete the key
        delete_sshkey(fab_person=api_user, fab_sshkey=fab_sshkey)
        # create response
        delete_info = Status200OkNoContentResults()
        delete_info.details = "SSH Key: '{0}' has been successfully deleted".format(uuid)
        response = Status200OkNoContent()
        response.results = [delete_info]
        response.size = len(response.results)
        response.status = 200
        response.type = 'no_content'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_uuid_delete(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_uuid_get(uuid: str) -> Sshkeys:  # noqa: E501
    """SSH Key details by UUID

    SSH Key details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Sshkeys
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user".format(api_user.display_name))
        # get FabricSshKey
        fab_sshkey = FabricSshKeys.query.filter_by(uuid=uuid).one_or_none()
        if not fab_sshkey:
            return cors_404(details="No match for SSH Key with uuid = '{0}'".format(uuid))
        # only return bastion key to owner
        if api_user.id == fab_sshkey.people_id or fab_sshkey.fabric_key_type == EnumSshKeyTypes.sliver:
            results = [sshkey_from_fab_sshkey(fab_sshkey=fab_sshkey)]
        else:
            results = []
        # create response
        response = Sshkeys()
        response.results = results
        response.size = len(results)
        response.status = 200
        response.type = 'sshkeys.detail'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_uuid_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)
