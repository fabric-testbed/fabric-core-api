import os
from datetime import datetime, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.models.whoami import Whoami, WhoamiResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_401, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims, update_fabric_person
from swagger_server.response_code.whoami_utils import get_vouch_session_expiry


@login_required
def whoami_get() -> Whoami:  # noqa: E501
    """Who am I?

    Who am I? # noqa: E501


    :rtype: Whoami
    """
    try:
        # get person from people table
        person = get_person_by_login_claims()
        if not person.co_person_id:
            details = 'Enrollment required: {0}'.format(os.getenv('CORE_API_401_UNAUTHORIZED_TEXT'))
            consoleLogger.info("unauthorized_access(): {0}".format(details))
            return cors_401(details=details)
        # check last time the user was updated against COmanage
        now = datetime.now(timezone.utc)
        try:
            if person.updated.timestamp() + int(
                    os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')) <= now.timestamp():
                consoleLogger.info(
                    'UPDATE FabricPeople: name={0}, last_updated={1}'.format(person.display_name, person.updated))
                update_fabric_person(fab_person=person)
        except Exception as exc:
            consoleLogger.info(
                'UPDATE FabricPeople: name={0}, last_updated=None - {1}'.format(person.display_name, exc))
            update_fabric_person(fab_person=person)
        # set WhoamiResults object
        whoami = WhoamiResults()
        whoami.active = person.active if person.active else False
        whoami.email = person.preferred_email if person.preferred_email else ''
        whoami.enrolled = True if person.co_person_id else False
        whoami.name = person.display_name if person.display_name else ''
        whoami.uuid = str(person.uuid) if person.uuid else ''
        whoami.vouch_expiry = get_vouch_session_expiry()
        # set Whoami object and return
        response = Whoami()
        response.results = [whoami]
        response.size = len(response.results)
        response.status = 200
        response.type = 'whoami'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with whoami_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)
