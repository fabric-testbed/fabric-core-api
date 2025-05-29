import os
import re
from datetime import datetime, timedelta, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import CoreApiMetrics as CoreApiMetricsModel, \
    EnumCoreApiMetricsTypes, EnumEventTypes
from swagger_server.database.models.people import FabricPeople, Organizations
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.tasktracker import TaskTimeoutTracker
from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.models.core_api_metrics_events import CoreApiMetricsEvents
from swagger_server.response_code.core_api_utils import core_api_events_by_start_date, core_api_events_by_people, core_api_events_by_project
from swagger_server.response_code.cors_response import cors_200, cors_400, cors_401, cors_404, cors_500
from swagger_server.response_code.decorators import login_or_token_required
from swagger_server.response_code.people_utils import get_person_by_login_claims
from swagger_server.response_code.vouch_utils import IdSourceEnum

TZISO = r"^.+\+[\d]{2}:[\d]{2}$"
TZPYTHON = r"^.+\+[\d]{4}$"


@login_or_token_required
def core_api_metrics_events_get(event_type=None, start_date=None, end_date=None):  # noqa: E501
    """Core API metrics events

    Core API metrics events # noqa: E501

    :param event_type: event type
    :type event_type: str
    :param start_date: starting date to search from
    :type start_date: str
    :param end_date: end date to search to
    :type end_date: str

    :rtype: CoreApiMetricsEvents

    {
        "event": "string",
        "event_date": "2025-05-15T17:56:08.339Z",
        "event_triggered_by": "string",
        "event_type": "string",
        "people_uuid": "string",
        "project_is_public": true,
        "project_uuid": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
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
            # query for events
            q_event_type = [EnumEventTypes.people.name, EnumEventTypes.projects.name]
            if event_type == EnumEventTypes.people.name:
                q_event_type = [EnumEventTypes.people.name]
            elif event_type == EnumEventTypes.projects.name:
                q_event_type = [EnumEventTypes.projects.name]
            # generate response
            response = CoreApiMetricsEvents()
            response.results = core_api_events_by_start_date(s_date, e_date, q_event_type)
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.events'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_events_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


@login_or_token_required
def core_api_metrics_events_people_membership_uuid_get(uuid):  # noqa: E501
    """Core API metrics people membership by UUID

    Core API metrics people membership by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsEventsMembership

    {
        "added_by": "string",
        "added_date": "2025-05-15T17:56:46.371Z",
        "membership_type": "string",
        "people_uuid": "string",
        "project_uuid": "string",
        "removed_by": "string",
        "removed_date": "2025-05-15T17:56:46.371Z"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            response = CoreApiMetricsEvents()
            response.results = core_api_events_by_people(people_uuid=uuid)
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.people_events_by_uuid'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_events_people_uuid_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


@login_or_token_required
def core_api_metrics_events_projects_membership_uuid_get(uuid):  # noqa: E501
    """Core API metrics projects membership by UUID

    Core API metrics projects membership by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsEventsMembership

    {
        "added_by": "string",
        "added_date": "2025-05-15T17:57:18.404Z",
        "membership_type": "string",
        "people_uuid": "string",
        "project_uuid": "string",
        "removed_by": "string",
        "removed_date": "2025-05-15T17:57:18.404Z"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            response = CoreApiMetricsEvents()
            response.results = core_api_events_by_project(project_uuid=uuid)
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.project_events_by_uuid'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_events_projects_uuid_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


def core_api_metrics_overview_get() -> CoreApiMetrics:  # noqa: E501
    """Core API metrics overview

    Core API metrics overview # noqa: E501


    :rtype: CoreApiMetrics
    """
    try:
        cam = TaskTimeoutTracker.query.filter_by(name=os.getenv('CAM_NAME')).one_or_none()
        response = CoreApiMetrics()
        if cam.timed_out():
            # retrieve new metrics data
            core_api_metrics = get_core_api_metrics_overview()
            cam.value = None
            cam.last_updated = datetime.now(timezone.utc)
            db.session.commit()
        else:
            # return previous metrics data
            core_api_metrics = CoreApiMetricsModel.query.filter_by(
                metrics_type=EnumCoreApiMetricsTypes.overview.name).one_or_none()
        if core_api_metrics:
            if isinstance(core_api_metrics.json_data, list):
                response.results = core_api_metrics.json_data
            else:
                response.results = [core_api_metrics.json_data]
        else:
            response.results = []

        response.size = len(response.results)
        response.status = 200
        response.type = 'core_api_metrics.overview'
        return cors_200(response_body=response)
    except Exception as exc:
        details = 'Oops! something went wrong with core_api_metrics_overview_get(): {0}'.format(exc)
        consoleLogger.error(details)
        return cors_500(details=details)


def get_core_api_metrics_overview():
    """
    Get Core API metrics overview
    - json_data = db.Column(JSONB, nullable=False)
    - last_updated = db.Column(db.DateTime(timezone=True), nullable=False)
    - metrics_type = db.Column(db.Enum(EnumCoreApiMetricsTypes), ...)

    {
    "results": [
        {
            "last_updated": "2024-04-02 19:50:00.00+00",
            "projects": {
                "active_cumulative": 164,
                "non_active_cumulative": 0
            },
            "users": {
                "active_within_24_hours": 95,
                "active_within_7_days": 218,
                "active_within_30_days": 374,
                "active_within_90_days": 640,
                "active_within_180_days": 959,
                "active_cumulative": 1392,
                "non_active_cumulative": 31
            }
        }
    ],
    "size": 1,
    "status": 200,
    "type": "core_api_metrics.overview"
    }
    """
    # delete prior instances of Core API metrics overview
    metrics_overview = CoreApiMetricsModel.query.filter_by(
        metrics_type=EnumCoreApiMetricsTypes.overview.name).all()
    for m in metrics_overview:
        db.session.delete(m)
    # create new Core API metrics overview
    now = datetime.now(timezone.utc)
    projects_active_cumulative = FabricProjects.query.filter_by(active=True).count()
    projects_non_active_cumulative = FabricProjects.query.filter_by(active=False).count()
    users_active_within_24_hours = FabricPeople.query.filter(
        FabricPeople.updated >= (now - timedelta(hours=24))).count()
    users_active_within_7_days = FabricPeople.query.filter(FabricPeople.updated >= (now - timedelta(days=7))).count()
    users_active_within_30_days = FabricPeople.query.filter(FabricPeople.updated >= (now - timedelta(days=30))).count()
    users_active_within_90_days = FabricPeople.query.filter(FabricPeople.updated >= (now - timedelta(days=90))).count()
    users_active_within_180_days = FabricPeople.query.filter(
        FabricPeople.updated >= (now - timedelta(days=180))).count()
    users_active_cumulative = FabricPeople.query.filter_by(active=True).count()
    users_non_active_cumulative = FabricPeople.query.filter_by(active=False).count()
    core_api_metrics = CoreApiMetricsModel()
    core_api_metrics.last_updated = str(now)
    core_api_metrics.json_data = {
        "last_updated": str(now),
        "projects": {
            "active_cumulative": projects_active_cumulative,
            "non_active_cumulative": projects_non_active_cumulative
        },
        "users": {
            "active_within_24_hours": users_active_within_24_hours,
            "active_within_7_days": users_active_within_7_days,
            "active_within_30_days": users_active_within_30_days,
            "active_within_90_days": users_active_within_90_days,
            "active_within_180_days": users_active_within_180_days,
            "active_cumulative": users_active_cumulative,
            "non_active_cumulative": users_non_active_cumulative
        }
    }
    core_api_metrics.metrics_type = "overview"
    db.session.add(core_api_metrics)
    db.session.commit()

    return core_api_metrics


@login_or_token_required
def core_api_metrics_people_get():  # noqa: E501
    """Core API metrics people

    Core API metrics people # noqa: E501

    :rtype: CoreApiMetricsPeople

    {
        "results": [
            {
                "active": true,
                "google_scholar": "string",
                "last_updated": "2025-05-09T18:40:38.836Z",
                "scopus": "string",
                "uuid": "string"
            }
        ],
        "size": 1,
        "status": 200,
        "type": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            response = CoreApiMetrics()
            fabric_people = FabricPeople.query.order_by(FabricPeople.uuid).all()
            people_results = []
            for p in fabric_people:
                google_scholar = None
                scopus = None
                for pr in p.profile.other_identities:
                    if pr.type == 'google_scholar':
                        google_scholar = pr.identity
                    if pr.type == 'scopus':
                        scopus = pr.identity
                person = {
                    'active': bool(p.active),
                    'google_scholar': google_scholar,
                    'last_updated': str(p.modified),
                    'scopus': scopus,
                    'uuid': str(p.uuid)
                }
                people_results.append(person)
            response.results = people_results
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.people'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_people_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


@login_or_token_required
def core_api_metrics_people_details_uuid_get(uuid):  # noqa: E501
    """Core API metrics people details by UUID

    Core API metrics people details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsPeopleOne

    {
        "results": [
            {
                "active": true,
                "affiliation": "string",
                "email": "string",
                "google_scholar": "string",
                "last_updated": "2025-05-09T20:03:24.290Z",
                "name": "string",
                "registered_on": "2025-05-09T20:03:24.290Z",
                "roles": [
                    {
                        "description": "string",
                        "name": "string"
                    },
                    ...
                ],
                "scopus": "string",
                "uuid": "string"
            }
        ],
        "size": 1,
        "status": 200,
        "type": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    print(id_source)
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            # get person by uuid
            fabric_person = FabricPeople.query.filter_by(uuid=uuid).one_or_none()
            if not fabric_person:
                return cors_404(details="No match for Person with uuid = '{0}'".format(uuid))
            # fabric person has been found
            response = CoreApiMetrics()
            google_scholar = None
            scopus = None
            for pr in fabric_person.profile.other_identities:
                if pr.type == 'google_scholar':
                    google_scholar = pr.identity
                if pr.type == 'scopus':
                    scopus = pr.identity
            roles = []
            for r in fabric_person.roles:
                roles.append({'name': r.name, 'description': r.description})
            roles = sorted(roles, key=lambda d: (d.get('name')).casefold())
            person = {
                'active': bool(fabric_person.active),
                'affiliation': Organizations.query.filter_by(
                    id=fabric_person.org_affiliation).one_or_none().organization,
                'email': fabric_person.preferred_email,
                'google_scholar': google_scholar,
                'last_updated': str(fabric_person.modified),
                'name': fabric_person.display_name,
                'registered_on': str(fabric_person.registered_on),
                'roles': roles,
                'scopus': scopus,
                'uuid': str(fabric_person.uuid)
            }
            response.results = [person]
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.people_one'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_people_uuid_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


@login_or_token_required
def core_api_metrics_projects_get():  # noqa: E501
    """Core API metrics projects

    Core API metrics projects # noqa: E501


    :rtype: CoreApiMetricsProjects

    {
        "results": [
            {
                "active": true,
                "last_updated": "2025-05-09T20:04:38.272Z",
                "project_is_public": true,
                "project_type": "string",
                "uuid": "string"
            }
        ],
        "size": 1,
        "status": 200,
        "type": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    print(id_source)
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            response = CoreApiMetrics()
            fabric_projects = FabricProjects.query.order_by(FabricProjects.uuid).all()
            project_results = []
            for p in fabric_projects:
                project = {
                    'active': bool(p.active),
                    'last_updated': str(p.modified),
                    'project_is_pubic': bool(p.is_public),
                    'project_type': p.project_type.name,
                    'uuid': str(p.uuid)
                }
                project_results.append(project)
            response.results = project_results
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.projects'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_projects_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )


@login_or_token_required
def core_api_metrics_projects_details_uuid_get(uuid):  # noqa: E501
    """Core API metrics projects details by UUID

    Core API metrics projects details by UUID # noqa: E501

    :param uuid: universally unique identifier
    :type uuid: str

    :rtype: CoreApiMetricsProjectsOne

    {
        "results": [
            {
                "active": true,
                "communities": [
                    "string"
                ],
                "created_by": "string",
                "created_date": "2025-05-09T20:05:15.300Z",
                "expires_on": "2025-05-09T20:05:15.300Z",
                "last_updated": "2025-05-09T20:05:15.300Z",
                "name": "string",
                "project_is_public": true,
                "project_type": "string",
                "retired_date": "2025-05-09T20:05:15.300Z",
                "storage": [
                    "string"
                ],
                "tags": [
                    "string"
                ],
                "uuid": "string"
            }
        ],
        "size": 1,
        "status": 200,
        "type": "string"
    }
    """
    # get api_user
    api_user, id_source = get_person_by_login_claims()
    print(id_source)
    if id_source is IdSourceEnum.SERVICES.value or api_user.is_facility_operator() or api_user.is_facility_viewer():
        try:
            # get project by uuid
            fabric_project = FabricProjects.query.filter_by(uuid=uuid).one_or_none()
            if not fabric_project:
                return cors_404(details="No match for Project with uuid = '{0}'".format(uuid))
            # fabric project has been found
            response = CoreApiMetrics()
            project = {
                'active': bool(fabric_project.active),
                'communities': [c.community for c in fabric_project.communities],
                'created_date': str(fabric_project.created),
                'expires_on': str(fabric_project.expires_on),
                'last_updated': str(fabric_project.modified),
                'name': fabric_project.name,
                'project_is_pubic': bool(fabric_project.is_public),
                'project_creators': [p.uuid for p in fabric_project.project_creators],
                'project_members': [p.uuid for p in fabric_project.project_members],
                'project_owners': [p.uuid for p in fabric_project.project_owners],
                'project_type': fabric_project.project_type.name,
                'retired_date': str(fabric_project.retired_date) if fabric_project.retired_date else None,
                'storage': [s.uuid for s in fabric_project.project_storage],
                'tags': [t.tag for t in fabric_project.tags],
                'token_holders': [p.uuid for p in fabric_project.token_holders],
                'uuid': str(fabric_project.uuid)
            }
            response.results = [project]
            response.size = len(response.results)
            response.status = 200
            response.type = 'core_api_metrics.projects_one'
            return cors_200(response_body=response)
        except Exception as exc:
            details = 'Oops! something went wrong with core_api_metrics_projects_uuid_get(): {0}'.format(exc)
            consoleLogger.error(details)
            return cors_500(details=details)
    else:
        return cors_401(
            details="Permission Denied: must be fabric read-only service user or fabric facility operator",
        )
