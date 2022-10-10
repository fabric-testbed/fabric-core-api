import base64
import gzip
import logging
import os

import jwt
from flask import request

logger = logging.getLogger(__name__)


def get_vouch_session_expiry() -> int:
    """
    Decoded JWT from Vouch-Proxy cookie
    GET decoded JWT from the cookie and return expiry as timestamp

    :rtype: int
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
        # return vouch_json "exp" value
        return int(vouch_json.get('exp'))

    except Exception as exc:
        details = 'Oops! something went wrong with get_vouch_session_expiry(): {0}'.format(exc)
        logger.error(details)
        return -1
