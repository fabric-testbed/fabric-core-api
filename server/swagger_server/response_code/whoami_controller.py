import logging
import os
from datetime import datetime, timezone

from swagger_server.models.whoami import Whoami, WhoamiResults  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_500
from swagger_server.response_code.decorators import login_required
from swagger_server.response_code.people_utils import get_person_by_login_claims, update_fabric_person

logger = logging.getLogger(__name__)


@login_required
def whoami_get() -> Whoami:  # noqa: E501
    """Who am I?

    Who am I? # noqa: E501


    :rtype: Whoami
    """
    try:
        # get person from people table
        person = get_person_by_login_claims()
        # check last time the user was updated against COmanage
        now = datetime.now(timezone.utc)
        if person.updated.timestamp() + int(os.getenv('CORE_API_USER_UPDATE_FREQUENCY_IN_SECONDS')) <= now.timestamp():
            logger.info('UPDATE FabricPeople: name={0}, last_updated={1}'.format(person.display_name, person.updated))
            update_fabric_person(fab_person=person)
        # set WhoamiResults object
        whoami = WhoamiResults()
        whoami.active = person.active if person.active else False
        whoami.email = person.preferred_email if person.preferred_email else ''
        whoami.enrolled = True if person.co_person_id else False
        whoami.name = person.display_name if person.display_name else ''
        whoami.uuid = person.uuid if person.uuid else ''
        # set Whoami object and return
        response = Whoami()
        response.results = [whoami]
        response.size = len(response.results)
        response.status = 200
        response.type = 'whoami'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with whoami_get(): {0}'.format(exc)
        logger.error(details)
        return cors_500(details=details)
