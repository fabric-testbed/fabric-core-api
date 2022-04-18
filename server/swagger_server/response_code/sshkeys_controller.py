import os
import logging
import os

from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.sshkeys import FabricSshKeys, EnumSshKeyTypes
from swagger_server.models.bastionkeys import Bastionkeys  # noqa: E501
from swagger_server.models.sshkey_pair import SshkeyPair
from swagger_server.models.sshkeys import Sshkeys, SshkeysOne  # noqa: E501
from swagger_server.models.sshkeys_post import SshkeysPost  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_403, cors_404, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.sshkeys_utils import create_ssh_key, sshkey_from_fab_sshkey, sshkeys_from_fab_person, \
    sskeys_count_by_fabric_key_type

logger = logging.getLogger(__name__)


def bastionkeys_get(secret, since_date):  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param secret: unique secret token
    :type secret: dict | bytes
    :param since_date: starting date to search from
    :type since_date: str

    :rtype: Bastionkeys
    """
    return 'do some magic!'


@login_required
def sshkeys_get(person_uuid=None):  # noqa: E501
    """Get active SSH Keys

    Get active SSH Keys # noqa: E501

    :param person_uuid: person uuid
    :type person_uuid: str

    :rtype: Sshkeys
    """
    # TODO: should bastion keys be returned as well?
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active or os.getenv('COU_NAME_PROJECT_LEADS') not in [r.name for r in api_user.roles]:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PROJECT_LEADS')))
        # get FabricSshKey
        fab_person = FabricPeople.query.filter_by(uuid=person_uuid).one_or_none()
        if not fab_person:
            return cors_404(details="No match for Person with uuid = '{0}'".format(person_uuid))
        people_prefs = {p.key: p.value for p in fab_person.preferences}
        # create response
        response = Sshkeys()
        response.data = sshkeys_from_fab_person(fab_person=fab_person) if api_user is fab_person or people_prefs.get('show_sshkeys') else []
        response.size = len(response.data)
        response.status = 200
        response.type = 'sshkeys'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_get(): {0}'.format(exc)
        logger.error(details)
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
        # check api_user active flag and verify project-leads role
        if not api_user.active or os.getenv('COU_NAME_PROJECT_LEADS') not in [r.name for r in api_user.roles]:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PROJECT_LEADS')))
        # check key count by fabric_key_type
        key_count = sskeys_count_by_fabric_key_type(
            fab_person=api_user,
            keytype=EnumSshKeyTypes.sliver if body.keytype == 'sliver' else EnumSshKeyTypes.bastion)
        if key_count >= int(os.getenv('SSH_KEY_QTY_LIMIT')):
            return cors_403(details="User: '{0}' already has max number of SSH Keys of type '{1}'".format(
                api_user.display_name, body.keytype))
        # create SSH Key Pair
        fab_sshkey = create_ssh_key(body=body, fab_person=api_user)
        data = [fab_sshkey]
        # create response
        response = SshkeyPair()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = 'sshkeys.keypair'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_post(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)


@login_required
def sshkeys_put(body=None):  # noqa: E501
    """Add a public SSH Key

    Add a public SSH Key # noqa: E501

    :param body: Add a public SSH Key
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def sshkeys_uuid_delete(uuid):  # noqa: E501
    """Delete SSH Key by UUID

    Delete SSH Key by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def sshkeys_uuid_get(uuid: str) -> Sshkeys:  # noqa: E501
    """SSH Key details by UUID

    SSH Key details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Sshkeys
    """
    # TODO: should bastion keys be returned as well?
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify project-leads role
        if not api_user.active or os.getenv('COU_NAME_PROJECT_LEADS') not in [r.name for r in api_user.roles]:
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_PROJECT_LEADS')))
        # get FabricSshKey
        fab_sshkey = FabricSshKeys.query.filter_by(uuid=uuid).one_or_none()
        if not fab_sshkey:
            return cors_404(details="No match for SSH Key with uuid = '{0}'".format(uuid))
        data = [sshkey_from_fab_sshkey(fab_sshkey=fab_sshkey)]
        # create response
        response = Sshkeys()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = 'sshkeys.detail'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with sshkeys_uuid_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)
