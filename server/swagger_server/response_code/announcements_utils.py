from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.database.db import db
from swagger_server.database.models.announcements import FabricAnnouncements
from swagger_server.database.models.people import FabricPeople
from swagger_server.models.announcements_post import AnnouncementsPost
from swagger_server.response_code.core_api_utils import normalize_date_to_utc


def create_fabric_announcement_from_api(body: AnnouncementsPost, creator: FabricPeople) -> FabricAnnouncements:
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

    {
        "announcement_type": "carousel",
        "background_image_url": "string",
        "button": "string",
        "content": "string",
        "display_date": "2022-08-07T15:08:37.246Z",
        "end_date": "2022-08-07T15:08:37.246Z",
        "is_active": true,
        "link": "string",
        "sequence": integer
        "start_date": "2022-08-07T15:08:37.246Z",
        "title": "string"
    }
    """
    # create Announcement
    now = datetime.now(timezone.utc)
    fab_announcement = FabricAnnouncements()
    fab_announcement.announcement_type = body.announcement_type
    fab_announcement.background_image_url = body.background_image_url if body.background_image_url else None
    fab_announcement.button = body.button if body.button else None
    fab_announcement.content = body.content
    fab_announcement.created = now
    fab_announcement.created_by_uuid = str(creator.uuid)
    fab_announcement.display_date = normalize_date_to_utc(date_str=body.display_date) if body.display_date else None
    fab_announcement.end_date = normalize_date_to_utc(date_str=body.end_date) if body.end_date else None
    fab_announcement.is_active = body.is_active
    fab_announcement.link = body.link
    fab_announcement.modified = now
    fab_announcement.modified_by_uuid = str(creator.uuid)
    fab_announcement.sequence = int(body.sequence) if body.sequence else None
    fab_announcement.start_date = normalize_date_to_utc(
        date_str=body.start_date) if body.start_date else normalize_date_to_utc(date_str=str(now))
    fab_announcement.title = body.title
    fab_announcement.uuid = uuid4()
    db.session.add(fab_announcement)
    db.session.commit()

    return fab_announcement
