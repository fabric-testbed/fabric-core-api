import base64
import gzip
import json
import logging
import os
from datetime import datetime, timezone

import jwt
import requests
from flask import request
from swagger_server.database.db import db
from swagger_server.database.models.tasktracker import TaskTimeoutTracker


def vouch_get_custom_claims() -> dict:
    """
    Vouch Proxy requested CustomClaims
    - aud - the audience of the id_token, which is the client_id of the OIDC client
    - email - an email address
    - family_name - last name
    - given_name - first name
    - iss - the issuer of the id_token
    - name - display/full name
    - sub - a unique identifier for the user
    - token_id - an identifier for the returned id_token
    """
    try:
        token = request.headers.get('Authorization', None)
        if token:
            return token_get_custom_claims(token=token.replace('Bearer ', ''))
        # get base64 encoded gzipped vouch JWT
        base64_encoded_gzip_vouch_jwt = request.cookies.get(os.getenv('VOUCH_COOKIE_NAME'))
        # decode base64
        encoded_gzip_vouch_jwt_bytes = base64.urlsafe_b64decode(base64_encoded_gzip_vouch_jwt)
        # gzip decompress
        vouch_jwt_bytes = gzip.decompress(encoded_gzip_vouch_jwt_bytes)
        # decode bytes
        vouch_jwt = vouch_jwt_bytes.decode('utf-8')
        # decode JWT using Vouch Proxy secret key (do not verify aud)
        vouch_json = jwt.decode(
            jwt=vouch_jwt,
            key=os.getenv('VOUCH_JWT_SECRET'),
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        return vouch_json.get('CustomClaims')
    except Exception as exc:
        logging.warning("Missing cookie: {0} - {1}".format(os.getenv('VOUCH_COOKIE_NAME'), exc))
        return {}


def token_get_custom_claims(token: str) -> dict:
    """
    Map CM token claim to format of vouch claim and return
    CM token claims
    {
        "acr": "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
        "email": "stealey@unc.edu",
        "given_name": "Michael",
        "family_name": "Stealey",
        "name": "Michael Stealey",
        "iss": "https://cilogon.org",
        "sub": "http://cilogon.org/serverA/users/242181",
        "aud": "cilogon:/client_id/297ddfadc5eaba5eba9c89868aa9627d",
        "jti": "https://cilogon.org/oauth2/idToken/2687221d4c70648bb40c5aad214ede85/1684771926776",
        "auth_time": 1684771926,
        "exp": 1684775543,
        "iat": 1684771943,
        "projects": [...],
        "roles": [...],
        "scope": "all",
        "uuid": "b12b961d-98ec-46f1-a938-af7a5ec0410b"
    }

    Example vouch claims
    {
        'aud': 'cilogon:/client_id/617cecdd74e32be4d818ca1151531dff',
        'email': 'michael.j.stealey@gmail.com',
        'family_name': 'J. Stealey',
        'given_name': 'Michael',
        'iss': 'https://cilogon.org',
        'name': 'Michael J. Stealey',
        'sub': 'http://cilogon.org/serverA/users/2911496'
    }
    """
    s = requests.Session()
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
        token_json = jwt.decode(
            jwt=token,
            key=public_signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        claims = {
            'aud': token_json.get('aud'),
            'email': token_json.get('email'),
            'family_name': token_json.get('family_name'),
            'given_name': token_json.get('given_name'),
            'iss': token_json.get('iss'),
            'name': token_json.get('name'),
            'sub': token_json.get('sub')
        }
    except Exception as exc:
        print(exc)
        claims = {}
    s.close()
    return claims
