import re
from datetime import datetime, timezone, timedelta

from swagger_server.api_logger import consoleLogger
from swagger_server.models.journey_tracker_people import JourneyTrackerPeople  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_401, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.journey_tracker_utils import journey_tracker_people_by_start_date
from swagger_server.response_code.vouch_utils import IdSourceEnum

TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"
DESCRIPTION_REGEX = r"^[\w\s\-'\.@_()/]{5,255}$"
COMMENT_LENGTH = 100


@login_or_token_required
def journey_tracker_people_get(start_date=None, end_date=None):  # noqa: E501
    """Get people information for Journey Tracker

    Get people information for Journey Tracker # noqa: E501

    :param start_date: starting date to search from
    :type start_date: str
    :param end_date: end date to search to
    :type end_date: str

    :rtype: JourneyTrackerPeople

    default to last 90 days if no start_date or end_date provided
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.READONLY.value or api_user.is_facility_operator():
        try:
            try:
                # validate since_date
                if start_date:
                    start_date = str(start_date).strip()
                    # with +00:00
                    if re.match(TZISO, start_date) is not None:
                        s_date = datetime.fromisoformat(start_date)
                    # with +0000
                    elif re.match(TZPYTHON, start_date) is not None:
                        s_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S%z")
                    # perhaps no TZ info? add as if UTC
                    else:
                        s_date = datetime.strptime(start_date + "+0000", "%Y-%m-%d %H:%M:%S%z")
                    # convert to UTC
                    s_date = s_date.astimezone(timezone.utc)
                else:
                    s_date = datetime.now(timezone.utc)
                # validate until_date
                if end_date is not None:
                    end_date = str(end_date).strip()
                    # with +00:00
                    if re.match(TZISO, end_date) is not None:
                        e_date = datetime.fromisoformat(end_date)
                    # with +0000
                    elif re.match(TZPYTHON, end_date) is not None:
                        e_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S%z")
                    # perhaps no TZ info? add as if UTC
                    else:
                        e_date = datetime.strptime(end_date + "+0000", "%Y-%m-%d %H:%M:%S%z")
                    # convert to UTC
                    e_date = e_date.astimezone(timezone.utc)
                else:
                    e_date = datetime.now(timezone.utc)
                # ensure date range is 90 days or less
                if s_date + timedelta(days=90) < e_date:
                    details = 'Invalid Date Range: start_date --> end_date: range exceeds 90 days'
                    consoleLogger.error(details)
                    return cors_400(details=details)

            except ValueError as exc:
                details = 'Exception: start_date / end_date: {0}'.format(exc)
                consoleLogger.error(details)
                return cors_400(details=details)
            # generate journey_tracker_people_get response
            response = JourneyTrackerPeople()
            response.results = journey_tracker_people_by_start_date(start_date=s_date, end_date=e_date)
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
