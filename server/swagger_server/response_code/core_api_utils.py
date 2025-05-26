import uuid
from datetime import datetime, timedelta, timezone
from typing import Union

from dateutil import parser

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import CoreApiEvents


def normalize_date_to_utc(date_str: str, return_type: str = None) -> Union[None, str, datetime]:
    try:
        date_parsed = parser.parse(date_str) + timedelta(milliseconds=100)
        date_parsed = date_parsed - timedelta(milliseconds=100)
        date_parsed = date_parsed.astimezone(timezone.utc)
    except Exception as exc:
        print(exc)
        return None
    if return_type and return_type.casefold() == 'str':
        return date_parsed.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    else:
        return date_parsed


def is_valid_uuid(val) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def add_core_api_event(event, event_date, event_triggered_by, event_type, people_uuid, project_is_public, project_uuid):
    """
    Add core api event - all validation should be done before calling this function

    CoreApiEvents
    - event - string
    - event_date - datetime
    - event_triggered_by - string
    - event_type - string
    - people_uuid - string
    - project_is_public - boolean
    - project_uuid - string
    """
    try:
        core_api_event = CoreApiEvents()
        core_api_event.event = event
        core_api_event.event_date = event_date
        core_api_event.event_triggered_by = event_triggered_by
        core_api_event.event_type = event_type
        core_api_event.people_uuid = people_uuid
        core_api_event.project_is_public = project_is_public
        core_api_event.project_uuid = project_uuid
        db.session.add(core_api_event)
        db.session.commit()
        consoleLogger.info('Event added: {0}:{1} by {2}'.format(event_type, event, event_triggered_by))
    except Exception as exc:
        db.session.rollback()
        consoleLogger.error(exc)
