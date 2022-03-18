import os
from functools import wraps

from flask import request

from swagger_server.response_code.cors_response import cors_401


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if os.getenv('VOUCH_COOKIE_NAME') not in request.cookies:
            return cors_401(details='Login required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT')))
        return f(*args, **kwargs)

    return decorated_function
