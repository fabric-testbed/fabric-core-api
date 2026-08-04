from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin, TrackingMixin


class FabricStorage(BaseMixin, TimestampMixin, TrackingMixin, db.Model):
    """
    Storage - Allocated storage volumes on specific sites for specific projects (* denotes required)
    - * active - boolean denoting active state
    - * created - timestamp created (TimestampMixin)
    - * created_by_uuid - uuid of person created_by (TrackingMixin)
    - expires_on - expiry date
    - * id - primary key (BaseMixin)
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - uuid of person modified_by (TrackingMixin)
    - * project_id - foreignkey link to project table
    - * requested_by_id - foreignkey link to people table
    - sites - array of site names
    - * uuid - unique universal identifier
    - * volume_name - name of volume
    - volume_size_gb - size of volume in GB

    rules:
    - can only be created/updated/deleted by facility operators (POST/PATCH/DELETE)
    - can only be read by project creator/owner/member roles or facility operators (GET)
    """
    query: db.Query
    __tablename__ = 'storage'
    __table_args__ = (db.UniqueConstraint('project_id', 'volume_name', name='constraint_storage'),)
    __allow_unmapped__ = True

    active = db.Column(db.Boolean, default=True, nullable=False)
    expires_on = db.Column(db.DateTime(timezone=True), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    sites = db.relationship('StorageSites', backref='storage', lazy=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
    volume_name = db.Column(db.String())
    volume_size_gb = db.Column(db.Integer, nullable=True)


class StorageSites(BaseMixin, db.Model):
    """
    - id - primary key (BaseMixin)
    - storage_id - foreignkey link to storage table
    - site - site as string
    """
    query: db.Query
    __tablename__ = 'storage_sites'
    __table_args__ = (db.UniqueConstraint('storage_id', 'site', name='constraint_storage_sites'),)
    __allow_unmapped__ = True

    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'), nullable=False)
    site = db.Column(db.Text, nullable=False)
