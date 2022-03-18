import connexion
import six

from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server.models.whoami import Whoami  # noqa: E501
from swagger_server import util
from swagger_server.response_code import whoami_controller as rc

from flask import request
import base64
import gzip
import jwt
import json


def whoami_get():  # noqa: E501
    """Who am I?

    Who am I? # noqa: E501


    :rtype: Whoami
    """
    if 'fabric-service-alpha' in request.cookies:
        print('Logged in')
        compressed_base64_cookie = request.cookies.get('fabric-service-alpha')
        encoded_compressed_base64_cookie = compressed_base64_cookie.encode('utf-8')
        compressed_bytes = base64.urlsafe_b64decode(encoded_compressed_base64_cookie)
        decompressed_bytes = gzip.decompress(compressed_bytes)
        decoded_bytes = decompressed_bytes.decode('utf-8')

        vouch_string = jwt.decode(
            jwt=decoded_bytes,
            key="narei7ood7aigheiK3noph9Eesei3miechoakohpheij",
            algorithms=["HS256"],
            options={"verify_aud": False}
        )

        print(json.dumps(vouch_string, indent=2))
    else:
        print('NOT logged in')

    # idp_idtoken = request.headers.get('X-Vouch-Idp-Idtoken', None)
    # cookie = request.cookies.get('fabric-service-alpha', None)
    # print('idp_token: ', idp_idtoken)
    # print('cookie: ', cookie)
    # decoded = base64.b64decode(cookie)
    # # sample = decoded.decode('utf-8')
    # print(decoded)
    # print(sample)
    return 'do some magic!'
