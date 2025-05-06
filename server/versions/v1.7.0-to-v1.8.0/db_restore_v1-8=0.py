"""
REV: v1.8.0
v1.7.0 --> v1.8.0 - database tables

                   List of relations
 Schema |           Name            | Type  |  Owner
--------+---------------------------+-------+----------
 public | alembic_version           | table | postgres  <-- alembic_version-v<VERSION>.json
 public | announcements             | table | postgres  <-- announcements-v<VERSION>.json
 public | core_api_metrics          | table | postgres  <-- core_api_metrics-v<VERSION>.json
 public | groups                    | table | postgres  <-- groups-v<VERSION>.json
 public | people                    | table | postgres  <-- people-v<VERSION>.json
 public | people_email_addresses    | table | postgres  <-- people_email_addresses-v<VERSION>.json
 public | people_organizations      | table | postgres  <-- people_organizations-v<VERSION>.json
 public | people_roles              | table | postgres  <-- people_roles-v<VERSION>.json
 public | preferences               | table | postgres  <-- preferences-v<VERSION>.json
 public | profiles_keywords         | table | postgres  <-- profiles_keywords-v<VERSION>.json
 public | profiles_other_identities | table | postgres  <-- profiles_other_identities-v<VERSION>.json
 public | profiles_people           | table | postgres  <-- profiles_people-v<VERSION>.json
 public | profiles_personal_pages   | table | postgres  <-- profiles_personal_pages-v<VERSION>.json
 public | profiles_projects         | table | postgres  <-- profiles_projects-v<VERSION>.json
 public | profiles_references       | table | postgres  <-- profiles_references-v<VERSION>.json
 public | projects                  | table | postgres  <-- projects-v<VERSION>.json
 public | projects_communities      | table | postgres  <-- projects_communities-v<VERSION>.json
 public | projects_creators         | table | postgres  <-- projects_creators-v<VERSION>.json
 public | projects_funding          | table | postgres  <-- projects_funding-v<VERSION>.json
 public | projects_members          | table | postgres  <-- projects_members-v<VERSION>.json
 public | projects_owners           | table | postgres  <-- projects_owners-v<VERSION>.json
 public | projects_storage          | table | postgres  <-- projects_storage-v<VERSION>.json
 public | projects_tags             | table | postgres  <-- projects_tags-v<VERSION>.json
 public | projects_topics           | table | postgres  <-- projects_topics-v<VERSION>.json
 public | quotas                    | table | postgres  <-- quotas-v<VERSION>.json
 public | sshkeys                   | table | postgres  <-- sshkeys-v<VERSION>.json
 public | storage                   | table | postgres  <-- storage-v<VERSION>.json
 public | storage_sites             | table | postgres  <-- storage_sites-v<VERSION>.json
 public | task_timeout_tracker      | table | postgres  <-- task_timeout_tracker-v<VERSION>.json
 public | testbed_info              | table | postgres  <-- testbed_info-v<VERSION>.json
 public | token_holders             | table | postgres  <-- token_holders-v<VERSION>.json
 public | user_org_affiliations     | table | postgres  <-- user_org_affiliations-v<VERSION>.json
 public | user_subject_identifiers  | table | postgres  <-- user_subject_identifiers-v<VERSION>.json
(33 rows)

Changes from v1.7.0 --> v1.8.0
- table: quotas
- table: people - added: receive_promotional_email
- TODO: table: projects_topics
- table: *core_api_metrics
- table: *projects_communities
- table: *projects_funding
- TODO: table: projects - added: *communities, *projects_funding, project_type, project_topics
"""

import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import text, update
from sqlalchemy.dialects.postgresql import insert

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.response_code.core_api_utils import normalize_date_to_utc

# API version of data to restore from
api_version = '1.7.0'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


# export alembic_version as JSON output file
def restore_alembic_version_data():
    """
    alembic_version
    - version_num = String
    """
    try:
        with open(BACKUP_DATA_DIR + '/alembic_version-v{0}.json'.format(api_version), 'r') as infile:
            alembic_version_dict = json.load(infile)
        alembic_version = alembic_version_dict.get('alembic_version')
        for a in alembic_version:
            stmt = update(db.Table('alembic_version')).values(
                version_num=a.get('version_num')
            )
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


