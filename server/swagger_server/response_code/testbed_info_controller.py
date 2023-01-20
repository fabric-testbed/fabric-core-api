import os

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.testbed_info import FabricTestbedInfo
from swagger_server.models.testbed_info import TestbedInfo
from swagger_server.models.testbed_info_post import TestbedInfoPost
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_403, cors_500
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.testbed_info_utils import create_fabric_testbed_info_from_api


def testbed_info_get() -> TestbedInfo:  # noqa: E501
    """Testbed Information

    Testbed Information # noqa: E501


    :rtype: TestbedInfo
    """
    try:
        response = TestbedInfo()
        testbed_info = FabricTestbedInfo.query.filter_by(is_active=True).one_or_none()
        if testbed_info:
            if isinstance(testbed_info.json_data, list):
                response.results = testbed_info.json_data
            else:
                response.results = [testbed_info.json_data]
        else:
            response.results = []
        response.size = len(response.results)
        response.status = 200
        response.type = 'testbed.info'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with testbed_info_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def testbed_info_post(body: TestbedInfoPost = None) -> TestbedInfo:  # noqa: E501
    """Create Testbed Information

    Create Testbed Information # noqa: E501

    :param body: Create Testbed Information
    :type body: dict | bytes

    :rtype: TestbedInfo
    """
    try:
        # get api_user
        api_user = get_person_by_login_claims()
        # check api_user active flag and verify facility-operators role
        if not api_user.active or not api_user.is_facility_operator():
            return cors_403(
                details="User: '{0}' is not registered as an active FABRIC user or not in group '{1}'".format(
                    api_user.display_name, os.getenv('COU_NAME_FACILITY_OPERATORS')))
        # validate testbed_info
        if not body.testbed_info:
            details = "Testbed Info POST: invalid entry, must contain data for 'testbed_info'"
            consoleLogger.error(details)
            return cors_400(details=details)
        # create Announcement
        testbed_info = create_fabric_testbed_info_from_api(body=body, creator=api_user)
        db.session.commit()
        return testbed_info_get()

    except Exception as exc:
        details = 'Oops! something went wrong with testbed_info_post(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)
