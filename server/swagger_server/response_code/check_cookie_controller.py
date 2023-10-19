import os

from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.people import FabricPeople, UserSubjectIdentifiers
from swagger_server.models.check_cookie import CheckCookie, CheckCookieResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_500
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims
from swagger_server.response_code.comanage_utils import api
from swagger_server.response_code.people_utils import update_fabric_person, create_fabric_person_from_login


def check_cookie_get():  # noqa: E501
    """Check Cookie

    Check Cookie # noqa: E501


    :rtype: CheckCookie
    """
    try:
        # get claims from cookie
        claims = vouch_get_custom_claims()
        check_cookie = CheckCookieResults()
        if claims:
            check_cookie.cookie_name = os.getenv('VOUCH_COOKIE_NAME')
            cookie_attributes = {
                'email': claims.get('email') if claims.get('email') else 'CLAIM_NOT_FOUND',
                'family_name': claims.get('family_name') if claims.get('family_name') else 'CLAIM_NOT_FOUND',
                'given_name': claims.get('given_name') if claims.get('given_name') else 'CLAIM_NOT_FOUND',
                'name': claims.get('name') if claims.get('name') else 'CLAIM_NOT_FOUND',
                'sub': claims.get('sub') if claims.get('sub') else 'CLAIM_NOT_FOUND'
            }
            check_cookie.cookie_attributes = cookie_attributes
            check_cookie.fabric_attributes = get_fabric_attributes(oidc_sub=claims.get('sub'), claims=claims)
        else:
            check_cookie.cookie_name = 'COOKIE_NOT_FOUND'
            check_cookie.cookie_attributes = {}
            check_cookie.fabric_attributes = {}
        # set CheckCookie object and return
        response = CheckCookie()
        response.results = [check_cookie]
        response.size = len(response.results)
        response.status = 200
        response.type = 'check-cookie'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with check_cookie_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def get_fabric_attributes(oidc_sub: str = None, claims: dict = None) -> dict:
    sub_identifier = UserSubjectIdentifiers.query.filter(
        UserSubjectIdentifiers.sub == oidc_sub
    ).one_or_none()
    if sub_identifier:
        # is a FABRIC user
        fab_person = FabricPeople.query.filter_by(
            id=sub_identifier.people_id
        ).one_or_none()
        update_fabric_person(fab_person=fab_person)
    else:
        # might be a new FABRIC user
        # check COmanage for user by sub
        co_person = api.copeople_view_per_identifier(
            identifier=oidc_sub, distinct_by_id=True
        ).get('CoPeople', [])
        if co_person:
            # is a new FABRIC user
            fab_person = create_fabric_person_from_login(claims=claims)
        else:
            # is not a new or existing FABRIC user
            fab_person = None
    if fab_person:
        roles = [r.name for r in fab_person.roles]
        roles.sort(key=str.casefold)
        fabric_attributes = {
            'affiliation': [p.affiliation for p in fab_person.user_org_affiliations],
            'roles': roles,
            'sub': [p.sub for p in fab_person.user_sub_identities],
            'uuid': str(fab_person.uuid)
        }
    else:
        fabric_attributes = {}

    return fabric_attributes
