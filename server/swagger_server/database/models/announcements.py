import enum

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


# Enum for Announcement type
class EnumAnnouncementTypes(enum.Enum):
    facility = 1
    maintenance = 2


class FabricAnnouncements(BaseMixin, TimestampMixin, db.Model):
    """
    Announcements - Facility or Maintenance announcements (* denotes required)
    - button - string
    - * content - string
    - * created - timestamp created (TimestampMixin)
    - display_date - timestamp
    - end_date - timestamp
    - * id - primary key (BaseMixin)
    - is_active - boolean
    - link - string
    - modified - timestamp modified (TimestampMixin)
    - * start_date - timestamp
    - * title - string
    - * type - [facility, maintenance]
    - * uuid - unique universal identifier
    """
    query: db.Query
    __tablename__ = 'announcements'

    button = db.Column(db.String())
    content = db.Column(db.String(), nullable=False)
    display_date = db.Column(db.DateTime(timezone=True), nullable=True)
    end_date = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    link = db.Column(db.String())
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    title = db.Column(db.String(), nullable=False)
    type = db.Column(db.Enum(EnumAnnouncementTypes), default=EnumAnnouncementTypes.facility, nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
