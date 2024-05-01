import os
from datetime import datetime, timedelta, timezone

from swagger_server.api_logger import consoleLogger
from swagger_server.database.db import db
from swagger_server.database.models.core_api_metrics import CoreApiMetrics as CoreApiMetricsModel, \
    EnumCoreApiMetricsTypes
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.tasktracker import TaskTimeoutTracker
from swagger_server.models.core_api_metrics import CoreApiMetrics  # noqa: E501
from swagger_server.response_code.cors_response import cors_200, cors_500


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
