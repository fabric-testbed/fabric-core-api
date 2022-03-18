from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


class ApiVersion(BaseMixin, TimestampMixin, db.Model):
    """
    - active - version status
    - created - timestamp created (TimestampMixin)
    - id - primary key (BaseMixin)
    - modified - timestamp modified (TimestampMixin)
    - reference - api reference URL from GitHub
    - version - api version tag from GitHub
    """
    __tablename__ = 'version'

    active = db.Column(db.Boolean, nullable=False, default=True)
    reference = db.Column(db.String(), nullable=False)
    version = db.Column(db.String(), nullable=False)
