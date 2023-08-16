from datetime import datetime, timedelta, timezone

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin


class TaskTimeoutTracker(BaseMixin, db.Model):
    """
    Task Timeout Tracker
    - description
    - * id - primary key (BaseMixin)
    - last_updated
    - name
    - timeout_in_seconds
    - uuid
    - value
    """
    query: db.Query
    __tablename__ = 'task_timeout_tracker'
    __allow_unmapped__ = True

    description = db.Column(db.String(), nullable=False)
    last_updated = db.Column(db.DateTime(timezone=True), nullable=False)
    name = db.Column(db.String(), nullable=False)
    timeout_in_seconds = db.Column(db.Integer, nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
    value = db.Column(db.String(), nullable=True)

    def __str__(self):
        return self.name

    def timed_out(self) -> bool:
        if datetime.now(timezone.utc) > (self.last_updated + timedelta(seconds=int(self.timeout_in_seconds))):
            return True
        else:
            return False
