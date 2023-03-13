import enum

from sqlalchemy.schema import Index

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


# Enum for SSH Keys type
class EnumSshKeyTypes(enum.Enum):
    bastion = 1
    sliver = 2


# Enum for SSH Keys status
class EnumSshKeyStatus(enum.Enum):
    active = 1
    deactivated = 2
    expired = 3


class FabricSshKeys(BaseMixin, TimestampMixin, db.Model):
    """
    SshKeys - Bastion and Sliver keys (* denotes required)
    - comment:
    - * created - timestamp created (TimestampMixin)
    - #created_on:
    - deactivated_on:
    - deactivation_reason:
    - description:
    - * expires_on:
    - * fabric_key_type: [bastion, sliver]
    - fingerprint:
    - * id - primary key (BaseMixin)
    - key_uuid:
    - modified - timestamp modified (TimestampMixin)
    - * people_id - foreignkey link to people table
    - public_key:
    - public_openssh:
    - * ssh_key_type:
    - * status: [active, deactivated, expired]
    - * uuid - unique universal identifier
    """
    query: db.Query
    __tablename__ = 'sshkeys'
    __table_args__ = (db.UniqueConstraint('public_key', 'people_id', name='constraint_sshkeys'),)
    __allow_unmapped__ = True

    # When received from user or returned to them
    # SSH public key has name, public_key and label in that order
    # e.g. 'ssh-dss <base 64 encoded public key> mykey'
    active = db.Column(db.Boolean, default=True, nullable=False)
    comment = db.Column(db.String())
    deactivated_on = db.Column(db.DateTime(timezone=True), nullable=True)
    deactivated_reason = db.Column(db.String())
    description = db.Column(db.String())
    expires_on = db.Column(db.DateTime(timezone=True), nullable=False)
    fabric_key_type = db.Column(db.Enum(EnumSshKeyTypes), default=EnumSshKeyTypes.sliver, nullable=False)
    fingerprint = db.Column(db.String())
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    public_key = db.Column(db.String())
    ssh_key_type = db.Column(db.String())
    status = db.Column(db.Enum(EnumSshKeyStatus), default=EnumSshKeyStatus.active, nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)


Index('idx_owner_keyid_keytype', 'people_id', 'uuid', 'ssh_key_type')
Index('idx_owner_fingerprint', 'people_id', 'fingerprint')
