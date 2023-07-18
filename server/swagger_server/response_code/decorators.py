import os
from functools import wraps
import hashlib
import jwt
from flask import request

from swagger_server.api_logger import consoleLogger
from swagger_server.response_code.cors_response import cors_401
from swagger_server.response_code.vouch_utils import vouch_get_custom_claims


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.getenv('VOUCH_COOKIE_NAME') not in request.cookies:
            details = 'Login required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            consoleLogger.info("login_required(): {0}".format(details))
            return cors_401(details=details)
        if not vouch_get_custom_claims():
            details = 'Cookie signature has expired: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            consoleLogger.info("login_required(): {0}".format(details))
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
            consoleLogger.info("secret_required(): {0}".format(details))
            return cors_401(details=details)
        if secret != os.getenv('SSH_KEY_SECRET'):
            details = 'Secret required: incorrect secret provided'
            consoleLogger.info("secret_required(): {0}".format(details))
            return cors_401(details=details)

        return f(*args, **kwargs)

    return decorated_function


def login_or_token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authorization' in [h.casefold() for h in request.headers.keys()]:
            if validate_authorization_token(request.headers.get('authorization')):
                return f(*args, **kwargs)
            else:
                details = 'Login or Valid Token required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
                consoleLogger.info("login_or_token_required(): {0}".format(details))
                return cors_401(details=details)
        if os.getenv('VOUCH_COOKIE_NAME') not in request.cookies:
            details = 'Login or Valid Token required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            consoleLogger.info("login_or_token_required(): {0}".format(details))
            return cors_401(details=details)
        if not vouch_get_custom_claims():
            details = 'Cookie signature has expired: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            consoleLogger.info("login_or_token_required(): {0}".format(details))
            return cors_401(details=details)

        return f(*args, **kwargs)

    return decorated_function


def validate_authorization_token(token: str) -> bool:
    # TODO: account for Ansible script which uses a static token for now
    if token == 'Bearer {0}'.format(os.getenv('ANSIBLE_AUTHORIZATION_TOKEN')):
        return True
    # Handle CM based tokens
    try:
        token = token.replace('Bearer ', '')
        token_json = jwt.decode(
            jwt=token,
            key=os.getenv('PUBLIC_SIGNING_KEY'),
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        print(token_json)
        if not is_token_revoked(token=token):
            return True
    except Exception as exc:
        print(exc)
    return False


def is_token_revoked(token: str) -> bool:
    """
    Check all incoming tokens against a token revocation list (TRL)
    """
    revocation_list = get_token_revocation_list()
    try:
        token_hash = hashlib.new('sha256')
        token_hash.update(token.encode())
        if token_hash.hexdigest() in revocation_list:
            return True
    except Exception as exc:
        print(exc)
        return True
    return False


def get_token_revocation_list() -> []:
    """
    - TODO: get revocation list from CM
    - TODO: SHA256 simple hash <-- needs to mirror whatever CM is doing
    """
    return ['ba8a9d292308e55ac9ca1f995625aecb2876fb4ba16935152a69a0efc28e4cbe']
