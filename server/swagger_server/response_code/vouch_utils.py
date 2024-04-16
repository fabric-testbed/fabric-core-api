import base64
import gzip
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum

import jwt
import requests
from comanage_api import ComanageApi
from flask import request

from swagger_server.database.db import db
from swagger_server.database.models.people import FabricPeople, FabricRoles
from swagger_server.database.models.tasktracker import TaskTimeoutTracker

api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
    co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
)


class IdSourceEnum(Enum):
    COOKIE = 'cookie-vouch-proxy'
    ANSIBLE = 'token-ansible'
    SERVICES = 'token-services'
    USER = 'token-user'


def vouch_get_custom_claims() -> dict:
    """
    Claim source - cookie-vouch-proxy

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
        claims = vouch_json.get('CustomClaims')
        claims.update(source=IdSourceEnum.COOKIE.value)
        return claims
    except Exception as exc:
        logging.warning("Missing cookie: {0} - {1}".format(os.getenv('VOUCH_COOKIE_NAME'), exc))
        return {}


def token_get_custom_claims(token: str) -> dict:
    """
    Map CM token claim to format of vouch claim and return

    Claims sources
    - token-user
    - token-services
    - token-ansible

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
        # account for Ansible script which uses a static token for now
        if token == format(os.getenv('ANSIBLE_AUTHORIZATION_TOKEN')):
            # print('ANSIBLE AUTHORIZATION TOKEN')
            claims = first_valid_facility_operator()
        # account for CF Services which uses a static token for now
        elif token == format(os.getenv('SERVICES_AUTHORIZATION_TOKEN')):
            # print('SERVICES AUTHORIZATION TOKEN')
            claims = {
                'aud': 'FABRIC',
                'email': None,
                'family_name': 'Services',
                'given_name': 'FABRIC',
                'iss': 'core-api',
                'name': 'FABRIC Services',
                'source': IdSourceEnum.SERVICES.value,
                'sub': None
            }
        # process normal user tokens
        else:
            # print('USER AUTHORIZATION TOKEN')
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
                'source': IdSourceEnum.USER.value,
                'sub': token_json.get('sub')
            }
    except Exception as exc:
        print(exc)
        claims = {}
    s.close()
    return claims


def first_valid_facility_operator() -> dict:
    """
    Returns the first valid facility operator registered within the system
    """
    # get list of facility-operator ids
    fac_op_ids = [(r.people_id, r.co_person_role_id) for r in
                  FabricRoles.query.filter_by(name=os.getenv('COU_NAME_FACILITY_OPERATORS'))]
    # check to make sure the id is still a valid facility operator
    api_user = FabricPeople()
    for fac_op_id in fac_op_ids:
        co_role = api.coperson_roles_view_one(coperson_role_id=fac_op_id[1]).get('CoPersonRoles', [])[0]
        api_user = FabricPeople.query.filter_by(id=fac_op_id[0]).one_or_none()
        if api_user and co_role.get('Status').casefold() == 'active' and co_role.get('Deleted') is False:
            # an active facility operator has been found
            break
        else:
            api_user = FabricPeople()
    # return first valid facility operator in claims format
    claims = {
        'aud': None,
        'email': api_user.oidc_claim_email,
        'family_name': api_user.oidc_claim_family_name,
        'given_name': api_user.oidc_claim_given_name,
        'iss': None,
        'name': api_user.oidc_claim_name,
        'source': IdSourceEnum.ANSIBLE.value,
        'sub': api_user.oidc_claim_sub
    }
    return claims
