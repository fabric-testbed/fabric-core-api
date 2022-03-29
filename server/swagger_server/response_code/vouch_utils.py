import base64
import gzip
import logging
import os

import jwt
from flask import request

logger = logging.getLogger(__name__)


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
