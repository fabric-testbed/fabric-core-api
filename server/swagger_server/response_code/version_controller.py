import logging

from swagger_server import __API_VERSION__, __API_REFERENCE__
from swagger_server.models.version import Version, VersionResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_500

logger = logging.getLogger(__name__)


def version_get() -> Version:  # noqa: E501
    """Version

    Version # noqa: E501


    :rtype: Version
    """
    try:
        version = VersionResults()
        version.reference = __API_REFERENCE__
        version.version = __API_VERSION__
        response = Version()
        response.results = [version]
        response.size = len(response.results)
        response.status = 200
        response.type = 'version'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with version_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)