# export announcements as JSON output file
def restore_announcements_data():
    """
    FabricAnnouncements(BaseMixin, TimestampMixin, TrackingMixin, db.Model):
    - announcement_type = db.Column(db.Enum(EnumAnnouncementTypes),default=EnumAnnouncementTypes.facility)
    - background_image_url = db.Column(db.String(), nullable=True)
    - button = db.Column(db.String())
    - content = db.Column(db.String(), nullable=False)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - created_by_uuid = db.Column(db.String(), nullable=True)
    - display_date = db.Column(db.DateTime(timezone=True), nullable=True)
    - end_date = db.Column(db.DateTime(timezone=True), nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - is_active = db.Column(db.Boolean, default=True, nullable=False)
    - link = db.Column(db.String())
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - modified_by_uuid = db.Column(db.String(), nullable=True)
    - sequence = db.Column(db.Integer(), nullable=True)
    - start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    - title = db.Column(db.String(), nullable=False)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/announcements-v{0}.json'.format(api_version), 'r') as infile:
            announcements_dict = json.load(infile)
        announcements = announcements_dict.get('announcements')
        max_id = 0
        for a in announcements:
            t_id = int(a.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('announcements')).values(
                announcement_type=a.get('announcement_type'),
                background_image_url=a.get('background_image_url') if a.get('background_image_url') else None,
                button=a.get('button') if a.get('button') else None,
                content=a.get('content'),
                created=normalize_date_to_utc(a.get('created')) if a.get('created') else None,
                created_by_uuid=a.get('created_by_uuid'),
                display_date=normalize_date_to_utc(a.get('display_date')) if a.get('display_date') else None,
                end_date=normalize_date_to_utc(a.get('end_date')) if a.get('end_date') else None,
                id=t_id,
                is_active=a.get('is_active'),
                link=a.get('link'),
                modified=normalize_date_to_utc(a.get('modified')) if a.get('modified') else None,
                modified_by_uuid=a.get('modified_by_uuid'),
                sequence=a.get('sequence') if a.get('sequence') else None,
                start_date=normalize_date_to_utc(a.get('start_date')) if a.get('start_date') else None,
                title=a.get('title'),
                uuid=a.get('uuid'),
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='announcements', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export testbed_info as JSON output file
def restore_core_api_metrics_data():
    """
    CoreApiMetrics(BaseMixin, db.Model):
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - json_data = db.Column(JSONB, nullable=False)
    - last_updated = db.Column(db.DateTime(timezone=True), nullable=False)
    - metrics_type = db.Column(db.Enum(EnumCoreApiMetricsTypes), ...)
    """
    try:
        with open(BACKUP_DATA_DIR + '/core_api_metrics-v{0}.json'.format(api_version), 'r') as infile:
            core_api_metrics_dict = json.load(infile)
        core_api_metrics = core_api_metrics_dict.get('core_api_metrics')
        max_id = 0
        for i in core_api_metrics:
            t_id = int(i.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('core_api_metrics')).values(
                id=t_id,
                json_data=i.get('json_data'),
                last_updated=i.get('last_updated') if i.get('last_updated') else None,
                metrics_type=i.get('metrics_type')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='core_api_metrics', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export groups as JSON output file
def restore_groups_data():
    """
    FabricGroups(BaseMixin, TimestampMixin, db.Model)
    - co_cou_id = db.Column(db.Integer, nullable=False)
    - co_parent_cou_id = db.Column(db.Integer, nullable=True)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - deleted = db.Column(db.Boolean, default=False, nullable=False)
    - description = db.Column(db.Text, nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - name = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/groups-v{0}.json'.format(api_version), 'r') as infile:
            groups_dict = json.load(infile)
        groups = groups_dict.get('groups')
        max_id = 0
        for g in groups:
            t_id = int(g.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('groups')).values(
                co_cou_id=int(g.get('co_cou_id')),
                co_parent_cou_id=int(g.get('co_parent_cou_id')) if g.get('co_parent_cou_id') else None,
                created=normalize_date_to_utc(g.get('created')) if g.get('created') else None,
                deleted=g.get('deleted'),
                description=g.get('description'),
                id=t_id,
                modified=normalize_date_to_utc(g.get('modified')) if g.get('modified') else None,
                name=g.get('name')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='groups', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export people as JSON output file
def restore_people_data():
    """
    FabricPeople(BaseMixin, TimestampMixin, db.Model)
    - * active = db.Column(db.Boolean, nullable=False, default=False)
    - * bastion_login = db.Column(db.String(), nullable=True)
    - * co_person_id = db.Column(db.Integer, nullable=True)
    - * created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - * display_name = db.Column(db.String(), nullable=False)
    - email_addresses = db.relationship('EmailAddresses', backref='people', lazy=True)
    - * eppn = db.Column(db.String(), nullable=True)
    - * fabric_id = db.Column(db.String(), nullable=True)
    - * gecos = db.Column(db.String(), nullable=True)
    - * id = db.Column(db.Integer, nullable=False, primary_key=True)
    - * modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - * oidc_claim_email = db.Column(db.String(), nullable=True)
    - * oidc_claim_family_name = db.Column(db.String(), nullable=True)
    - * oidc_claim_given_name = db.Column(db.String(), nullable=True)
    - * oidc_claim_name = db.Column(db.String(), nullable=True)
    - * oidc_claim_sub = db.Column(db.String(), nullable=True)
    - * org_affiliation = db.Column(db.Integer, db.ForeignKey('people_organizations.id'), nullable=True)
    - preferences = db.relationship('FabricPreferences', backref='people', lazy=True)
    - * preferred_email = db.Column(db.String(), nullable=False)
    - profile = db.relationship('FabricProfilesPeople', backref='people', uselist=False, lazy=True)
    # - publications = db.relationship('Publications', secondary=publications)
    - receive_promotional_email = db.Column(db.Boolean, nullable=False, default=True)
    - * registered_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - roles = db.relationship('FabricRoles', backref='people', lazy=True)
    - sshkeys = db.relationship('FabricSshKeys', backref='people', lazy=True)
    - * updated = db.Column(db.DateTime(timezone=True), nullable=False)
    - * uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/people-v{0}.json'.format(api_version), 'r') as infile:
            people_dict = json.load(infile)
        people = people_dict.get('people')
        max_id = 0
        for p in people:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('people')).values(
                active=int(p.get('active')),
                bastion_login=p.get('bastion_login') if p.get('bastion_login') else None,
                co_person_id=int(p.get('co_person_id')) if p.get('co_person_id') else None,
                created=normalize_date_to_utc(p.get('created')),
                display_name=p.get('display_name'),
                # email_addresses=p.get('email_addresses'), <-- restore_people_email_addresses_data()
                eppn=p.get('eppn') if p.get('eppn') else None,
                fabric_id=p.get('fabric_id') if p.get('fabric_id') else None,
                gecos=p.get('gecos') if p.get('gecos') else None,
                id=t_id,
                modified=normalize_date_to_utc(p.get('modified')) if p.get('modified') else None,
                oidc_claim_email=p.get('oidc_claim_email') if p.get('oidc_claim_email') else p.get('preferred_email'),
                oidc_claim_family_name=p.get('oidc_claim_family_name') if p.get('oidc_claim_family_name') else None,
                oidc_claim_given_name=p.get('oidc_claim_given_name') if p.get('oidc_claim_given_name') else None,
                oidc_claim_name=p.get('oidc_claim_name') if p.get('oidc_claim_name') else None,
                oidc_claim_sub=p.get('oidc_claim_sub') if p.get('oidc_claim_sub') else None,
                org_affiliation=int(p.get('org_affiliation')) if p.get('org_affiliation') else None,
                # preferences=p.get('preferences'), <-- restore_preferences_data()
                preferred_email=p.get('preferred_email'),
                # profile=p.get('profile.id'), <-- restore_profiles_people_data()
                receive_promotional_email=p.get('receive_promotional_email') if p.get('receive_promotional_email') else True,
                registered_on=normalize_date_to_utc(p.get('registered_on')) if p.get('registered_on') else None,
                # roles=p.get('roles'), <-- restore_people_roles_data()
                # sshkeys=p.get('sshkeys'), <-- restore_sshkeys_data()
                updated=normalize_date_to_utc(p.get('updated')) if p.get('updated') else None,
                uuid=p.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='people', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_email_addresses as JSON output file
def restore_people_email_addresses_data():
    """
    EmailAddresses(BaseMixin, db.Model)
    - co_email_address_id = db.Column(db.Integer)
    - email = db.Column(db.String())
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - type = db.Column(db.String())
    """
    try:
        with open(BACKUP_DATA_DIR + '/people_email_addresses-v{0}.json'.format(api_version), 'r') as infile:
            people_email_addresses_dict = json.load(infile)
        people_email_addresses = people_email_addresses_dict.get('people_email_addresses')
        max_id = 0
        for e in people_email_addresses:
            t_id = int(e.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('people_email_addresses')).values(
                co_email_address_id=int(e.get('co_email_address_id')),
                email=e.get('email'),
                id=t_id,
                people_id=int(e.get('people_id')),
                type=e.get('type')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='people_email_addresses', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_organizations as JSON output file
def restore_people_organizations_data():
    """
    Organizations(BaseMixin, db.Model)
    - affiliation = db.Column(db.String(), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - org_identity_id = db.Column(db.Integer)
    - organization = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/people_organizations-v{0}.json'.format(api_version), 'r') as infile:
            people_organizations_dict = json.load(infile)
        people_organizations = people_organizations_dict.get('people_organizations')
        max_id = 0
        for o in people_organizations:
            t_id = int(o.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('people_organizations')).values(
                affiliation=o.get('affiliation'),
                id=t_id,
                org_identity_id=int(o.get('org_identity_id')),
                organization=o.get('organization')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='people_organizations', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_roles as JSON output file
def restore_people_roles_data():
    """
    FabricRoles(BaseMixin, db.Model)
    - affiliation = db.Column(db.String(), nullable=False)
    - co_cou_id = db.Column(db.Integer, nullable=False)
    - co_person_id = db.Column(db.Integer, nullable=False)
    - co_person_role_id = db.Column(db.Integer, nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - name = db.Column(db.String(), nullable=False)
    - description = db.Column(db.String(), nullable=True)
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - status = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/people_roles-v{0}.json'.format(api_version), 'r') as infile:
            people_roles_dict = json.load(infile)
        people_roles = people_roles_dict.get('people_roles')
        max_id = 0
        for r in people_roles:
            t_id = int(r.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('people_roles')).values(
                affiliation=r.get('affiliation'),
                co_cou_id=int(r.get('co_cou_id')),
                co_person_id=int(r.get('co_person_id')),
                co_person_role_id=int(r.get('co_person_role_id')),
                id=t_id,
                name=r.get('name'),
                description=r.get('description') if r.get('description') else None,
                people_id=r.get('people_id'),
                status=r.get('status')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='people_roles', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export preferences as JSON output file
def restore_preferences_data():
    """
    FabricPreferences(BaseMixin, TimestampMixin, db.Model)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - key = db.Column(db.String(), nullable=False)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=True)
    - profiles_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=True)
    - profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    - type = db.Column(db.Enum(EnumPreferenceTypes), nullable=False)
    - value = db.Column(db.Boolean, default=True, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/preferences-v{0}.json'.format(api_version), 'r') as infile:
            preferences_dict = json.load(infile)
        preferences = preferences_dict.get('preferences')
        max_id = 0
        for p in preferences:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('preferences')).values(
                created=normalize_date_to_utc(p.get('created')) if p.get('created') else None,
                id=t_id,
                key=p.get('key'),
                modified=normalize_date_to_utc(p.get('modified')) if p.get('modified') else None,
                people_id=int(p.get('people_id')) if p.get('people_id') else None,
                profiles_people_id=int(p.get('profiles_people_id')) if p.get('profiles_people_id') else None,
                profiles_projects_id=int(p.get('profiles_projects_id')) if p.get('profiles_projects_id') else None,
                projects_id=int(p.get('projects_id')) if p.get('projects_id') else None,
                type=p.get('type'),
                value=p.get('value')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='preferences', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_keywords as JSON output file
def restore_profiles_keywords_data():
    """
    ProfilesKeywords(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - keyword = db.Column(db.String(), nullable=False)
    - profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_keywords-v{0}.json'.format(api_version), 'r') as infile:
            profiles_keywords_dict = json.load(infile)
        profiles_keywords = profiles_keywords_dict.get('profiles_keywords')
        max_id = 0
        for p in profiles_keywords:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_keywords')).values(
                id=t_id,
                keyword=p.get('keyword'),
                profiles_projects_id=int(p.get('profiles_projects_id'))
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_keywords', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_other_identities as JSON output file
def restore_profiles_other_identities_data():
    """
    ProfilesOtherIdentities(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - identity = db.Column(db.String(), nullable=False)
    - profiles_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    - type = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_other_identities-v{0}.json'.format(api_version), 'r') as infile:
            profiles_other_identities_dict = json.load(infile)
        profiles_other_identities = profiles_other_identities_dict.get('profiles_other_identities')
        max_id = 0
        for p in profiles_other_identities:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_other_identities')).values(
                id=t_id,
                identity=p.get('identity'),
                profiles_id=int(p.get('profiles_id')),
                type=p.get('type')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_other_identities', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_people as JSON output file
def restore_profiles_people_data():
    """
    FabricProfilesPeople(BaseMixin, TimestampMixin, db.Model):
    - * bio = db.Column(db.String(), nullable=True)
    - * created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - * cv = db.Column(db.String(), nullable=True)
    - * id = db.Column(db.Integer, nullable=False, primary_key=True)
    - * job = db.Column(db.String(), nullable=True)
    - * modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - other_identities = db.relationship('ProfilesOtherIdentities', backref='profiles_people', lazy=True)
    - * people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - personal_pages = db.relationship('ProfilesPersonalPages', backref='profiles_people', lazy=True)
    - preferences = db.relationship('FabricPreferences', backref='profiles_people', lazy=True)
    - * pronouns = db.Column(db.String(), nullable=True)
    - * uuid = db.Column(db.String(), primary_key=False, nullable=False)
    - * website = db.Column(db.String(), nullable=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_people-v{0}.json'.format(api_version), 'r') as infile:
            profiles_people_dict = json.load(infile)
        profiles_people = profiles_people_dict.get('profiles_people')
        max_id = 0
        for p in profiles_people:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_people')).values(
                bio=p.get('bio') if p.get('bio') else None,
                created=normalize_date_to_utc(p.get('created')) if p.get('created') else None,
                cv=p.get('cv') if p.get('cv') else None,
                id=t_id,
                job=p.get('job') if p.get('job') else None,
                modified=normalize_date_to_utc(p.get('modified')) if p.get('modified') else None,
                # other_identities=p.get('other_identities'), <-- restore_profiles_other_identities_data()
                people_id=int(p.get('people_id')),
                # personal_pages=p.get('personal_pages'), <-- restore_profiles_personal_pages_data()
                # preferences=p.get('preferences'), <-- restore_preferences_data()
                pronouns=p.get('pronouns') if p.get('pronouns') else None,
                uuid=p.get('uuid'),
                website=p.get('website') if p.get('website') else None
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_people', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_personal_pages as JSON output file
def restore_profiles_personal_pages_data():
    """
    ProfilesPersonalPages(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - profiles_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    - type = db.Column(db.String(), nullable=False)
    - url = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_personal_pages-v{0}.json'.format(api_version), 'r') as infile:
            profiles_personal_pages_dict = json.load(infile)
        profiles_personal_pages = profiles_personal_pages_dict.get('profiles_personal_pages')
        max_id = 0
        for p in profiles_personal_pages:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_personal_pages')).values(
                id=t_id,
                profiles_people_id=int(p.get('profiles_people_id')),
                type=p.get('type'),
                url=p.get('url')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_personal_pages', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_projects as JSON output file
def restore_profiles_projects_data():
    """
    FabricProfilesProjects(BaseMixin, TimestampMixin, db.Model):
    - * award_information = db.Column(db.String(), nullable=True)
    - * created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - * goals = db.Column(db.String(), nullable=True)
    - * id = db.Column(db.Integer, nullable=False, primary_key=True)
    - keywords = db.relationship('ProfilesKeywords', backref='profiles_projects', lazy=True)
    - * modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - preferences = db.relationship('FabricPreferences', backref='profiles_projects', lazy=True)
    - * project_status = db.Column(db.String(), nullable=True)
    - * projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - * purpose = db.Column(db.String(), nullable=True)
    - references = db.relationship('ProfilesReferences', backref='profiles_projects', lazy=True)
    - * uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_projects-v{0}.json'.format(api_version), 'r') as infile:
            profiles_projects_dict = json.load(infile)
        profiles_projects = profiles_projects_dict.get('profiles_projects')
        max_id = 0
        for p in profiles_projects:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_projects')).values(
                award_information=p.get('award_information') if p.get('award_information') else None,
                created=normalize_date_to_utc(p.get('created')) if p.get('created') else None,
                goals=p.get('goals') if p.get('goals') else None,
                id=t_id,
                # keywords=p.get('keywords'), <-- restore_profiles_keywords_data()
                modified=normalize_date_to_utc(p.get('modified')) if p.get('modified') else None,
                # preferences=p.get('preferences'), <-- restore_preferences_data()
                project_status=p.get('project_status') if p.get('project_status') else None,
                projects_id=int(p.get('projects_id')),
                purpose=p.get('purpose') if p.get('purpose') else None,
                # references=p.get('references'), <-- restore_profiles_references_data()
                uuid=p.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_projects', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_references as JSON output file
def restore_profiles_references_data():
    """
    ProfilesReferences(BaseMixin, db.Model)
    - description = db.Column(db.String(), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)
    - url = db.Column(db.String(), nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/profiles_references-v{0}.json'.format(api_version), 'r') as infile:
            profiles_references_dict = json.load(infile)
        profiles_references = profiles_references_dict.get('profiles_references')
        max_id = 0
        for p in profiles_references:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('profiles_references')).values(
                description=p.get('description'),
                id=t_id,
                profiles_projects_id=int(p.get('profiles_projects_id')),
                url=p.get('url')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='profiles_references', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects as JSON output file
def restore_projects_data():
    """
    FabricProjects(BaseMixin, TimestampMixin, TrackingMixin, db.Model)
    - * active = db.Column(db.Boolean, default=True, nullable=False)
    - * co_cou_id_pc = db.Column(db.Integer, nullable=True)
    - * co_cou_id_pm = db.Column(db.Integer, nullable=True)
    - * co_cou_id_po = db.Column(db.Integer, nullable=True)
    - * co_cou_id_tk = db.Column(db.Integer, nullable=True)
    - communities = db.relationship('ProjectsCommunities', backref='projects', lazy=True)
    - * created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - * created_by_uuid = db.Column(db.String(), nullable=True)
    - * description = db.Column(db.Text, nullable=False)
    - * expires_on = db.Column(db.DateTime(timezone=True), nullable=True)
    - * facility = db.Column(db.String(), default=os.getenv('CORE_API_DEFAULT_FACILITY'), nullable=False)
    - * id = db.Column(db.Integer, nullable=False, primary_key=True)
    - * is_locked = db.Column(db.Boolean, default=False, nullable=False)
    - * is_public = db.Column(db.Boolean, default=True, nullable=False)
    - * modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - * modified_by_uuid = db.Column(db.String(), nullable=True)
    - * name = db.Column(db.String(), nullable=False)
    - preferences = db.relationship('FabricPreferences', backref='projects', lazy=True)
    - profile = db.relationship('FabricProfilesProjects', backref='projects', uselist=False, lazy=True)
    - project_creators = db.relationship('FabricPeople', secondary=projects_creators)
    - project_funding = db.relationship('ProjectsFunding', backref='projects', lazy=True)
    - project_members = db.relationship('FabricPeople', secondary=projects_members)
    - project_owners = db.relationship('FabricPeople', secondary=projects_owners)
    - project_storage = db.relationship('FabricStorage', secondary=projects_storage)
    - project_topics = db.relationship('ProjectsTopics', backref='projects', lazy=True)
    - project_type = db.Column(db.Enum(EnumProjectTypes), default=EnumProjectTypes.research, nullable=False)
    - tags = db.relationship('ProjectsTags', backref='projects', lazy=True)
    - token_holders = db.relationship('FabricPeople', secondary=token_holders)
    - * uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects-v{0}.json'.format(api_version), 'r') as infile:
            projects_dict = json.load(infile)
        projects = projects_dict.get('projects')
        max_id = 0
        for p in projects:
            t_id = int(p.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('projects')).values(
                active=p.get('active'),
                co_cou_id_pc=int(p.get('co_cou_id_pc')) if p.get('co_cou_id_pc') else None,
                co_cou_id_pm=int(p.get('co_cou_id_pm')) if p.get('co_cou_id_pm') else None,
                co_cou_id_po=int(p.get('co_cou_id_po')) if p.get('co_cou_id_po') else None,
                co_cou_id_tk=int(p.get('co_cou_id_tk')) if p.get('co_cou_id_tk') else None,
                # communities=p.get('communities'), <-- restore_projects_communities_data()
                created=normalize_date_to_utc(p.get('created')) if p.get('created') else None,
                created_by_uuid=p.get('created_by_uuid') if p.get('created_by_uuid') else None,
                description=p.get('description'),
                expires_on=normalize_date_to_utc(p.get('expires_on')) if p.get('expires_on') else None,
                facility=p.get('facility'),
                id=t_id,
                is_locked=p.get('is_locked') if p.get('is_locked') else False,
                is_public=p.get('is_public'),
                modified=normalize_date_to_utc(p.get('modified')) if p.get('modified') else None,
                modified_by_uuid=p.get('modified_by_uuid') if p.get('modified_by_uuid') else None,
                name=p.get('name'),
                # preferences=p.get('preferences'), <-- restore_preferences_data()
                # profile=p.get('profile.id'), <-- restore_projects_profiles_data()
                # project_creators=p.get('projects_creators'), <-- restore_projects_creators_data()
                # project_funding=p.get('project_funding'), <-- restore_project_funding_data()
                # project_members=p.get('projects_members'), <-- restore_projects_members_data()
                # project_owners=p.get('projects_owners'), <-- restore_projects_owners_data()
                # project_storage=p.get('projects_storage'), <-- restore_projects_storage_data()
                # project_topics=p.get('projects_topics'), <-- restore_projects_topics_data()
                project_type=p.get('project_type') if p.get('project_type') else 'research',
                # tags=p.get('tags'), <-- restore_projects_tags_data()
                # token_holders=p.get('token_holders'), <-- restore_token_holders_data()
                uuid=p.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='projects', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_tags as JSON output file
def restore_projects_communities_data():
    """
    ProjectsCommunities(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - community = db.Column(db.Text, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_communities-v{0}.json'.format(api_version), 'r') as infile:
            projects_communities_dict = json.load(infile)
        projects_communities = projects_communities_dict.get('projects_communities')
        max_id = 0
        for c in projects_communities:
            c_id = int(c.get('id'))
            if c_id > max_id:
                max_id = c_id
            stmt = insert(db.Table('projects_communities')).values(
                id=c_id,
                projects_id=int(c.get('projects_id')),
                community=c.get('community')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='projects_communities', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_creators as JSON output file
def restore_projects_creators_data():
    """
    projects_creators
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_creators-v{0}.json'.format(api_version), 'r') as infile:
            projects_creators_dict = json.load(infile)
        projects_creators = projects_creators_dict.get('projects_creators')
        for pc in projects_creators:
            stmt = insert(db.Table('projects_creators', metadata=db.Model.metadata)).values(
                people_id=pc.get('people_id'),
                projects_id=pc.get('projects_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


# restore projects_funding from JSON input file
def restore_projects_funding_data():
    """
    ProjectsFunding(BaseMixin, db.Model)
    - id - primary key (BaseMixin)
    - projects_id - foreignkey link to projects table
    - agency - agency as string
    - award_amount - award amount as string
    - award_number - award number as string
    - directorate - directorate as string
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_funding-v{0}.json'.format(api_version), 'r') as infile:
            projects_funding_dict = json.load(infile)
        projects_funding = projects_funding_dict.get('projects_funding')
        max_id = 0
        for c in projects_funding:
            c_id = int(c.get('id'))
            if c_id > max_id:
                max_id = c_id
            stmt = insert(db.Table('projects_funding')).values(
                id=c_id,
                projects_id=int(c.get('projects_id')),
                agency=c.get('agency'),
                agency_other=c.get('agency_other'),
                award_amount=c.get('award_amount'),
                award_number=c.get('award_number'),
                directorate=c.get('directorate')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='projects_funding', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_members as JSON output file
def restore_projects_members_data():
    """
    projects_members
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_members-v{0}.json'.format(api_version), 'r') as infile:
            projects_members_dict = json.load(infile)
        projects_members = projects_members_dict.get('projects_members')
        for pc in projects_members:
            stmt = insert(db.Table('projects_members', metadata=db.Model.metadata)).values(
                people_id=pc.get('people_id'),
                projects_id=pc.get('projects_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_owners as JSON output file
def restore_projects_owners_data():
    """
    projects_owners
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_owners-v{0}.json'.format(api_version), 'r') as infile:
            projects_owners_dict = json.load(infile)
        projects_owners = projects_owners_dict.get('projects_owners')
        for pc in projects_owners:
            stmt = insert(db.Table('projects_owners', metadata=db.Model.metadata)).values(
                people_id=pc.get('people_id'),
                projects_id=pc.get('projects_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_owners as JSON output file
def restore_projects_storage_data():
    """
    projects_storage
    - storage_id = db.Column('storage_id', db.Integer, db.ForeignKey('storage.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_storage-v{0}.json'.format(api_version), 'r') as infile:
            projects_storage_dict = json.load(infile)
        projects_storage = projects_storage_dict.get('projects_storage')
        for pc in projects_storage:
            stmt = insert(db.Table('projects_storage', metadata=db.Model.metadata)).values(
                storage_id=pc.get('storage_id'),
                projects_id=pc.get('projects_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_tags as JSON output file
def restore_projects_tags_data():
    """
    ProjectsTags(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - tag = db.Column(db.Text, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_tags-v{0}.json'.format(api_version), 'r') as infile:
            projects_tags_dict = json.load(infile)
        projects_tags = projects_tags_dict.get('projects_tags')
        max_id = 0
        for t in projects_tags:
            t_id = int(t.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('projects_tags')).values(
                id=t_id,
                projects_id=int(t.get('projects_id')),
                tag=t.get('tag')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='projects_tags', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_tags as JSON output file
def restore_projects_topics_data():
    """
    ProjectsTopics(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - topic = db.Column(db.Text, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/projects_topics-v{0}.json'.format(api_version), 'r') as infile:
            projects_topics_dict = json.load(infile)
        projects_topics = projects_topics_dict.get('projects_topics')
        max_id = 0
        for c in projects_topics:
            c_id = int(c.get('id'))
            if c_id > max_id:
                max_id = c_id
            stmt = insert(db.Table('projects_topics')).values(
                id=c_id,
                projects_id=int(c.get('projects_id')),
                topic=c.get('topic')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='projects_topics', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_tags as JSON output file
def restore_quotas_data():
    """
    FabricQuotas(db.Model)
    - created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - project_uuid = db.Column(db.String(), nullable=False)
    - quota_limit = db.Column(db.Float, nullable=False)
    - quota_used = db.Column(db.Float, nullable=False)
    - resource_type = db.Column(db.Enum(EnumResourceTypes), default=EnumResourceTypes.core, nullable=False)
    - resource_unit = db.Column(db.Enum(EnumResourceUnits), default=EnumResourceUnits.hours, nullable=False)
    - updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/quotas-v{0}.json'.format(api_version), 'r') as infile:
            quotas_dict = json.load(infile)
        quotas = quotas_dict.get('quotas')
        max_id = 0
        for q in quotas:
            q_id = int(q.get('id'))
            if q_id > max_id:
                max_id = q_id
            stmt = insert(db.Table('quotas')).values(
                created_at=normalize_date_to_utc(q.get('created_at')),
                id=q_id,
                project_uuid=int(q.get('project_uuid')),
                quota_limit=q.get('quota_limit'),
                quota_used=q.get('quota_used'),
                resource_type=q.get('resource_type'),
                resource_unit=q.get('resource_unit'),
                updated_at=normalize_date_to_utc(q.get('updated_at')) if k.get('updated_at') else None,
                uuid=q.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='quotas', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export sshkeys as JSON output file
def restore_sshkeys_data():
    """
    FabricSshKeys(BaseMixin, TimestampMixin, db.Model)
    - active = db.Column(db.Boolean, default=True, nullable=False)
    - comment = db.Column(db.String())
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - deactivated_on = db.Column(db.DateTime(timezone=True), nullable=True)
    - deactivated_reason = db.Column(db.String())
    - description = db.Column(db.String())
    - expires_on = db.Column(db.DateTime(timezone=True), nullable=False)
    - fabric_key_type = db.Column(db.Enum(EnumSshKeyTypes), default=EnumSshKeyTypes.sliver, nullable=False)
    - fingerprint = db.Column(db.String())
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - public_key = db.Column(db.String())
    - ssh_key_type = db.Column(db.String())
    - status = db.Column(db.Enum(EnumSshKeyStatus), default=EnumSshKeyStatus.active, nullable=False)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/sshkeys-v{0}.json'.format(api_version), 'r') as infile:
            sshkeys_dict = json.load(infile)
        sshkeys = sshkeys_dict.get('sshkeys')
        max_id = 0
        for k in sshkeys:
            t_id = int(k.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('sshkeys')).values(
                active=k.get('active'),
                comment=k.get('comment'),
                created=normalize_date_to_utc(k.get('created')),
                deactivated_on=normalize_date_to_utc(k.get('deactivated_on')) if k.get('deactivated_on') else None,
                deactivated_reason=k.get('deactivated_reason') if k.get('deactivated_reason') else None,
                description=k.get('description') if k.get('description') else None,
                expires_on=normalize_date_to_utc(k.get('expires_on')) if k.get('expires_on') else None,
                fabric_key_type=k.get('fabric_key_type'),
                fingerprint=k.get('fingerprint'),
                id=t_id,
                modified=normalize_date_to_utc(k.get('modified')) if k.get('modified') else None,
                people_id=int(k.get('people_id')),
                public_key=k.get('public_key'),
                ssh_key_type=k.get('ssh_key_type'),
                status=k.get('status'),
                uuid=k.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='sshkeys', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


def restore_storage_data():
    """
    FabricStorage(BaseMixin, TimestampMixin, TrackingMixin, db.Model)
    - active = db.Column(db.Boolean, default=True, nullable=False)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - created_by_uuid = db.Column(db.String(), nullable=True)
    - expires_on = db.Column(db.DateTime(timezone=True), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - modified_by_uuid = db.Column(db.String(), nullable=True)
    - project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - requested_by_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - sites = db.relationship('StorageSites', backref='storage', lazy=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    - volume_name = db.Column(db.String())
    - volume_size_gb = db.Column(db.Integer, nullable=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/storage-v{0}.json'.format(api_version), 'r') as infile:
            storage_dict = json.load(infile)
        storage = storage_dict.get('storage')
        max_id = 0
        for s in storage:
            t_id = int(s.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('storage')).values(
                active=s.get('active'),
                created=normalize_date_to_utc(s.get('created')),
                created_by_uuid=s.get('created_by_uuid') if s.get('created_by_uuid') else None,
                expires_on=normalize_date_to_utc(s.get('expires_on')) if s.get('expires_on') else None,
                id=t_id,
                modified=normalize_date_to_utc(s.get('modified')) if s.get('modified') else None,
                modified_by_uuid=s.get('modified_by_uuid') if s.get('modified_by_uuid') else None,
                project_id=int(s.get('project_id')),
                requested_by_id=int(s.get('requested_by_id')),
                # sites=s.get('sites'),  <-- restore_storage_sites_data()
                uuid=s.get('uuid'),
                volume_name=s.get('volume_name'),
                volume_size_gb=int(s.get('volume_size_gb'))
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='storage', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


def restore_storage_sites_data():
    """
    StorageSites(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'), nullable=False)
    - site = db.Column(db.Text, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/storage_sites-v{0}.json'.format(api_version), 'r') as infile:
            storage_sites_dict = json.load(infile)
        storage_sites = storage_sites_dict.get('storage_sites')
        max_id = 0
        for s in storage_sites:
            t_id = int(s.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('storage_sites')).values(
                id=t_id,
                storage_id=int(s.get('storage_id')),
                site=s.get('site')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='storage_sites', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


#  public | task_timeout_tracker | table | postgres  <-- task_timeout_tracker-v<VERSION>.json
def restore_task_timeout_tracker_data():
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
    try:
        with open(BACKUP_DATA_DIR + '/task_timeout_tracker-v{0}.json'.format(api_version), 'r') as infile:
            task_timeout_tracker_dict = json.load(infile)
        task_timeout_tracker = task_timeout_tracker_dict.get('task_timeout_tracker')
        max_id = 0
        for t in task_timeout_tracker:
            t_id = int(t.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('task_timeout_tracker')).values(
                description=t.get('description'),
                id=t_id,
                last_updated=normalize_date_to_utc(t.get('last_updated')) if t.get('last_updated') else None,
                name=t.get('name'),
                timeout_in_seconds=int(t.get('timeout_in_seconds')),
                uuid=t.get('uuid'),
                value=t.get('value')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='task_timeout_tracker', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# export testbed_info as JSON output file
def restore_testbed_info_data():
    """
    FabricTestbedInfo(BaseMixin, TimestampMixin, TrackingMixin, db.Model)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - created_by_uuid = db.Column(db.String(), nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - is_active = db.Column(db.Boolean, default=True)
    - json_data = db.Column(JSONB, nullable=False)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - modified_by_uuid = db.Column(db.String(), nullable=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        with open(BACKUP_DATA_DIR + '/testbed_info-v{0}.json'.format(api_version), 'r') as infile:
            testbed_info_dict = json.load(infile)
        testbed_info = testbed_info_dict.get('testbed_info')
        max_id = 0
        for i in testbed_info:
            t_id = int(i.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('testbed_info')).values(
                created=i.get('created') if i.get('created') else None,
                created_by_uuid=i.get('created_by_uuid') if i.get('created_by_uuid') else None,
                id=t_id,
                is_active=i.get('is_active'),
                json_data=i.get('json_data'),
                modified=i.get('modified') if i.get('modified') else None,
                modified_by_uuid=i.get('modified_by_uuid') if i.get('modified_by_uuid') else None,
                uuid=i.get('uuid')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='testbed_info', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


#  public | token_holders             | table | postgres  <-- token_holders-v<VERSION>.json
def restore_token_holders_data():
    """
    token_holders
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)
    """
    try:
        with open(BACKUP_DATA_DIR + '/token_holders-v{0}.json'.format(api_version), 'r') as infile:
            token_holders_dict = json.load(infile)
        token_holders = token_holders_dict.get('token_holders')
        for tk in token_holders:
            stmt = insert(db.Table('token_holders', metadata=db.Model.metadata)).values(
                people_id=tk.get('people_id'),
                projects_id=tk.get('projects_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


#  public | user_org_affiliations     | table | postgres  <-- user_org_affiliations-v<VERSION>.json
def restore_user_org_affiliations_data():
    """
    user_org_affiliations
    - affiliation - affiliation as string
    - id - primary key (BaseMixin)
    - people_id - foreignkey link to people table
    """
    try:
        with open(BACKUP_DATA_DIR + '/user_org_affiliations-v{0}.json'.format(api_version), 'r') as infile:
            user_org_affiliations_dict = json.load(infile)
        user_org_affiliations = user_org_affiliations_dict.get('user_org_affiliations')
        max_id = 0
        for oa in user_org_affiliations:
            t_id = int(oa.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('user_org_affiliations', metadata=db.Model.metadata)).values(
                affiliation=oa.get('affiliation'),
                id=t_id,
                people_id=oa.get('people_id')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='user_org_affiliations', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


#  public | user_subject_identifiers  | table | postgres  <-- user_subject_identifiers-v<VERSION>.json
def restore_user_subject_identifiers_data():
    """
    user_subject_identifiers
    - id - primary key (BaseMixin)
    - people_id - foreignkey link to people table
    - sub - subject identifier as string
    """
    try:
        with open(BACKUP_DATA_DIR + '/user_subject_identifiers-v{0}.json'.format(api_version), 'r') as infile:
            user_subject_identifiers_dict = json.load(infile)
        user_subject_identifiers = user_subject_identifiers_dict.get('user_subject_identifiers')
        max_id = 0
        for si in user_subject_identifiers:
            t_id = int(si.get('id'))
            if t_id > max_id:
                max_id = t_id
            stmt = insert(db.Table('user_subject_identifiers', metadata=db.Model.metadata)).values(
                id=t_id,
                people_id=si.get('people_id'),
                sub=si.get('sub')
            ).on_conflict_do_nothing()
            db.session.execute(stmt)
        db.session.commit()
        reset_serial_sequence(db_table='user_subject_identifiers', seq_value=max_id + 1)
    except Exception as exc:
        consoleLogger.error(exc)


# verify project expiry date
def verify_project_expiry():
    """
    FabricProjects(BaseMixin, TimestampMixin, TrackingMixin, db.Model)
    - active = db.Column(db.Boolean, default=True, nullable=False)
    - co_cou_id_pc = db.Column(db.Integer, nullable=True)
    - co_cou_id_pm = db.Column(db.Integer, nullable=True)
    - co_cou_id_po = db.Column(db.Integer, nullable=True)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - created_by_uuid = db.Column(db.String(), nullable=True)
    - description = db.Column(db.Text, nullable=False)
    - expires_on = db.Column(db.DateTime(timezone=True), nullable=True)
    - facility = db.Column(db.String(), default=os.getenv('CORE_API_DEFAULT_FACILITY'), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - is_locked = db.Column(db.Boolean, default=False, nullable=False)
    - is_public = db.Column(db.Boolean, default=True, nullable=False)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - modified_by_uuid = db.Column(db.String(), nullable=True)
    - name = db.Column(db.String(), nullable=False)
    - preferences = db.relationship('FabricPreferences', backref='projects', lazy=True)
    - profile = db.relationship('FabricProfilesProjects', backref='projects', uselist=False, lazy=True)
    - project_creators = db.relationship('FabricPeople', secondary=projects_creators)
    - project_members = db.relationship('FabricPeople', secondary=projects_members)
    - project_owners = db.relationship('FabricPeople', secondary=projects_owners)
    # - publications = db.relationship('Publications', secondary=publications)
    - tags = db.relationship('ProjectsTags', backref='projects', lazy=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    """
    try:
        fab_projects = FabricProjects.query.order_by('id').all()
        now = datetime.now(timezone.utc)
        project_expiry = now + timedelta(days=float(os.getenv('PROJECTS_RENEWAL_PERIOD_IN_DAYS')))
        for p in fab_projects:
            if not p.expires_on:
                # set new project expiry date
                p.expires_on = project_expiry
                p.modified = now
                db.session.commit()
                consoleLogger.info('Project: {0} set expiry: {1}'.format(str(p.uuid), str(project_expiry)))
            else:
                if p.expires_on < now:
                    # set is_locked to True
                    p.is_locked = True
                    p.modified = now
                    consoleLogger.info('Project: {0} is expired'.format(str(p.uuid)))
    except Exception as exc:
        consoleLogger.error(exc)


def reset_serial_sequence(db_table: str, seq_value: int):
    try:
        stmt = text('SELECT setval(pg_get_serial_sequence(\'{0}\',\'id\'),{1});'.format(db_table, str(seq_value)))
        db.session.execute(stmt)
        db.session.commit()
        consoleLogger.info('  - Table: {0}, sequence_id: {1}'.format(db_table, str(seq_value)))
    except Exception as exc:
        consoleLogger.error(exc)


# -------------------------------------- Version specific methods --------------------------------------
from swagger_server.response_code.comanage_utils import api
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.people import FabricGroups, FabricPeople, FabricRoles
from swagger_server.response_code.core_api_utils import is_valid_uuid
from swagger_server.response_code.projects_utils import create_fabric_project_from_uuid


def import_missing_groups_from_comanage():
    """
    check all COUs from COmanage and add groups that may be missing
    """
    try:
        cous = api.cous_view_per_co().get('Cous', [])
        for co_cou in cous:
            co_cou_id = co_cou.get('Id')
            fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
            if not fab_group:
                consoleLogger.info("CREATE: entry in 'groups' table for co_cou_id: {0}".format(co_cou_id))
                fab_group = FabricGroups()
                fab_group.co_cou_id = co_cou_id
                fab_group.co_parent_cou_id = co_cou.get('ParentId', None)
                fab_group.created = normalize_date_to_utc(co_cou.get('Created'))
                fab_group.name = co_cou.get('Name')
                fab_group.description = co_cou.get('Description')
                fab_group.deleted = co_cou.get('Deleted')
                db.session.add(fab_group)
                db.session.commit()
            else:
                modified = False
                if fab_group.name != co_cou.get('Name'):
                    consoleLogger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, name = '{1}'".format(
                        co_cou_id, fab_group.name))
                    fab_group.name = co_cou.get('Name')
                    db.session.commit()
                    modified = True
                if fab_group.description != co_cou.get('Description'):
                    consoleLogger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, description = '{1}'".format(
                        co_cou_id, fab_group.description))
                    fab_group.description = co_cou.get('Description')
                    db.session.commit()
                    modified = True
                if fab_group.deleted != co_cou.get('Deleted'):
                    consoleLogger.info("UPDATE: entry in 'groups' table for co_cou_id: {0}, deleted = '{1}'".format(
                        co_cou_id, fab_group.deleted))
                    fab_group.deleted = co_cou.get('Deleted')
                    db.session.commit()
                    modified = True
                if not modified:
                    consoleLogger.info("NO CHANGE: entry in 'groups' table for co_cou_id: {0}, name = '{1}'".format(
                        co_cou_id, fab_group.name))
    except Exception as exc:
        consoleLogger.error(exc)


def import_missing_roles_from_comanage():
    """
    check all COPerson Roles that may be missing and add to active FABRIC people
    """
    co_people = api.copeople_view_per_co().get('CoPeople', [])
    for co_person in co_people:
        co_person_id = co_person.get('Id')
        fab_person = FabricPeople.query.filter_by(co_person_id=co_person_id).first()
        if fab_person:
            co_roles = api.coperson_roles_view_per_coperson(coperson_id=co_person_id)
            if co_roles:
                co_roles = co_roles.get('CoPersonRoles', [])
                for co_role in co_roles:
                    co_person_role_id = co_role.get('Id', None)
                    co_cou_id = co_role.get('CouId')
                    fab_role = FabricRoles.query.filter_by(co_person_role_id=co_person_role_id).one_or_none()
                    fab_group = FabricGroups.query.filter_by(co_cou_id=co_cou_id).one_or_none()
                    if not fab_role:
                        if fab_group:
                            fab_role = FabricRoles()
                            fab_role.affiliation = co_role.get('Affiliation', 'member')
                            fab_role.co_cou_id = co_cou_id
                            fab_role.co_person_id = co_person_id
                            fab_role.co_person_role_id = co_person_role_id
                            fab_role.name = fab_group.name
                            fab_role.description = fab_group.description
                            fab_role.people_id = fab_person.id
                            fab_role.status = co_role.get('Status', 'Active')
                            try:
                                db.session.add(fab_role)
                                db.session.commit()
                                consoleLogger.info(
                                    "CREATE: entry in 'roles' table for co_person_role_id: {0}".format(
                                        co_person_role_id))
                            except Exception as exc:
                                consoleLogger.error('DUPLICATE ROLE: {0}'.format(exc))
                                db.session.rollback()
                                continue
                        else:
                            consoleLogger.warning(
                                "ERROR: unable to locate co_cou_id {0} in the 'groups' table".format(co_cou_id))
                    else:
                        modified = False
                        if fab_role.name != fab_group.name:
                            consoleLogger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, name = '{1}'".format(
                                    co_person_role_id, fab_group.name))
                            fab_role.name = fab_group.name
                            db.session.commit()
                            modified = True
                        if fab_role.description != fab_group.description:
                            consoleLogger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, description = '{1}'".format(
                                    co_person_role_id, fab_group.description))
                            fab_role.description = fab_group.description
                            db.session.commit()
                            modified = True
                        if fab_role.status != co_role.get('Status'):
                            consoleLogger.info(
                                "UPDATE: entry in 'roles' table for co_person_role_id: {0}, status = '{1}'".format(
                                    co_person_role_id, co_role.get('Status')))
                            fab_role.status = co_role.get('Status')
                            db.session.commit()
                            modified = True
                        if not modified:
                            consoleLogger.info(
                                "NO CHANGE: entry in 'roles' table for co_person_role_id: {0}".format(
                                    co_person_role_id))
        else:
            consoleLogger.warning("ERROR: unable to locate co_person_id {0} in the 'people' table".format(co_person_id))


def import_missing_projects_cous():
    """
    Add missing projects based on COUs
    """
    try:
        fab_groups = FabricGroups.query.order_by('id').all()
        for group in fab_groups:
            proj_uuid = str(group.name)[:-3]
            fab_project = FabricProjects.query.filter_by(uuid=proj_uuid).one_or_none()
            if not fab_project and is_valid_uuid(proj_uuid):
                print('- create project {0}'.format(proj_uuid))
                fab_project = create_fabric_project_from_uuid(uuid=proj_uuid)

    except Exception as exc:
        consoleLogger.error(exc)


# -------------------------------------- Version specific methods --------------------------------------


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Restore data from API version {0}'.format(api_version))
    #                    List of relations
    #  Schema |           Name            | Type  |  Owner
    # --------+---------------------------+-------+----------
    #  public | alembic_version           | table | postgres
    # consoleLogger.info('restore alembic_version table')
    # restore_alembic_version_data()

    #  public | announcements             | table | postgres
    consoleLogger.info('restore announcements table')
    restore_announcements_data()

    # public | core_api_metrics           | table | postgres
    consoleLogger.info('restore core_api_metrics table')
    restore_core_api_metrics_data()

    #  public | groups                    | table | postgres
    consoleLogger.info('restore groups table')
    restore_groups_data()

    #  public | people_organizations      | table | postgres
    consoleLogger.info('restore people_organizations table')
    restore_people_organizations_data()

    #  public | people                    | table | postgres
    consoleLogger.info('restore people table')
    restore_people_data()

    #  public | people_email_addresses    | table | postgres
    consoleLogger.info('restore people_email_addresses table')
    restore_people_email_addresses_data()

    #  public | people_roles              | table | postgres
    consoleLogger.info('restore people_roles table')
    restore_people_roles_data()

    #  public | profiles_people           | table | postgres
    consoleLogger.info('restore profiles_people table')
    restore_profiles_people_data()

    #  public | profiles_other_identities | table | postgres
    consoleLogger.info('restore profiles_other_identities table')
    restore_profiles_other_identities_data()

    #  public | profiles_personal_pages   | table | postgres
    consoleLogger.info('restore profiles_personal_pages table')
    restore_profiles_personal_pages_data()

    #  public | projects                  | table | postgres
    consoleLogger.info('restore projects table')
    restore_projects_data()

    #  public | profiles_projects         | table | postgres
    consoleLogger.info('restore profiles_projects table')
    restore_profiles_projects_data()

    #  public | profiles_keywords         | table | postgres
    consoleLogger.info('restore profiles_keywords table')
    restore_profiles_keywords_data()

    #  public | profiles_references       | table | postgres
    consoleLogger.info('restore profiles_references table')
    restore_profiles_references_data()

    # public | projects_communities       | table | postgres
    consoleLogger.info('restore projects_communities table')
    restore_projects_communities_data()

    #  public | projects_creators         | table | postgres
    consoleLogger.info('restore projects_creators table')
    restore_projects_creators_data()

    # public | projects_funding           | table | postgres
    consoleLogger.info('restore projects_funding table')
    restore_projects_funding_data()

    #  public | projects_members          | table | postgres
    consoleLogger.info('restore projects_members table')
    restore_projects_members_data()

    #  public | projects_owners           | table | postgres
    consoleLogger.info('restore projects_owners table')
    restore_projects_owners_data()

    #  public | projects_tags             | table | postgres
    consoleLogger.info('restore projects_tags table')
    restore_projects_tags_data()
    restore_projects_owners_data()

    #  public | projects_topics           | table | postgres
    consoleLogger.info('restore projects_topics table')
    restore_projects_topics_data()

    #  public | preferences               | table | postgres
    consoleLogger.info('restore preferences table')
    restore_preferences_data()

    #  public | sshkeys                   | table | postgres
    consoleLogger.info('restore sshkeys table')
    restore_sshkeys_data()

    #  public | storage                   | table | postgres
    consoleLogger.info('restore storage table')
    restore_storage_data()

    #  public | storage_sites             | table | postgres
    consoleLogger.info('restore storage_sites table')
    restore_storage_sites_data()

    #  public | projects_storage          | table | postgres
    consoleLogger.info('restore projects_storage table')
    restore_projects_storage_data()

    #  public | task_timeout_tracker | table | postgres
    consoleLogger.info('restore task_timeout_tracker table')
    restore_task_timeout_tracker_data()

    #  public | testbed_info              | table | postgres
    consoleLogger.info('restore testbed_info table')
    restore_testbed_info_data()

    #  public | token_holders             | table | postgres
    consoleLogger.info('restore token_holders table')
    restore_token_holders_data()

    #  public | user_org_affiliations     | table | postgres
    consoleLogger.info('restore user_org_affiliations table')
    restore_user_org_affiliations_data()

    #  public | user_subject_identifiers  | table | postgres
    consoleLogger.info('restore user_subject_identifiers table')
    restore_user_subject_identifiers_data()

    #  verify project expiry
    consoleLogger.info('verify project expiry')
    verify_project_expiry()

    # import missing groups, roles, and project cous from COmanage
    # consoleLogger.info('import missing groups from COmanage')
    # import_missing_groups_from_comanage()
    #
    # consoleLogger.info('import missing roles from COmanage')
    # import_missing_roles_from_comanage()
    #
    # consoleLogger.info('import missing projects from COUs')
    # import_missing_projects_cous()
