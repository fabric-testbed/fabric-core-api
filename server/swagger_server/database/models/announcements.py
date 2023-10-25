import enum

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin, TrackingMixin


# Enum for Announcement type
class EnumAnnouncementTypes(enum.Enum):
    carousel = 0
    facility = 1
    maintenance = 2
    news = 3


class FabricAnnouncements(BaseMixin, TimestampMixin, TrackingMixin, db.Model):
    """
    Announcements - Facility or Maintenance announcements (* denotes required)
    - * announcement_type - [carousel, facility, maintenance, news]
    - background_image_url - string
    - button - string
    - * content - string
    - * created - timestamp created (TimestampMixin)
    - * created_by_uuid - string (TrackingMixin)
    - display_date - timestamp
    - end_date - timestamp
    - * id - primary key (BaseMixin)
    - is_active - boolean
    - link - string
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - string (TrackingMixin)
    - sequence - integer
    - * start_date - timestamp
    - * title - string
    - * uuid - unique universal identifier
    """
    query: db.Query
    __tablename__ = 'announcements'
    __allow_unmapped__ = True

    announcement_type = db.Column(db.Enum(EnumAnnouncementTypes),
                                  default=EnumAnnouncementTypes.facility, nullable=False)
    background_image_url = db.Column(db.String(), nullable=True)
    button = db.Column(db.String(), nullable=True)
    content = db.Column(db.String(), nullable=False)
    display_date = db.Column(db.DateTime(timezone=True), nullable=True)
    end_date = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    link = db.Column(db.String(), nullable=True)
    sequence = db.Column(db.Integer(), nullable=True)
    start_date = db.Column(db.DateTime(timezone=True), nullable=True)
    title = db.Column(db.String(), nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
