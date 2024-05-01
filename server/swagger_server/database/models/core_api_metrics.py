import enum

from sqlalchemy.dialects.postgresql import JSONB

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
