import hashlib
import json
import os
from datetime import datetime, timezone
from functools import wraps

import jwt
import requests
from flask import request
from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.tasktracker import TaskTimeoutTracker
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
    s = requests.Session()
    is_valid = False
    # account for Ansible script which uses a static token for now
    if token == 'Bearer {0}'.format(os.getenv('ANSIBLE_AUTHORIZATION_TOKEN')):
        is_valid = True
    # Handle CM based tokens
    else:
        try:
            psk = TaskTimeoutTracker.query.filter_by(name=os.getenv('PSK_NAME')).one_or_none()
            if not psk.timed_out():
                public_signing_key = jwt.PyJWK(json.loads(psk.value)).key
            else:
                api_call = s.get(url=os.getenv('FABRIC_CREDENTIAL_MANAGER') + '/credmgr/certs')
                jwks = api_call.json().get('keys')[0]
                public_signing_key = jwt.PyJWK(jwks).key
                psk.value = json.dumps(jwks)
                psk.last_updated = datetime.now(timezone.utc)
                db.session.commit()
            token = token.replace('Bearer ', '')
            token_json = jwt.decode(
                jwt=token,
                key=public_signing_key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
            if not is_token_revoked(token=token):
                is_valid = True
        except Exception as exc:
            print(exc)
            is_valid = False
    s.close()
    return is_valid


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


def get_token_revocation_list() -> [str]:
    """
    Retrieve Token Revocation List (TRL) from CM at some interval
    """
    s = requests.Session()
    try:
        trl = TaskTimeoutTracker.query.filter_by(name=os.getenv('TRL_NAME')).one_or_none()
        if not trl.timed_out():
            token_revocation_list = json.loads(trl.value)
        else:
            api_call = s.get(url=os.getenv('FABRIC_CREDENTIAL_MANAGER') + '/credmgr/tokens/revoke_list')
            token_revocation_list = api_call.json().get('data')
            trl.value = json.dumps(token_revocation_list)
            trl.last_updated = datetime.now(timezone.utc)
            trl.save()
    except Exception as exc:
        print(exc)
        token_revocation_list = []
    s.close()
    return list(token_revocation_list)
