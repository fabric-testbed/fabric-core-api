from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin, TrackingMixin
from sqlalchemy.dialects.postgresql import JSONB


class FabricTestbedInfo(BaseMixin, TimestampMixin, TrackingMixin, db.Model):
    """
    TestbedInfo - Read only information regarding testbed state for remote tools (* denotes required)
    - * created - timestamp created (TimestampMixin)
    - * created_by_uuid - string (TrackingMixin)
    - * is_active - boolean
    - * json_data - JSON field data
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - string (TrackingMixin)
    - * uuid - unique universal identifier
    """
    query: db.Query
    __tablename__ = 'testbed_info'
    __allow_unmapped__ = True

    is_active = db.Column(db.Boolean, default=True)
    json_data = db.Column(JSONB, nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
