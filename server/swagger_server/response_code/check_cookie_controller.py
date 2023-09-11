from swagger_server.models.check_cookie import CheckCookie, CheckCookieResults  # noqa: E501
import os
from datetime import datetime, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.models.whoami import Whoami, WhoamiResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_401, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims, update_fabric_person
from swagger_server.response_code.whoami_utils import get_vouch_session_expiry
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims

def check_cookie_get():  # noqa: E501
    """Check Cookie

    Check Cookie # noqa: E501


    :rtype: CheckCookie
    """
    try:
        # get claims from cookie
        claims = vouch_get_custom_claims()
        check_cookie = CheckCookieResults()
        check_cookie.email = claims.get('email')
        check_cookie.family_name = claims.get('family_name')
        check_cookie.given_name = claims.get('given_name')
        check_cookie.name = claims.get('name')
        check_cookie.sub = claims.get('sub')
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
