from datetime import datetime, timezone

from swagger_server.database.db import db


class BaseMixin(object):
    id = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TimestampMixin(object):
    created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TrackingMixin(object):
    created_by_uuid = db.Column(db.String(), nullable=True)
    modified_by_uuid = db.Column(db.String(), nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
