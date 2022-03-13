import enum

from swagger_server.database.db import db
from swagger_server.database.models import _PEOPLE_ID, _PROJECTS_ID, _PROFILE_PROJECTS_ID, _PROFILE_PEOPLE_ID
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


# Enum for preferences type
class PreferencesTypeEnum(enum.Enum):
    people = 'people'
    projects = 'projects'
    profile_people = 'profile_people'
    profile_projects = 'profile_projects'


# Enum for external pages type
class ExternalPagesTypeEnum(enum.Enum):
    professional = 'professional'
    social = 'social'


class ExternalPagesUrlEnum(enum.Enum):
    bitbucket = 'bitbucket'
    facebook = 'facebook'
    github = 'github'
    gitlab = 'gitlab'
    instagram = 'instagram'
    linkedin = 'linkedin'
    messenger = 'messenger'
    other = 'other'
    pinterest = 'pinterest'
    twitter = 'twitter'
    youtube = 'youtube'


# Enum for identities type
class OtherIdentitiesTypeEnum(enum.Enum):
    google_scholar = 'google_scholar'
    orcid = 'orcid'
    other = 'other'


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
    Preference per Type
    people
    - show_email: <bool>
    - show_eppn: <bool>
    - show_profile: <bool>
    - show_publications: <bool>
    - show_roles: <bool>
    - show_sshkeys: <bool>
    profile_people
    - show_bio: <bool>,
    - show_cv: <bool>,
    - show_job: <bool>,
    - show_other_identities: <bool>,
    - show_professional: <bool>,
    - show_pronouns: <bool>,
    - show_social: <bool>,
    - show_website: <bool>
    projects
    - is_public
    - show_profile: <bool>
    - show_publications: <bool>
    profile_projects
    - show_award_information: <bool>
    - show_goals: <bool>
    - show_keywords: <bool>
    - show_notebooks: <bool>
    - show_project_status: <bool>
    - show_purpose: <bool>
    - show_references: <bool>
    """
    __tablename__ = 'preferences'

    key = db.Column(db.String(), nullable=False)
    people_id = db.Column(db.Integer, db.ForeignKey(_PEOPLE_ID), nullable=True)
    profile_people_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PEOPLE_ID), nullable=True)
    profile_projects_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PROJECTS_ID), nullable=True)
    projects_id = db.Column(db.Integer, db.ForeignKey(_PROJECTS_ID), nullable=True)
    type = db.Column(db.Enum(PreferencesTypeEnum), default=PreferencesTypeEnum.people, nullable=False)
    value = db.Column(db.Boolean, default=True, nullable=False)


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
    people_id = db.Column(db.Integer, db.ForeignKey(_PEOPLE_ID), nullable=False)
    preferences = db.relationship('FabricPreferences', backref='profiles_people', lazy=True)
    pronouns = db.Column(db.String(), nullable=True)
    website = db.Column(db.String(), nullable=True)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)


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
    __tablename__ = 'profiles_external_pages'

    profile_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PEOPLE_ID), nullable=False)
    page_type = db.Column(db.Enum(ExternalPagesTypeEnum), default=ExternalPagesTypeEnum.professional, nullable=False)
    url_type = db.Column(db.Enum(ExternalPagesUrlEnum), default=ExternalPagesUrlEnum.github, nullable=False)
    url = db.Column(db.String(), nullable=False)


class ProfilesOtherIdentities(BaseMixin, db.Model):
    __tablename__ = 'profiles_other_identities'

    identity = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PEOPLE_ID), nullable=False)
    type = db.Column(db.Enum(OtherIdentitiesTypeEnum), default=OtherIdentitiesTypeEnum.orcid, nullable=False)


class ProfilesKeywords(BaseMixin, db.Model):
    __tablename__ = 'profiles_keywords'

    keyword = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PROJECTS_ID), nullable=False)


class ProfilesReferences(BaseMixin, db.Model):
    __tablename__ = 'profiles_references'

    description = db.Column(db.String(), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey(_PROFILE_PROJECTS_ID), nullable=False)
    url = db.Column(db.String(), nullable=False)
