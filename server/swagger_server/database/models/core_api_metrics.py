import enum
from email.policy import default

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Index

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin


# Enum for SSH Keys type
class EnumCoreApiMetricsTypes(enum.Enum):
    overview = 1
    advanced = 2

class CoreApiMetrics(BaseMixin, db.Model):
    """
    CoreApiMetrics - Read only information regarding Core-API metrics for remote tools
    - json_data - JSON field data
    - last_updated - timestamp data was last updated at
    - metrics_type: [overview, advanced]
    """
    query: db.Query
    __tablename__ = 'core_api_metrics'
    __allow_unmapped__ = True

    json_data = db.Column(JSONB, nullable=False)
    last_updated = db.Column(db.DateTime(timezone=True), nullable=False)
    metrics_type = db.Column(db.Enum(EnumCoreApiMetricsTypes), default=EnumCoreApiMetricsTypes.overview, nullable=False)

class EnumEvents(enum.Enum):
    people_create = "People Create"
    people_retire = "People Retire"
    people_unretire = "People Un-retire"
    project_create = "Project Create"
    project_retire = "Project Retire"
    project_unretire = "Project Un-retire"
    project_add_creator = "Project add Creator"
    project_remove_creator = "Project remove Creator"
    project_add_member = "Project add Member"
    project_remove_member = "Project remove Member"
    project_add_owner = "Project add Owner"
    project_remove_owner = "Project remove Owner"
    project_add_tokenholder = "Project add Token-holder"
    project_remove_tokenholder = "Project remove Token-holder"

class EnumEventTypes(enum.Enum):
    people = "People"
    projects = "Projects"

class CoreApiEvents(BaseMixin, db.Model):
    """
    event - string
    event_date - datetime
    event_triggered_by - string
    event_type - string
    people_uuid - string
    project_is_public - boolean
    project_uuid - string
    """
    __tablename__ = 'core_api_events'
    __allow_unmapped__ = True

    event = db.Column(db.Enum(EnumEvents), default=EnumEvents.project_add_member.name, nullable=False)
    event_date = db.Column(db.DateTime(timezone=True), nullable=False)
    event_triggered_by = db.Column(db.String, nullable=False)
    event_type = db.Column(db.Enum(EnumEventTypes), default=EnumEventTypes.projects.name, nullable=False)
    people_uuid = db.Column(db.String, nullable=False)
    project_is_public = db.Column(db.Boolean, nullable=True)
    project_uuid = db.Column(db.String, nullable=True)

    __table_args__ = (
        Index(
            "idx_events_people_projects",
            "event_date",
            "event",
            "people_uuid",
            "project_uuid",
            unique=True,
            postgresql_where=project_uuid.isnot(None)
        ),
        Index(
            "idx_events_people_only",
            "event_date",
            "event",
            "people_uuid",
            unique=True,
            postgresql_where=project_uuid.is_(None)
        ),
    )