import connexion
import six
import logging

from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.people import People  # noqa: E501
from swagger_server.models.people_details import PeopleDetails  # noqa: E501
from swagger_server.models.people_patch import PeoplePatch  # noqa: E501
from swagger_server.models.people_profile_patch import PeopleProfilePatch  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.models.status400_bad_request import Status400BadRequest  # noqa: E501
from swagger_server.models.status401_unauthorized import Status401Unauthorized  # noqa: E501
from swagger_server.models.status403_forbidden import Status403Forbidden  # noqa: E501
from swagger_server.models.status404_not_found import Status404NotFound  # noqa: E501
from swagger_server.models.status500_internal_server_error import Status500InternalServerError  # noqa: E501
from swagger_server import util
from swagger_server.response_code import PEOPLE_PREFERENCES, PEOPLE_PROFILE_OTHER_IDENTITY_TYPES, \
    PEOPLE_PROFILE_PREFERENCES, PEOPLE_PROFILE_PROFESSIONAL_TYPES, PEOPLE_PROFILE_SOCIAL_TYPES
from swagger_server.response_code.cors_response import cors_200, cors_500

logger = logging.getLogger(__name__)


def people_get(search=None, offset=None, limit=None):  # noqa: E501
    """Search for FABRIC People

    Search for FABRIC People by name or email # noqa: E501

    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: People
    """
    return 'do some magic!'


def people_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Preference options

    List of People Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Preferences.Get()')


def people_profile_otheridentity_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Other Identity Type options

    List of People Profile Other Identity Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_OTHER_IDENTITY_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_otheridentity_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.OtherIdentity.Types.Get()')


def people_profile_preferences_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Preference options

    List of People Profile Preference options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_PREFERENCES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_PREFERENCES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_PREFERENCES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_preferences_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Preferences.Get()')


def people_profile_professionalpage_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Professional Page Type options

    List of People Profile Professional Page Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_PROFESSIONAL_TYPES.search(search) if
                    search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_PROFESSIONAL_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_PROFESSIONAL_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_professionalpage_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Professional.Types.Get()')


def people_profile_socialpage_types_get(search=None) -> ApiOptions:  # noqa: E501
    """List of People Profile Social Page Type options

    List of People Profile Social Page Type options # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            data = [tag for tag in PEOPLE_PROFILE_SOCIAL_TYPES.search(search) if search.casefold() in tag.casefold()]
        else:
            data = PEOPLE_PROFILE_SOCIAL_TYPES.options
        response = ApiOptions()
        response.data = data
        response.size = len(data)
        response.status = 200
        response.type = PEOPLE_PROFILE_SOCIAL_TYPES.name
        return cors_200(response_body=response)
    except Exception as exc:
        logger.error("people_profile_socialpage_types_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with People.Profile.Social.Types.Get()')


def people_uuid_get(uuid, as_self=None):  # noqa: E501
    """Person details by UUID

    Person details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param as_self: GET object as Self
    :type as_self: bool

    :rtype: PeopleDetails
    """
    return 'do some magic!'


def people_uuid_patch(uuid, body=None):  # noqa: E501
    """Update Person details as Self

    Update Person details as Self # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Person details as self
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


def people_uuid_profile_patch(uuid, body=None):  # noqa: E501
    """Update Person Profile details as Self

    Update Person Profile details as Self # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str
    :param body: Update Person details as self
    :type body: dict | bytes

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'
