import os

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin, TrackingMixin

projects_creators = db.Table('projects_creators',
                             db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
                             db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
                             )

projects_members = db.Table('projects_members',
                            db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
                            db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
                            )

projects_owners = db.Table('projects_owners',
                           db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
                           db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
                           )


class FabricProjects(BaseMixin, TimestampMixin, TrackingMixin, db.Model):
    """
    - active - project status
    - created - timestamp created (TimestampMixin)
    - created_by_uuid - uuid of person created_by (TrackingMixin)
    - description - project description
    - facility - project facility (default = FABRIC)
    - id - primary key (BaseMixin)
    - is_public - show/hide project in all public interfaces (default: True)
    - modified - timestamp modified (TimestampMixin)
    - modified_by_uuid - uuid of person modified_by (TrackingMixin)
    - name - project name
    - preferences - array of preference booleans
    - profile - foreignkey link to profile_projects
    - project_creators - one-to-many people (initially one person)
    - project_members - one-to-many people
    - project_owners - one-to-many people
    - tags - array of tag strings
    - uuid - unique universal identifier
    """
    __tablename__ = 'projects'

    active = db.Column(db.Boolean, default=True, nullable=False)
    co_cou_id_pc = db.Column(db.Integer, nullable=True)
    co_cou_id_pm = db.Column(db.Integer, nullable=True)
    co_cou_id_po = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=False)
    facility = db.Column(db.String(), default=os.getenv('CORE_API_DEFAULT_FACILITY'), nullable=False)
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    name = db.Column(db.String(), nullable=False)
    preferences = db.relationship('FabricPreferences', backref='projects', lazy=True)
    profile = db.relationship('FabricProfilesProjects', backref='projects', uselist=False, lazy=True)
    project_creators = db.relationship('FabricPeople', secondary=projects_creators, lazy='subquery',
                                       backref=db.backref('project_creators', lazy=True))
    project_members = db.relationship('FabricPeople', secondary=projects_members, lazy='subquery',
                                      backref=db.backref('project_members', lazy=True))
    project_owners = db.relationship('FabricPeople', secondary=projects_owners, lazy='subquery',
                                     backref=db.backref('project_owners', lazy=True))
    # publications = db.relationship('Publications', secondary=publications, lazy='subquery',
    #                                backref=db.backref('projects', lazy=True))
    tags = db.relationship('ProjectsTags', backref='projects', lazy=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)


class ProjectsTags(BaseMixin, db.Model):
    """
    - id - primary key (BaseMixin)
    - projects_id - foreignkey link to projects table
    - tag - tag as string
    """
    __tablename__ = 'projects_tags'

    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    tag = db.Column(db.Text, nullable=False)
