import os

from swagger_server.api_logger import consoleLogger
from swagger_server.models.api_options import ApiOptions  # noqa: E501
from swagger_server.models.status200_ok_no_content import Status200OkNoContent  # noqa: E501
from swagger_server.response_code import PUBLICATIONS_CLASSIFICATION_TERMS
from swagger_server.response_code.cors_response import cors_200, cors_500
from swagger_server.response_code.decorators import login_required

# Constants
_SERVER_URL = os.getenv('CORE_API_SERVER_URL', '')


def publications_classification_terms_get(search=None) -> ApiOptions:  # noqa: E501
    """List of Classification Terms

    List of Classification Terms # noqa: E501

    :param search: search term applied
    :type search: str

    :rtype: ApiOptions
    """
    try:
        if search:
            results = [tag for tag in PUBLICATIONS_CLASSIFICATION_TERMS.search(search) if
                       search.casefold() in tag.casefold()]
        else:
            results = PUBLICATIONS_CLASSIFICATION_TERMS.options
        response = ApiOptions()
        # response.results = [r.split(':')[-1] for r in results]
        response.results = [r.split('/')[0] for r in results]
        # response.results = results
        response.size = len(results)
        response.status = 200
        response.type = PUBLICATIONS_CLASSIFICATION_TERMS.name
        return cors_200(response_body=response)
    except Exception as exc:
        consoleLogger.error("publications_classification_terms_get(search=None): {0}".format(exc))
        return cors_500(details='Ooops! something has gone wrong with publications_classification_terms_get()')


def publications_get(search=None, offset=None, limit=None):  # noqa: E501
    """Publications (placeholder)

    Search for Publications by author or title # noqa: E501

    :param search: search term applied
    :type search: str
    :param offset: number of items to skip before starting to collect the result set
    :type offset: int
    :param limit: maximum number of results to return per page (1 or more)
    :type limit: int

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_post():  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501


    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_uuid_delete(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


def publications_uuid_get(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'


@login_required
def publications_uuid_patch(uuid):  # noqa: E501
    """Publications (placeholder)

    Publications (placeholder) # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: Status200OkNoContent
    """
    return 'do some magic!'
