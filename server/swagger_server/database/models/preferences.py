import enum

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


class EnumPreferenceTypes(enum.Enum):
    people = 'people'
    projects = 'projects'
    profile_people = 'profile_people'
    profile_projects = 'profile_projects'


class FabricPreferences(BaseMixin, TimestampMixin, db.Model):
    """
    Table format
    - created - timestamp created (TimestampMixin)
    - id - primary key (BaseMixin)
    - key - string
    - modified - timestamp modified (TimestampMixin)
    - people_id - foriegnkey to fabric_people (nullable)
    - projects_id - foriegnkey to fabric_projects (nullable)
    - type - string:['people', 'projects', 'profile_people', 'profile_projects']
    - value - boolean
    """
    __tablename__ = 'preferences'

    key = db.Column(db.String(), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    profile_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    profile_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    type = db.Column(db.Enum(EnumPreferenceTypes), default=EnumPreferenceTypes.people, nullable=False)
    value = db.Column(db.Boolean, default=True, nullable=False)
