import uuid
from datetime import datetime, timedelta, timezone
from typing import Union

from dateutil import parser

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import CoreApiEvents, EnumEvents


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
    Add core api event
    NOTE - ALL validation needs to take place prior to calling this function

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


def core_api_events_by_start_date(start_date: datetime = None, end_date: datetime = None,
                                  event_type: list[str] = None) -> list[str]:
    events = []
    results = CoreApiEvents.query.filter(
        CoreApiEvents.event_date >= start_date,
        CoreApiEvents.event_date <= end_date,
        CoreApiEvents.event_type.in_(event_type)
    ).order_by(CoreApiEvents.event_date.asc()).all()
    for res in results:
        try:
            e = {
                'event': res.event.name,
                'event_date': str(res.event_date),
                'event_triggered_by': res.event_triggered_by,
                'event_type': res.event_type.name,
                'people_uuid': res.people_uuid,
                'project_is_public': res.project_is_public,
                'project_uuid': res.project_uuid
            }
            events.append(e)
        except Exception as exc:
            consoleLogger.error('core_api_utils.core_api_events_by_start_date: {0}'.format(exc))
    consoleLogger.info('core_api_utils.core_api_events_by_start_date: {0} records returned'.format(len(events)))
    return events


def core_api_events_by_people(people_uuid: str = None) -> list[str]:
    """
    {
        "added_by": "string",
        "added_date": "2025-05-27T20:03:24.232Z",
        "membership_type": "string",
        "people_uuid": "string",
        "project_uuid": "string",
        "removed_by": "string",
        "removed_date": "2025-05-27T20:03:24.232Z"
    }
    """
    events = []
    results = CoreApiEvents.query.filter(
        CoreApiEvents.people_uuid == people_uuid,
    ).order_by(CoreApiEvents.event_date.asc()).all()
    for res in results:
        # project_add_{creator,memmber,owner,tokenholder}
        if res.event.name in [EnumEvents.project_add_creator.name, EnumEvents.project_add_member.name,
                              EnumEvents.project_add_owner.name, EnumEvents.project_add_tokenholder.name]:
            try:
                e = {
                    'added_by': res.event_triggered_by,
                    'added_date': str(res.event_date),
                    'membership_type': str(res.event.name).replace('project_add_', ''),
                    'people_uuid': res.people_uuid,
                    'project_uuid': res.project_uuid,
                    'removed_by': None,
                    'removed_date': None
                }
                events.append(e)
            except Exception as exc:
                consoleLogger.error('core_api_utils.core_api_events_by_people: {0}'.format(exc))
        # project_remove_{creator,memmber,owner,tokenholder}
        if res.event.name in [EnumEvents.project_remove_creator.name, EnumEvents.project_remove_member.name,
                              EnumEvents.project_remove_owner.name, EnumEvents.project_remove_tokenholder.name]:
            # find corresponding add
            add_found = False
            membership_type = str(res.event.name).replace('project_remove_', '')
            for idx, item in enumerate(events):
                if ((item.get('people_uuid') == res.people_uuid and item.get('project_uuid') == res.project_uuid
                    and item.get('membership_type') == membership_type) and not item.get('removed_by')
                        and not item.get('removed_date')):
                    # update existing record with remove
                    events[idx]['removed_by'] = res.event_triggered_by
                    events[idx]['removed_date'] = str(res.event_date)
                    add_found = True
                    break
            if not add_found:
                consoleLogger.error('core_api_utils.core_api_events_by_people: match error event ID: {0}'.format(res.id))

    consoleLogger.info('core_api_utils.core_api_events_by_people: {0} records returned'.format(len(events)))
    return events


def core_api_events_by_project(project_uuid: str = None) -> list[str]:
    """
    {
        "added_by": "string",
        "added_date": "2025-05-27T20:03:24.232Z",
        "membership_type": "string",
        "people_uuid": "string",
        "project_uuid": "string",
        "removed_by": "string",
        "removed_date": "2025-05-27T20:03:24.232Z"
    }
    """
    events = []
    results = CoreApiEvents.query.filter(
        CoreApiEvents.project_uuid == project_uuid,
    ).order_by(CoreApiEvents.event_date.asc()).all()
    for res in results:
        # project_add_{creator,memmber,owner,tokenholder}
        if res.event.name in [EnumEvents.project_add_creator.name, EnumEvents.project_add_member.name,
                              EnumEvents.project_add_owner.name, EnumEvents.project_add_tokenholder.name]:
            try:
                e = {
                    'added_by': res.event_triggered_by,
                    'added_date': str(res.event_date),
                    'membership_type': str(res.event.name).replace('project_add_', ''),
                    'people_uuid': res.people_uuid,
                    'project_uuid': res.project_uuid,
                    'removed_by': None,
                    'removed_date': None
                }
                events.append(e)
            except Exception as exc:
                consoleLogger.error('core_api_utils.core_api_events_by_project: {0}'.format(exc))
        # project_remove_{creator,memmber,owner,tokenholder}
        if res.event.name in [EnumEvents.project_remove_creator.name, EnumEvents.project_remove_member.name,
                              EnumEvents.project_remove_owner.name, EnumEvents.project_remove_tokenholder.name]:
            # find corresponding add
            add_found = False
            membership_type = str(res.event.name).replace('project_remove_', '')
            for idx, item in enumerate(events):
                if ((item.get('people_uuid') == res.people_uuid and item.get('project_uuid') == res.project_uuid
                    and item.get('membership_type') == membership_type) and not item.get('removed_by')
                        and not item.get('removed_date')):
                    # update existing record with remove
                    events[idx]['removed_by'] = res.event_triggered_by
                    events[idx]['removed_date'] = str(res.event_date)
                    add_found = True
                    break
            if not add_found:
                consoleLogger.error('core_api_utils.core_api_events_by_project: match error event ID: {0}'.format(res.id))

    consoleLogger.info('core_api_utils.core_api_events_by_project: {0} records returned'.format(len(events)))
    return events
