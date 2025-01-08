import re
from datetime import datetime, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.models.journey_tracker_people import JourneyTrackerPeople  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_401, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.journey_tracker_utils import journey_tracker_people_by_since_date
from swagger_server.response_code.vouch_utils import IdSourceEnum

TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"
DESCRIPTION_REGEX = r"^[\w\s\-'\.@_()/]{5,255}$"
COMMENT_LENGTH = 100


@login_or_token_required
def journey_tracker_people_get(since_date, until_date=None):  # noqa: E501
    """Get people information for Journey Tracker

    Get people information for Journey Tracker # noqa: E501

    :param since_date: starting date to search from
    :type since_date: str
    :param until_date: ending date to search to
    :type until_date: str

    :rtype: JourneyTrackerPeople
    """

    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.READONLY.value or api_user.is_facility_operator():
        try:
            try:
                # validate since_date
                if since_date:
                    since_date = str(since_date).strip()
                    # with +00:00
                    if re.match(TZISO, since_date) is not None:
                        s_date = datetime.fromisoformat(since_date)
                    # with +0000
                    elif re.match(TZPYTHON, since_date) is not None:
                        s_date = datetime.strptime(since_date, "%Y-%m-%d %H:%M:%S%z")
                    # perhaps no TZ info? add as if UTC
                    else:
                        s_date = datetime.strptime(since_date + "+0000", "%Y-%m-%d %H:%M:%S%z")
                    # convert to UTC
                    s_date = s_date.astimezone(timezone.utc)
                else:
                    s_date = datetime.now(timezone.utc)
                # validate until_date
                if until_date is not None:
                    until_date = str(until_date).strip()
                    # with +00:00
                    if re.match(TZISO, until_date) is not None:
                        u_date = datetime.fromisoformat(until_date)
                    # with +0000
                    elif re.match(TZPYTHON, until_date) is not None:
                        u_date = datetime.strptime(until_date, "%Y-%m-%d %H:%M:%S%z")
                    # perhaps no TZ info? add as if UTC
                    else:
                        u_date = datetime.strptime(until_date + "+0000", "%Y-%m-%d %H:%M:%S%z")
                    # convert to UTC
                    u_date = u_date.astimezone(timezone.utc)
                else:
                    u_date = datetime.now(timezone.utc)
            except ValueError as exc:
                details = 'Exception: since_date / until_date: {0}'.format(exc)
                consoleLogger.error(details)
                return cors_400(details=details)
            # generate journey_tracker_people_get response
            response = JourneyTrackerPeople()
            response.results = journey_tracker_people_by_since_date(since_date=s_date, until_date=u_date)
            response.size = len(response.results)
            response.status = 200
            response.type = 'journey_tracker_people'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with journey_tracker_people_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )
