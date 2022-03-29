import os
from datetime import datetime, timezone

from swagger_server.database.db import db
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


class EmailAddresses(BaseMixin, db.Model):
    """
    EmailAddresses - from COmanage
    - co_email_address_id - EmailAddress Id as integer in COmanage
    - email - email address as string
    - id - primary key (BaseMixin)
    - people_id - foreignkey link to people table
    - type - type of email address as string
    """
    query: db.Query
    __tablename__ = 'people_email_addresses'

    co_email_address_id = db.Column(db.Integer)
    email = db.Column(db.String())
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    type = db.Column(db.String())


class FabricGroups(BaseMixin, db.Model):
    """
    Cous - from COmanage
    - co_cou_id - Cous Id
    - co_parent_cou_id - Cous Parent Id
    - deleted - COU status (false == active)
    - description - COU description
    - id - primary key (BaseMixin)
    - name - COU name
    """
    query: db.Query
    __tablename__ = 'groups'

    co_cou_id = db.Column(db.Integer, nullable=False)
    co_parent_cou_id = db.Column(db.Integer, nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(), nullable=False)


class FabricPeople(BaseMixin, TimestampMixin, db.Model):
    """
    OIDC Claims, COmanage Registry attributes and external table links (* denotes required)
    - * active - account status
    - bastion_login - generated from email:email and openid:sub
    - co_person_id - COmanage CoPersonId
    - created - timestamp created (TimestampMixin)
    - * display_name - initially OIDC scope: profile:name
    - email_addresses = array of COmanage EmailAddresses
    - eppn - edu person principle name
    - fabric_id - unique FABRIC ID set at enrollment
    - id - primary key (BaseMixin)
    - modified - timestamp modified (TimestampMixin)
    - oidc_claim_email - OIDC scope email:email
    - oidc_claim_family_name - OIDC scope profile:family_name
    - oidc_claim_given_name - OIDC scope profile:given_name
    - oidc_claim_name - OIDC scope profile:name
    - oidc_claim_sub - OIDC scope openid:sub
    - org_affiliation - foreignkey link to people_organizations table
    - preferences - array of preference booleans
    - * preferred_email - initially OIDC scope: email:email
    - profile - one-to-one relationship with profiles_people table
    - publications - array of publications
    - registered_on - timestamp user was registered on
    - roles - array of fabric_roles
    - sshkeys - array of sshkeys
    - updated - timestamp user was last updated against COmanage
    - * uuid - unique universal identifier
    """
    query: db.Query
    __tablename__ = 'people'

    active = db.Column(db.Boolean, nullable=False, default=False)
    bastion_login = db.Column(db.String(), nullable=True)
    co_person_id = db.Column(db.Integer, nullable=True)
    display_name = db.Column(db.String(), nullable=False)
    email_addresses = db.relationship('EmailAddresses', backref='people', lazy=True)
    eppn = db.Column(db.String(), nullable=True)
    fabric_id = db.Column(db.String(), nullable=True)
    oidc_claim_email = db.Column(db.String(), nullable=True)
    oidc_claim_family_name = db.Column(db.String(), nullable=True)
    oidc_claim_given_name = db.Column(db.String(), nullable=True)
    oidc_claim_name = db.Column(db.String(), nullable=True)
    oidc_claim_sub = db.Column(db.String(), nullable=True)
    org_affiliation = db.Column(db.Integer, db.ForeignKey('people_organizations.id'), nullable=True)
    preferences = db.relationship('FabricPreferences', backref='people', lazy=True)
    preferred_email = db.Column(db.String(), nullable=False)
    profile = db.relationship('FabricProfilesPeople', backref='people', uselist=False, lazy=True)
    # publications = db.relationship('Publications', secondary=publications, lazy='subquery',
    #                                backref=db.backref('people', lazy=True))
    registered_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    roles = db.relationship('FabricRoles', backref='people', lazy=True)
    # sshkeys = db.relationship('SshKeys', secondary=sshkeys, lazy='subquery', backref=db.backref('people', lazy=True))
    updated = db.Column(db.DateTime(timezone=True), nullable=False)
    uuid = db.Column(db.String(), primary_key=False, nullable=False)

    def is_active(self) -> bool:
        return self.active

    def is_project_lead(self) -> bool:
        return os.getenv('COU_NAME_PROJECT_LEADS').casefold() in [r.name.casefold() for r in self.roles]

    def is_facility_operator(self) -> bool:
        return os.getenv('COU_NAME_FACILITY_OPERATORS').casefold() in [r.name.casefold() for r in self.roles]

    def is_project_creator(self, project_uuid: str = None) -> bool:
        return project_uuid + '-pc' in [r.name.casefold() for r in self.roles]

    def is_project_member(self, project_uuid: str = None) -> bool:
        return project_uuid + '-pm' in [r.name.casefold() for r in self.roles]

    def is_project_owner(self, project_uuid: str = None) -> bool:
        return project_uuid + '-po' in [r.name.casefold() for r in self.roles]


class FabricRoles(BaseMixin, db.Model):
    """
    CoPersonRoles - from COmanage
    - affiliation - role affiliation type
    - co_cou_id - COmanage COU Id
    - co_person_id - CoPerson Id
    - co_person_role_id - CoPersonRoles Id
    - id - primary key (BaseMixin)
    - name - COU name
    - description - COU description
    - people_id - foreignkey link to people table
    - status - role status
    """
    query: db.Query
    __tablename__ = 'people_roles'

    affiliation = db.Column(db.String(), nullable=False)
    co_cou_id = db.Column(db.Integer, nullable=False)
    co_person_id = db.Column(db.Integer, nullable=False)
    co_person_role_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    status = db.Column(db.String(), nullable=False)


class Organizations(BaseMixin, db.Model):
    """
    OrgIdentities - from COmanage
    - affiliation - type of affiliation
    - id - primary key (BaseMixin)
    - org_identitiy_id - COmanage Id
    - organization - name
    """
    query: db.Query
    __tablename__ = 'people_organizations'

    affiliation = db.Column(db.String(), nullable=False)
    org_identity_id = db.Column(db.Integer)
    organization = db.Column(db.String(), nullable=False)
