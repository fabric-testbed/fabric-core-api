import logging
import os
from functools import wraps

from flask import request

from swagger_server.response_code.cors_response import cors_401
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims

logger = logging.getLogger(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.getenv('VOUCH_COOKIE_NAME') not in request.cookies:
            details = 'Login required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            logger.info("login_required(): {0}".format(details))
            return cors_401(details=details)
        if not vouch_get_custom_claims():
            details = 'Cookie signature has expired: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            logger.info("login_required(): {0}".format(details))
            return cors_401(details=details)

        return f(*args, **kwargs)

    return decorated_function


def secret_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            secret = request.args.get('secret')
        except Exception as exc:
            details = 'Exception: {0}'.format(exc)
            logger.info("login_required(): {0}".format(details))
            return cors_401(details=details)
        if secret != os.getenv('SSH_KEY_SECRET'):
            details = 'Secret required: incorrect secret provided'
            logger.info("login_required(): {0}".format(details))
            return cors_401(details=details)

        return f(*args, **kwargs)

    return decorated_function
