import enum

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


class EnumPreferenceTypes(enum.Enum):
    people = 1
    projects = 2
    profiles_people = 3
    profiles_projects = 4


class FabricPreferences(BaseMixin, TimestampMixin, db.Model):
    """
    Table format
    - created - timestamp created (TimestampMixin)
    - id - primary key (BaseMixin)
    - * key - string
    - modified - timestamp modified (TimestampMixin)
    - people_id - foreignkey link to people table (nullable)
    - profiles_people_id - foreignkey link to profiles_people table (nullable)
    - profiles_projects_id - foreignkey link to profiles_projects table (nullable)
    - projects_id - foreignkey link to projects table (nullable)
    - * type - string:['people', 'projects', 'profiles_people', 'profiles_projects']
    - * value - boolean
    """
    query: db.Query
    __tablename__ = 'preferences'

    key = db.Column(db.String(), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    profiles_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    type = db.Column(db.Enum(EnumPreferenceTypes), nullable=False)
    value = db.Column(db.Boolean, default=True, nullable=False)
