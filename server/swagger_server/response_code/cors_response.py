import json
import os
from typing import Union

from flask import request, Response

from swagger_server.models.announcements import Announcements
from swagger_server.models.announcements_details import AnnouncementsDetails
from swagger_server.models.api_options import ApiOptions
from swagger_server.models.bastionkeys import Bastionkeys
from swagger_server.models.check_cookie import CheckCookie
from swagger_server.models.people import People
from swagger_server.models.people_details import PeopleDetails
from swagger_server.models.projects import Projects
from swagger_server.models.projects_details import ProjectsDetails
from swagger_server.models.sshkey_pair import SshkeyPair
from swagger_server.models.sshkeys import Sshkeys
from swagger_server.models.status200_ok_no_content import Status200OkNoContent, Status200OkNoContentResults
from swagger_server.models.status400_bad_request import Status400BadRequest, Status400BadRequestErrors
from swagger_server.models.status401_unauthorized import Status401Unauthorized, Status401UnauthorizedErrors
from swagger_server.models.status403_forbidden import Status403Forbidden, Status403ForbiddenErrors
from swagger_server.models.status404_not_found import Status404NotFound, Status404NotFoundErrors
from swagger_server.models.status423_locked import Status423Locked, Status423LockedErrors
from swagger_server.models.status500_internal_server_error import Status500InternalServerError, \
    Status500InternalServerErrorErrors
from swagger_server.models.storage import Storage
from swagger_server.models.storage_many import StorageMany
from swagger_server.models.testbed_info import TestbedInfo
from swagger_server.models.version import Version
from swagger_server.models.whoami import Whoami

# Constants
_INDENT = int(os.getenv('CORE_API_JSON_RESPONSE_INDENT', '0'))


def delete_none(_dict):
    """
    Delete None values recursively from all of the dictionaries, tuples, lists, sets
    """
    if isinstance(_dict, dict):
        for key, value in list(_dict.items()):
            if isinstance(value, (list, dict, tuple, set)):
                _dict[key] = delete_none(value)
            elif value is None or key is None:
                del _dict[key]

    elif isinstance(_dict, (list, set, tuple)):
        _dict = type(_dict)(delete_none(item) for item in _dict if item is not None)

    return _dict


def cors_response(req: request, status_code: int = 200, body: object = None, x_error: str = None) -> Response:
    """
    Return CORS Response object
    """
    response = Response()
    response.status_code = status_code
    response.data = body
    response.headers['Content-type'] = 'application/json'
    response.headers['Access-Control-Allow-Origin'] = req.headers.get('Origin',
                                                                      os.getenv('NGINX_ACCESS_CONTROL_ALLOW_ORIGIN'))
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'DNT, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Range, Authorization'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Range, X-Error'

    if x_error:
        response.headers['X-Error'] = x_error

    return response


def cors_200(response_body: Union[
    ApiOptions, Bastionkeys, CheckCookie, People, PeopleDetails, Projects, ProjectsDetails, SshkeyPair, Sshkeys,
    Status200OkNoContent, Announcements, Version, Whoami, AnnouncementsDetails, TestbedInfo, StorageMany, Storage
] = None) -> cors_response:
    """
    Return 200 - OK
    """
    return cors_response(
        req=request,
        status_code=200,
        body=json.dumps(delete_none(response_body.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(response_body.to_dict()), sort_keys=True)
    )


def cors_200_no_content(details: str = None) -> cors_response:
    """
    Return 200 - No Content
    """
    results = Status200OkNoContentResults()
    results.details = details
    results_object = Status200OkNoContent([results])
    return cors_response(
        req=request,
        status_code=200,
        body=json.dumps(delete_none(results_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(results_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_400(details: str = None) -> cors_response:
    """
    Return 400 - Bad Request
    """
    errors = Status400BadRequestErrors()
    errors.details = details
    error_object = Status400BadRequest([errors])
    return cors_response(
        req=request,
        status_code=400,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_401(details: str = None) -> cors_response:
    """
    Return 401 - Unauthorized
    """
    errors = Status401UnauthorizedErrors()
    errors.details = details
    error_object = Status401Unauthorized([errors])
    return cors_response(
        req=request,
        status_code=401,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_403(details: str = None) -> cors_response:
    """
    Return 403 - Forbidden
    """
    errors = Status403ForbiddenErrors()
    errors.details = details
    error_object = Status403Forbidden([errors])
    return cors_response(
        req=request,
        status_code=403,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_404(details: str = None) -> cors_response:
    """
    Return 404 - Not Found
    """
    errors = Status404NotFoundErrors()
    errors.details = details
    error_object = Status404NotFound([errors])
    return cors_response(
        req=request,
        status_code=404,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_423(details: str = None) -> cors_response:
    """
    Return 423 - Locked
    """
    errors = Status423LockedErrors()
    errors.details = details
    error_object = Status423Locked([errors])
    return cors_response(
        req=request,
        status_code=423,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )


def cors_500(details: str = None) -> cors_response:
    """
    Return 500 - Internal Server Error
    """
    errors = Status500InternalServerErrorErrors()
    errors.details = details
    error_object = Status500InternalServerError([errors])
    return cors_response(
        req=request,
        status_code=500,
        body=json.dumps(delete_none(error_object.to_dict()), indent=_INDENT, sort_keys=True)
        if _INDENT != 0 else json.dumps(delete_none(error_object.to_dict()), sort_keys=True),
        x_error=details
    )
