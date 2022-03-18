import enum

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


# Enum for external pages type
class EnumExternalPageTypes(enum.Enum):
    professional = 'professional'
    social = 'social'


class FabricProfilesPeople(BaseMixin, TimestampMixin, db.Model):
    """
    - bio - short bio
    - created - timestamp created (TimestampMixin)
    - cv - Link to a CV or resume. (Later it might be nice if this could be stored on the Portal)
    - external_pages - external links for social and professional pages
        - professional - Links to professional pages on resources such as LinkedIn, Twitter, Youtube, Github
        - social - Links to personal pages on resources such as LinkedIn, Twitter, Youtube, Github
    - id - primary key (BaseMixin)
    - identities - IDs from other identity services such as ORCID, Google Scholar
    - job - Role/job/position
    - modified - timestamp modified (TimestampMixin)
    - people_id - foreignkey to people table
    - pronouns - personal pronouns used
    - uuid - unique universal identifier
    - website - Link to a personal website
    """
    __tablename__ = 'profiles_people'

    bio = db.Column(db.String(), nullable=True)
    cv = db.Column(db.String(), nullable=True)
    external_pages = db.relationship('ProfilesExternalPages', backref='profiles_people', lazy=True)
    job = db.Column(db.String(), nullable=True)
    other_identities = db.relationship('ProfilesOtherIdentities', backref='profiles_people', lazy=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    preferences = db.relationship('FabricPreferences', backref='profiles_people', lazy=True)
    pronouns = db.Column(db.String(), nullable=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)
    website = db.Column(db.String(), nullable=True)


class FabricProfilesProjects(BaseMixin, TimestampMixin, db.Model):
    """
    - award_information - award number with directorate acronym
    - created - timestamp created (TimestampMixin)
    - goals - goals/value statement
    - id - primary key (BaseMixin)
    - keywords - subjects/topics/keywords
    - modified - timestamp modified (TimestampMixin)
    - notebooks - python notebooks to share
    - project_status - s there a status for a project (e.g., like if it is for a class and the class ends)...
      we may not need to show this necessarily but we do need to know it.
      Can this be automated in some way based on a lack of activity?
    - purpose - class? research? Etc?
    - references - works where this project work is discussed/featured
    - uuid - unique universal identifier
    """
    __tablename__ = 'profiles_projects'

    award_information = db.Column(db.String(), nullable=True)
    goals = db.Column(db.String(), nullable=True)
    keywords = db.relationship('ProfilesKeywords', backref='profiles_projects', lazy=True)
    notebooks = db.Column(db.String(), nullable=True)
    preferences = db.relationship('FabricPreferences', backref='profiles_projects', lazy=True)
    project_status = db.Column(db.String(), nullable=True)
    projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    purpose = db.Column(db.String(), nullable=True)
    references = db.relationship('ProfilesReferences', backref='profiles_projects', lazy=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)


class ProfilesExternalPages(BaseMixin, db.Model):
    """
    - id - primary key (BaseMixin)
    - profile_id - foreignkey to profiles table
    - page_type
    - url
    - url_type
    """
    __tablename__ = 'profiles_external_pages'

    profiles_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    page_type = db.Column(db.Enum(EnumExternalPageTypes), default=EnumExternalPageTypes.professional, nullable=False)
    url = db.Column(db.String(), nullable=False)
    url_type = db.Column(db.String(), nullable=False)


class ProfilesKeywords(BaseMixin, db.Model):
    __tablename__ = 'profiles_keywords'

    keyword = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)


class ProfilesOtherIdentities(BaseMixin, db.Model):
    __tablename__ = 'profiles_other_identities'

    identity = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    type = db.Column(db.String(), nullable=False)


class ProfilesReferences(BaseMixin, db.Model):
    __tablename__ = 'profiles_references'

    description = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)
    url = db.Column(db.String(), nullable=False)
