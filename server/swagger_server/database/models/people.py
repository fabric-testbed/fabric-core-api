from datetime import datetime, timezone

from swagger_server.database.db import db
from swagger_server.database.models import _PEOPLE_ID
from swagger_server.database.models.mixins import BaseMixin, TimestampMixin


class EmailAddresses(BaseMixin, db.Model):
    """
    EmailAddresses - from COmanage
    """
    __tablename__ = 'people_email_addresses'

    co_email_address_id = db.Column(db.Integer)
    email = db.Column(db.String())
    type = db.Column(db.String())
    people_id = db.Column(db.Integer, db.ForeignKey(_PEOPLE_ID), nullable=False)


class FabricGroups(BaseMixin, db.Model):
    """
    Cous - from COmanage
    - co_cou_id - Cous Id
    - co_parent_cou_id - Cous Parent Id
    - name - COU name
    - description - COU description
    - deleted - COU status (false == active)
    """
    __tablename__ = 'groups'

    co_cou_id = db.Column(db.Integer, nullable=False)
    co_parent_cou_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=True)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


class FabricPeople(BaseMixin, TimestampMixin, db.Model):
    """
    - active - account status
    - id - primary key (BaseMixin)
    - created - timestamp created (TimestampMixin)
    - modified - timestamp modified (TimestampMixin)
    - registered_on
    - uuid - unique universal identifier
    - oidc_claim_sub - OIDC scope openid:sub
    - name - initially OIDC scope: profile:name
    - email - initially OIDC scope: email:email
    - eppn - OIDC scope org.cilogon.userinfo:eppn
    - bastion_login - generated from email:email and openid:sub
    - co_person_id - COmanage CoPersonId
    - preferences - array of preference booleans
    - sshkeys - array of sshkeys
    - profile - foriegnkey to profiles_people
    - roles - array of fabric_roles
    """
    __tablename__ = 'people'

    active = db.Column(db.Boolean, nullable=False, default=False)
    bastion_login = db.Column(db.String(), nullable=True)
    co_person_id = db.Column(db.Integer, nullable=True)
    display_name = db.Column(db.String(), nullable=False)
    email_addresses = db.relationship('EmailAddresses', backref='people', lazy=True)
    fabric_id = db.Column(db.String(), nullable=True)
    oidc_claim_email = db.Column(db.String(), nullable=True)
    oidc_claim_eppn = db.Column(db.String(), nullable=True)
    oidc_claim_family_name = db.Column(db.String(), nullable=True)
    oidc_claim_given_name = db.Column(db.String(), nullable=True)
    oidc_claim_idp_name = db.Column(db.String(), nullable=True)
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
    uuid = db.Column(db.String(), primary_key=False, nullable=False)


class FabricRoles(BaseMixin, db.Model):
    """
    CoPersonRoles - from COmanage
    - affiliation - role affiliation type
    - co_cou_id - COmanage COU Id
    - co_person_id - CoPerson Id
    - co_person_role_id - CoPersonRoles Id
    - name - COU name
    - description - COU description
    - person_id - FabricPeople Id
    - status - role status
    """
    __tablename__ = 'people_roles'

    affiliation = db.Column(db.String(), nullable=False)
    co_cou_id = db.Column(db.Integer, nullable=False)
    co_person_id = db.Column(db.Integer, nullable=False)
    co_person_role_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey(_PEOPLE_ID), nullable=False)
    status = db.Column(db.String(), nullable=False)


class Organizations(BaseMixin, db.Model):
    """
    OrgIdentities - from COmanage
    - affiliation - type of affiliation
    - org_identitiy_id - COmanage Id
    - organization - name
    """
    __tablename__ = 'people_organizations'

    affiliation = db.Column(db.String(), nullable=False)
    org_identity_id = db.Column(db.Integer)
    organization = db.Column(db.String(), nullable=False)
