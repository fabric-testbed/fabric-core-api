"""
REV: v1.8.0
v1.7.0 - database tables

$ docker exec -u postgres api-database psql -c "\dt;"
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
 public | sshkeys                   | table | postgres  <-- sshkeys-v<VERSION>.json
 public | storage                   | table | postgres  <-- storage-v<VERSION>.json
 public | storage_sites             | table | postgres  <-- storage_sites-v<VERSION>.json
 public | task_timeout_tracker      | table | postgres  <-- task_timeout_tracker-v<VERSION>.json
 public | testbed_info              | table | postgres  <-- testbed_info-v<VERSION>.json
 public | token_holders             | table | postgres  <-- token_holders-v<VERSION>.json
 public | user_org_affiliations     | table | postgres  <-- user_org_affiliations-v<VERSION>.json
 public | user_subject_identifiers  | table | postgres  <-- user_subject_identifiers-v<VERSION>.json
(32 rows)
"""

import json
import os

from sqlalchemy.sql import text

from swagger_server import __API_VERSION__
from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.announcements import FabricAnnouncements
from swagger_server.database.models.core_api_metrics import CoreApiMetrics
from swagger_server.database.models.people import EmailAddresses, FabricGroups, FabricPeople, FabricRoles, \
    Organizations, UserOrgAffiliations, UserSubjectIdentifiers
from swagger_server.database.models.preferences import FabricPreferences
from swagger_server.database.models.profiles import FabricProfilesPeople, FabricProfilesProjects, ProfilesKeywords, \
    ProfilesOtherIdentities, ProfilesPersonalPages, ProfilesReferences
from swagger_server.database.models.projects import FabricProjects, ProjectsCommunities, ProjectsFunding, ProjectsTags, ProjectsTopics
from swagger_server.database.models.sshkeys import FabricSshKeys
from swagger_server.database.models.storage import FabricStorage, StorageSites
from swagger_server.database.models.tasktracker import TaskTimeoutTracker
from swagger_server.database.models.testbed_info import FabricTestbedInfo
from swagger_server.response_code.core_api_utils import normalize_date_to_utc

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


# export alembic_version as JSON output file
def dump_alembic_version_data():
    """
    alembic_version
    - version_num = String

    Table "public.alembic_version"
       Column    |         Type          | Collation | Nullable | Default
    -------------+-----------------------+-----------+----------+---------
     version_num | character varying(32) |           | not null |
    """
    try:
        alembic_version = []
        query = text("SELECT version_num FROM alembic_version")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'version_num': row[0]
            }
            alembic_version.append(data)
        output_dict = {'alembic_version': alembic_version}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/alembic_version-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export announcements as JSON output file
def dump_announcements_data():
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
    - start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    - title = db.Column(db.String(), nullable=False)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)

    Table "public.announcements"
            Column        |           Type           | Collation | Nullable |                  Default
    ----------------------+--------------------------+-----------+----------+-------------------------------------------
     announcement_type    | enumannouncementtypes    |           | not null |
     background_image_url | character varying        |           |          |
     button               | character varying        |           |          |
     content              | character varying        |           | not null |
     display_date         | timestamp with time zone |           |          |
     end_date             | timestamp with time zone |           |          |
     is_active            | boolean                  |           | not null |
     link                 | character varying        |           |          |
     sequence             | integer                  |           |          |
     start_date           | timestamp with time zone |           |          |
     title                | character varying        |           | not null |
     uuid                 | character varying        |           | not null |
     id                   | integer                  |           | not null | nextval('announcements_id_seq'::regclass)
     created              | timestamp with time zone |           | not null |
     modified             | timestamp with time zone |           |          |
     created_by_uuid      | character varying        |           |          |
     modified_by_uuid     | character varying        |           |          |
    """
    try:
        announcements = []
        fab_announcements = FabricAnnouncements.query.order_by('id').all()
        for a in fab_announcements:
            data = {
                'announcement_type': a.announcement_type.name,
                'background_image_url': a.background_image_url,
                'button': a.button,
                'content': a.content,
                'created': normalize_date_to_utc(date_str=str(a.created), return_type='str'),
                'created_by_uuid': str(a.created_by_uuid),
                'display_date': normalize_date_to_utc(date_str=str(a.display_date), return_type='str'),
                'end_date': normalize_date_to_utc(date_str=str(a.end_date), return_type='str'),
                'id': a.id,
                'is_active': a.is_active,
                'link': a.link,
                'modified': normalize_date_to_utc(date_str=str(a.modified), return_type='str'),
                'modified_by_uuid': str(a.modified_by_uuid),
                'start_date': normalize_date_to_utc(date_str=str(a.start_date), return_type='str'),
                'title': a.title,
                'uuid': str(a.uuid)
            }
            announcements.append(data)
        output_dict = {'announcements': announcements}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/announcements-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export groups as JSON output file
def dump_core_api_metrics_data():
    """
    CoreApiMetrics(BaseMixin, db.Model)
    - json_data = db.Column(JSONB, nullable=False)
    - last_updated = db.Column(db.DateTime(timezone=True), nullable=False)
    - metrics_type = db.Column(db.Enum(EnumCoreApiMetricsTypes), default=EnumCoreApiMetricsTypes.overview, nullable=False)

    Table "public.core_api_metrics"
        Column    |           Type           | Collation | Nullable |                   Default
    --------------+--------------------------+-----------+----------+----------------------------------------------
     json_data    | jsonb                    |           | not null |
     last_updated | timestamp with time zone |           | not null |
     metrics_type | enumcoreapimetricstypes  |           | not null |
     id           | integer                  |           | not null | nextval('core_api_metrics_id_seq'::regclass)
    """
    try:
        core_api_metrics = []
        fab_core_api_metrics = CoreApiMetrics.query.order_by('id').all()
        for m in fab_core_api_metrics:
            data = {
                'id': m.id,
                'json_data': m.json_data,
                'last_updated': normalize_date_to_utc(date_str=str(m.last_updated),
                                                      return_type='str') if m.last_updated else None,
                'metrics_type': m.metrics_type.name,
            }
            core_api_metrics.append(data)
        output_dict = {'core_api_metrics': core_api_metrics}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/core_api_metrics-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export groups as JSON output file
def dump_groups_data():
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

    Table "public.groups"
          Column      |           Type           | Collation | Nullable |              Default
    ------------------+--------------------------+-----------+----------+------------------------------------
     co_cou_id        | integer                  |           | not null |
     co_parent_cou_id | integer                  |           |          |
     deleted          | boolean                  |           | not null |
     description      | text                     |           |          |
     name             | character varying        |           | not null |
     id               | integer                  |           | not null | nextval('groups_id_seq'::regclass)
     created          | timestamp with time zone |           | not null |
     modified         | timestamp with time zone |           |          |
    """
    try:
        groups = []
        fab_groups = FabricGroups.query.order_by('id').all()
        for g in fab_groups:
            data = {
                'co_cou_id': g.co_cou_id,
                'co_parent_cou_id': g.co_parent_cou_id,
                'created': normalize_date_to_utc(date_str=str(g.created), return_type='str') if g.created else None,
                'deleted': g.deleted,
                'description': g.description,
                'id': g.id,
                'modified': normalize_date_to_utc(date_str=str(g.modified), return_type='str') if g.modified else None,
                'name': g.name,
            }
            groups.append(data)
        output_dict = {'groups': groups}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/groups-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export people as JSON output file
def dump_people_data():
    """
    FabricPeople(BaseMixin, TimestampMixin, db.Model)
    - active = db.Column(db.Boolean, nullable=False, default=False)
    - bastion_login = db.Column(db.String(), nullable=True)
    - co_person_id = db.Column(db.Integer, nullable=True)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - display_name = db.Column(db.String(), nullable=False)
    - email_addresses = db.relationship('EmailAddresses', backref='people', lazy=True)
    - eppn = db.Column(db.String(), nullable=True)
    - fabric_id = db.Column(db.String(), nullable=True)
    - gecos = db.Column(db.String(), nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - oidc_claim_email = db.Column(db.String(), nullable=True)
    - oidc_claim_family_name = db.Column(db.String(), nullable=True)
    - oidc_claim_given_name = db.Column(db.String(), nullable=True)
    - oidc_claim_name = db.Column(db.String(), nullable=True)
    - oidc_claim_sub = db.Column(db.String(), nullable=True)
    - org_affiliation = db.Column(db.Integer, db.ForeignKey('people_organizations.id'), nullable=True)
    - preferences = db.relationship('FabricPreferences', backref='people', lazy=True)
    - preferred_email = db.Column(db.String(), nullable=False)
    - profile = db.relationship('FabricProfilesPeople', backref='people', uselist=False, lazy=True)
    - registered_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - roles = db.relationship('FabricRoles', backref='people', lazy=True)
    - sshkeys = db.relationship('FabricSshKeys', backref='people', lazy=True)
    - updated = db.Column(db.DateTime(timezone=True), nullable=False)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)

    Table "public.people"
              Column           |           Type           | Collation | Nullable |              Default
    ---------------------------+--------------------------+-----------+----------+------------------------------------
     active                    | boolean                  |           | not null |
     bastion_login             | character varying        |           |          |
     co_person_id              | integer                  |           |          |
     display_name              | character varying        |           | not null |
     eppn                      | character varying        |           |          |
     fabric_id                 | character varying        |           |          |
     gecos                     | character varying        |           |          |
     oidc_claim_email          | character varying        |           |          |
     oidc_claim_family_name    | character varying        |           |          |
     oidc_claim_given_name     | character varying        |           |          |
     oidc_claim_name           | character varying        |           |          |
     oidc_claim_sub            | character varying        |           |          |
     org_affiliation           | integer                  |           |          |
     preferred_email           | character varying        |           | not null |
     receive_promotional_email | boolean                  |           | not null |
     registered_on             | timestamp with time zone |           | not null |
     updated                   | timestamp with time zone |           | not null |
     uuid                      | character varying        |           | not null |
     id                        | integer                  |           | not null | nextval('people_id_seq'::regclass)
     created                   | timestamp with time zone |           | not null |
     modified                  | timestamp with time zone |           |          |
    """
    try:
        people = []
        fab_people = FabricPeople.query.order_by('id').all()
        for p in fab_people:
            data = {
                'active': p.active,
                'bastion_login': p.bastion_login,
                'co_person_id': p.co_person_id,
                'created': normalize_date_to_utc(date_str=str(p.created), return_type='str') if p.created else None,
                'display_name': p.display_name,
                'email_addresses': [e.id for e in p.email_addresses],
                'eppn': p.eppn,
                'fabric_id': p.fabric_id,
                'gecos': p.gecos,
                'id': p.id,
                'modified': normalize_date_to_utc(date_str=str(p.modified), return_type='str') if p.modified else None,
                'oidc_claim_email': p.oidc_claim_email,
                'oidc_claim_family_name': p.oidc_claim_family_name,
                'oidc_claim_given_name': p.oidc_claim_given_name,
                'oidc_claim_name': p.oidc_claim_name,
                'oidc_claim_sub': p.oidc_claim_sub,
                'org_affiliation': p.org_affiliation,
                'preferences': [pr.id for pr in p.preferences],  # [FabricPreferences.id]
                'preferred_email': p.preferred_email,
                'profile': p.profile.id,
                # 'publications': [pu.id for pu in p.publications], # [FabricPublications.id]
                'registered_on': normalize_date_to_utc(date_str=str(p.registered_on),
                                                       return_type='str') if p.registered_on else None,
                'roles': [r.id for r in p.roles],
                'sshkeys': [s.id for s in p.sshkeys],
                'updated': normalize_date_to_utc(date_str=str(p.updated), return_type='str') if p.updated else None,
                'uuid': p.uuid
            }
            people.append(data)
        output_dict = {'people': people}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/people-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_email_addresses as JSON output file
def dump_people_email_addresses_data():
    """
    EmailAddresses(BaseMixin, db.Model)
    - co_email_address_id = db.Column(db.Integer)
    - email = db.Column(db.String())
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - type = db.Column(db.String())

    Table "public.people_email_addresses"
           Column        |       Type        | Collation | Nullable |                      Default
    ---------------------+-------------------+-----------+----------+----------------------------------------------------
     co_email_address_id | integer           |           |          |
     email               | character varying |           |          |
     people_id           | integer           |           | not null |
     type                | character varying |           |          |
     id                  | integer           |           | not null | nextval('people_email_addresses_id_seq'::regclass)
    """
    try:
        people_email_addresses = []
        fab_people_email_addresses = EmailAddresses.query.order_by('id').all()
        for e in fab_people_email_addresses:
            data = {
                'co_email_address_id': e.co_email_address_id,
                'email': e.email,
                'id': e.id,
                'people_id': e.people_id,
                'type': e.type
            }
            people_email_addresses.append(data)
        output_dict = {'people_email_addresses': people_email_addresses}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/people_email_addresses-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_organizations as JSON output file
def dump_people_organizations_data():
    """
    Organizations(BaseMixin, db.Model)
    - affiliation = db.Column(db.String(), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - org_identity_id = db.Column(db.Integer)
    - organization = db.Column(db.String(), nullable=False)

    Table "public.people_organizations"
         Column      |       Type        | Collation | Nullable |                     Default
    -----------------+-------------------+-----------+----------+--------------------------------------------------
     affiliation     | character varying |           | not null |
     org_identity_id | integer           |           |          |
     organization    | character varying |           | not null |
     id              | integer           |           | not null | nextval('people_organizations_id_seq'::regclass)
    """
    try:
        people_organizations = []
        fab_people_organizations = Organizations.query.order_by('id').all()
        for o in fab_people_organizations:
            data = {
                'affiliation': o.affiliation,
                'id': o.id,
                'org_identity_id': o.org_identity_id,
                'organization': o.organization
            }
            people_organizations.append(data)
        output_dict = {'people_organizations': people_organizations}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/people_organizations-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export people_roles as JSON output file
def dump_people_roles_data():
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

    Table "public.people_roles"
          Column       |       Type        | Collation | Nullable |                 Default
    -------------------+-------------------+-----------+----------+------------------------------------------
     affiliation       | character varying |           | not null |
     co_cou_id         | integer           |           | not null |
     co_person_id      | integer           |           | not null |
     co_person_role_id | integer           |           | not null |
     name              | character varying |           | not null |
     description       | character varying |           |          |
     people_id         | integer           |           | not null |
     status            | character varying |           | not null |
     id                | integer           |           | not null | nextval('people_roles_id_seq'::regclass)
    """
    try:
        people_roles = []
        fab_people_roles = FabricRoles.query.order_by('id').all()
        for r in fab_people_roles:
            data = {
                'affiliation': r.affiliation,
                'co_cou_id': r.co_cou_id,
                'co_person_id': r.co_person_id,
                'co_person_role_id': r.co_person_role_id,
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'people_id': r.people_id,
                'status': r.status
            }
            people_roles.append(data)
        output_dict = {'people_roles': people_roles}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/people_roles-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export preferences as JSON output file
def dump_preferences_data():
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

    Table "public.preferences"
            Column        |           Type           | Collation | Nullable |                 Default
    ----------------------+--------------------------+-----------+----------+-----------------------------------------
     key                  | character varying        |           | not null |
     people_id            | integer                  |           |          |
     profiles_people_id   | integer                  |           |          |
     profiles_projects_id | integer                  |           |          |
     projects_id          | integer                  |           |          |
     type                 | enumpreferencetypes      |           | not null |
     value                | boolean                  |           | not null |
     id                   | integer                  |           | not null | nextval('preferences_id_seq'::regclass)
     created              | timestamp with time zone |           | not null |
     modified             | timestamp with time zone |           |          |
    """
    try:
        preferences = []
        fab_preferences = FabricPreferences.query.order_by('id').all()
        for p in fab_preferences:
            data = {
                'created': normalize_date_to_utc(date_str=str(p.created), return_type='str') if p.created else None,
                'id': p.id,
                'key': p.key,
                'modified': normalize_date_to_utc(date_str=str(p.modified), return_type='str') if p.modified else None,
                'people_id': p.people_id,
                'profiles_people_id': p.profiles_people_id,
                'profiles_projects_id': p.profiles_projects_id,
                'projects_id': p.projects_id,
                'type': p.type.name,
                'value': p.value,
            }
            preferences.append(data)
        output_dict = {'preferences': preferences}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/preferences-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_keywords as JSON output file
def dump_profiles_keywords_data():
    """
    ProfilesKeywords(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - keyword = db.Column(db.String(), nullable=False)
    - profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)

    Table "public.profiles_keywords"
            Column        |       Type        | Collation | Nullable |                    Default
    ----------------------+-------------------+-----------+----------+-----------------------------------------------
     keyword              | character varying |           | not null |
     profiles_projects_id | integer           |           | not null |
     id                   | integer           |           | not null | nextval('profiles_keywords_id_seq'::regclass)
    """
    try:
        profiles_keywords = []
        fab_profiles_keywords = ProfilesKeywords.query.order_by('id').all()
        for p in fab_profiles_keywords:
            data = {
                'id': p.id,
                'keyword': p.keyword,
                'profiles_projects_id': p.profiles_projects_id
            }
            profiles_keywords.append(data)
        output_dict = {'profiles_keywords': profiles_keywords}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_keywords-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_other_identities as JSON output file
def dump_profiles_other_identities_data():
    """
    ProfilesOtherIdentities(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - identity = db.Column(db.String(), nullable=False)
    - profiles_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    - type = db.Column(db.String(), nullable=False)

    Table "public.profiles_other_identities"
       Column    |       Type        | Collation | Nullable |                        Default
    -------------+-------------------+-----------+----------+-------------------------------------------------------
     identity    | character varying |           | not null |
     profiles_id | integer           |           | not null |
     type        | character varying |           | not null |
     id          | integer           |           | not null | nextval('profiles_other_identities_id_seq'::regclass)
    """
    try:
        profiles_other_identities = []
        fab_profiles_other_identities = ProfilesOtherIdentities.query.order_by('id').all()
        for p in fab_profiles_other_identities:
            data = {
                'id': p.id,
                'identity': p.identity,
                'profiles_id': p.profiles_id,
                'type': p.type
            }
            profiles_other_identities.append(data)
        output_dict = {'profiles_other_identities': profiles_other_identities}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_other_identities-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_people as JSON output file
def dump_profiles_people_data():
    """
    FabricProfilesPeople(BaseMixin, TimestampMixin, db.Model):
    - bio = db.Column(db.String(), nullable=True)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - cv = db.Column(db.String(), nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - job = db.Column(db.String(), nullable=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    - other_identities = db.relationship('ProfilesOtherIdentities', backref='profiles_people', lazy=True)
    - people_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    - personal_pages = db.relationship('ProfilesPersonalPages', backref='profiles_people', lazy=True)
    - preferences = db.relationship('FabricPreferences', backref='profiles_people', lazy=True)
    - pronouns = db.Column(db.String(), nullable=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)
    - website = db.Column(db.String(), nullable=True)

    Table "public.profiles_people"
      Column   |           Type           | Collation | Nullable |                   Default
    -----------+--------------------------+-----------+----------+---------------------------------------------
     bio       | character varying        |           |          |
     cv        | character varying        |           |          |
     job       | character varying        |           |          |
     people_id | integer                  |           | not null |
     pronouns  | character varying        |           |          |
     uuid      | character varying        |           | not null |
     website   | character varying        |           |          |
     id        | integer                  |           | not null | nextval('profiles_people_id_seq'::regclass)
     created   | timestamp with time zone |           | not null |
     modified  | timestamp with time zone |           |          |
    """
    try:
        profiles_people = []
        fab_profiles_people = FabricProfilesPeople.query.order_by('id').all()
        for p in fab_profiles_people:
            data = {
                'bio': p.bio,
                'created': normalize_date_to_utc(date_str=str(p.created), return_type='str') if p.created else None,
                'cv': p.cv,
                'id': p.id,
                'job': p.job,
                'modified': normalize_date_to_utc(date_str=str(p.modified), return_type='str') if p.modified else None,
                'other_identities': [oi.id for oi in p.other_identities],
                'people_id': p.people_id,
                'personal_pages': [pp.id for pp in p.personal_pages],
                'preferences': [pr.id for pr in p.preferences],
                'pronouns': p.pronouns,
                'uuid': p.uuid,
                'website': p.website
            }
            profiles_people.append(data)
        output_dict = {'profiles_people': profiles_people}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_people-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_personal_pages as JSON output file
def dump_profiles_personal_pages_data():
    """
    ProfilesPersonalPages(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - profiles_people_id = db.Column(db.Integer, db.ForeignKey('profiles_people.id'), nullable=False)
    - type = db.Column(db.String(), nullable=False)
    - url = db.Column(db.String(), nullable=False)

    Table "public.profiles_personal_pages"
           Column       |       Type        | Collation | Nullable |                       Default
    --------------------+-------------------+-----------+----------+-----------------------------------------------------
     profiles_people_id | integer           |           | not null |
     url                | character varying |           | not null |
     type               | character varying |           | not null |
     id                 | integer           |           | not null | nextval('profiles_personal_pages_id_seq'::regclass)
    """
    try:
        profiles_personal_pages = []
        fab_profiles_personal_pages = ProfilesPersonalPages.query.order_by('id').all()
        for p in fab_profiles_personal_pages:
            data = {
                'id': p.id,
                'profiles_people_id': p.profiles_people_id,
                'type': p.type,
                'url': p.url
            }
            profiles_personal_pages.append(data)
        output_dict = {'profiles_personal_pages': profiles_personal_pages}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_personal_pages-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_projects as JSON output file
def dump_profiles_projects_data():
    """
    FabricProfilesProjects(BaseMixin, TimestampMixin, db.Model):
    - award_information = db.Column(db.String(), nullable=True)
    - created = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    - goals = db.Column(db.String(), nullable=True)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - keywords = db.relationship('ProfilesKeywords', backref='profiles_projects', lazy=True)
    - modified = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    # - notebooks = db.relationship('Notebooks', secondary=notebooks, lazy='subquery)
    - preferences = db.relationship('FabricPreferences', backref='profiles_projects', lazy=True)
    - project_status = db.Column(db.String(), nullable=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - purpose = db.Column(db.String(), nullable=True)
    - references = db.relationship('ProfilesReferences', backref='profiles_projects', lazy=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)

    Table "public.profiles_projects"
          Column       |           Type           | Collation | Nullable |                    Default
    -------------------+--------------------------+-----------+----------+-----------------------------------------------
     award_information | character varying        |           |          |
     goals             | character varying        |           |          |
     project_status    | character varying        |           |          |
     projects_id       | integer                  |           | not null |
     purpose           | character varying        |           |          |
     uuid              | character varying        |           | not null |
     id                | integer                  |           | not null | nextval('profiles_projects_id_seq'::regclass)
     created           | timestamp with time zone |           | not null |
     modified          | timestamp with time zone |           |          |
    """
    try:
        profiles_projects = []
        fab_profiles_projects = FabricProfilesProjects.query.order_by('id').all()
        for p in fab_profiles_projects:
            data = {
                'award_information': p.award_information,
                'created': normalize_date_to_utc(date_str=str(p.created), return_type='str') if p.created else None,
                'goals': p.goals,
                'id': p.id,
                'keywords': [k.id for k in p.keywords],
                'modified': normalize_date_to_utc(date_str=str(p.modified), return_type='str') if p.modified else None,
                # - notebooks = db.relationship('Notebooks', secondary=notebooks, lazy='subquery)
                'preferences': [pr.id for pr in p.preferences],
                'project_status': p.project_status,
                'projects_id': p.projects_id,
                'purpose': p.purpose,
                'references': [r.id for r in p.references],
                'uuid': p.uuid
            }
            profiles_projects.append(data)
        output_dict = {'profiles_projects': profiles_projects}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_projects-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export profiles_references as JSON output file
def dump_profiles_references_data():
    """
    ProfilesReferences(BaseMixin, db.Model)
    - description = db.Column(db.String(), nullable=False)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - profiles_projects_id = db.Column(db.Integer, db.ForeignKey('profiles_projects.id'), nullable=False)
    - url = db.Column(db.String(), nullable=False)

    Table "public.profiles_references"
            Column        |       Type        | Collation | Nullable |                     Default
    ----------------------+-------------------+-----------+----------+-------------------------------------------------
     description          | character varying |           | not null |
     profiles_projects_id | integer           |           | not null |
     url                  | character varying |           | not null |
     id                   | integer           |           | not null | nextval('profiles_references_id_seq'::regclass)
    """
    try:
        profiles_references = []
        fab_profiles_references = ProfilesReferences.query.order_by('id').all()
        for p in fab_profiles_references:
            data = {
                'description': p.description,
                'id': p.id,
                'profiles_projects_id': p.profiles_projects_id,
                'url': p.url
            }
            profiles_references.append(data)
        output_dict = {'profiles_references': profiles_references}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/profiles_references-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects as JSON output file
def dump_projects_data():
    """
    FabricProjects(BaseMixin, TimestampMixin, TrackingMixin, db.Model)
    - active = db.Column(db.Boolean, default=True, nullable=False)
    - co_cou_id_pc = db.Column(db.Integer, nullable=True)
    - co_cou_id_pm = db.Column(db.Integer, nullable=True)
    - co_cou_id_po = db.Column(db.Integer, nullable=True)
    - co_cou_id_tk = db.Column(db.Integer, nullable=True)
    - communities = db.relationship('ProjectsCommunities', backref='projects', lazy=True)
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
    - preferences = db.relationship('FabricPreferences', backref='projects')
    - profile = db.relationship('FabricProfilesProjects', backref='projects')
    - project_creators = db.relationship('FabricPeople', secondary=projects_creators)
    - project_funding = db.relationship('ProjectsFunding', backref='projects', lazy=True)
    - project_members = db.relationship('FabricPeople', secondary=projects_members)
    - project_owners = db.relationship('FabricPeople', secondary=projects_owners)
    - project_storage = db.relationship('FabricStorage', secondary=projects_storage)
    - project_type = db.Column(db.Enum(EnumProjectTypes), default=EnumProjectTypes.research, nullable=False)
    - tags = db.relationship('ProjectsTags', backref='projects', lazy=True)
    - token_holders = db.relationship('FabricPeople', secondary=token_holders)
    - topics = db.relationship('ProjectsTopics', backref='projects', lazy=True)
    - uuid = db.Column(db.String(), primary_key=False, nullable=False)

    Table "public.projects"
          Column      |           Type           | Collation | Nullable |               Default
    ------------------+--------------------------+-----------+----------+--------------------------------------
     active           | boolean                  |           | not null |
     co_cou_id_pc     | integer                  |           |          |
     co_cou_id_pm     | integer                  |           |          |
     co_cou_id_po     | integer                  |           |          |
     co_cou_id_tk     | integer                  |           |          |
     description      | text                     |           | not null |
     expires_on       | timestamp with time zone |           |          |
     facility         | character varying        |           | not null |
     is_locked        | boolean                  |           | not null |
     is_public        | boolean                  |           | not null |
     name             | character varying        |           | not null |
     project_type     | enumprojecttypes         |           | not null |
     uuid             | character varying        |           | not null |
     id               | integer                  |           | not null | nextval('projects_id_seq'::regclass)
     created          | timestamp with time zone |           | not null |
     modified         | timestamp with time zone |           |          |
     created_by_uuid  | character varying        |           |          |
     modified_by_uuid | character varying        |           |          |
    """
    try:
        projects = []
        fab_projects = FabricProjects.query.order_by('id').all()
        # TODO: table: projects - added: *communities, *projects_funding, project_type, project_topics
        for p in fab_projects:
            data = {
                'active': p.active,
                'co_cou_id_pc': p.co_cou_id_pc,
                'co_cou_id_pm': p.co_cou_id_pm,
                'co_cou_id_po': p.co_cou_id_po,
                'co_cou_id_tk': p.co_cou_id_tk,
                'communities': [c.id for c in p.communities],  # [ProjectsCommunities.id]
                'created': normalize_date_to_utc(date_str=str(p.created), return_type='str') if p.created else None,
                'created_by_uuid': p.created_by_uuid,
                'description': p.description,
                'expires_on': normalize_date_to_utc(date_str=str(p.expires_on),
                                                    return_type='str') if p.created else None,
                'facility': p.facility,
                'id': p.id,
                'is_locked': p.is_locked,
                'is_public': p.is_public,
                'modified': normalize_date_to_utc(date_str=str(p.modified), return_type='str') if p.modified else None,
                'modified_by_uuid': p.modified_by_uuid,
                'name': p.name,
                'preferences': [pr.id for pr in p.preferences],  # [FabricPreferences.id]
                'profile': p.profile.id,
                'project_creators': [pc.id for pc in p.project_creators],  # [FabricPeople.id]
                'project_funding': [pf.id for pf in p.project_funding],  # [ProjectsFunding.id]
                'project_members': [pm.id for pm in p.project_members],  # [FabricPeople.id]
                'project_owners': [po.id for po in p.project_owners],  # [FabricPeople.id]
                'project_storage': [ps.id for ps in p.project_storage],  # [FabricStorage.id]
                'project_type': p.project_type,
                'tags': [t.id for t in p.tags],  # [ProjectsTags.id]
                'token_holders': [tk.id for tk in p.token_holders],  # [FabricPeople.id]
                'topics': [t.id for t in p.topics],  # [ProjectsTopics.id]
                'uuid': p.uuid
            }
            projects.append(data)
        output_dict = {'projects': projects}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_creators as JSON output file
def dump_projects_communities_data():
    """
    projects_communities
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - community = db.Column(db.Text, nullable=False)

    Table "public.projects_communities"
       Column    |  Type   | Collation | Nullable |                     Default
    -------------+---------+-----------+----------+--------------------------------------------------
     projects_id | integer |           | not null |
     community   | text    |           | not null |
     id          | integer |           | not null | nextval('projects_communities_id_seq'::regclass)
    """
    try:
        projects_communities = []
        fab_projects_communities = ProjectsCommunities.query.order_by('id').all()
        for c in fab_projects_communities:
            data = {
                'id': c.id,
                'projects_id': c.projects_id,
                'community': c.community
            }
            projects_communities.append(data)
        output_dict = {'projects_communities': projects_communities}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_communities-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_creators as JSON output file
def dump_projects_creators_data():
    """
    projects_creators
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    Table "public.projects_creators"
       Column    |  Type   | Collation | Nullable | Default
    -------------+---------+-----------+----------+---------
     people_id   | integer |           | not null |
     projects_id | integer |           | not null |
    """
    try:
        projects_creators = []
        query = text("SELECT people_id, projects_id FROM projects_creators")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'people_id': row[0],
                'projects_id': row[1]
            }
            projects_creators.append(data)
        output_dict = {'projects_creators': projects_creators}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_creators-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_creators as JSON output file
def dump_projects_funding_data():
    """
    projects_funding
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - agency = db.Column(db.Text, nullable=False)
    - award_amount = db.Column(db.Text, nullable=True)
    - award_number = db.Column(db.Text, nullable=True)
    - directorate = db.Column(db.Text, nullable=True)

    Table "public.projects_funding"
        Column    |  Type   | Collation | Nullable |                   Default
    --------------+---------+-----------+----------+----------------------------------------------
     projects_id  | integer |           | not null |
     agency       | text    |           | not null |
     agency_other | text    |           |          |
     award_amount | text    |           |          |
     award_number | text    |           |          |
     directorate  | text    |           |          |
     id           | integer |           | not null | nextval('projects_funding_id_seq'::regclass)
    """
    try:
        projects_funding = []
        fab_projects_funding = ProjectsFunding.query.order_by('id').all()
        for pf in fab_projects_funding:
            data = {
                'agency': pf.agency,
                'agency_other': pf.agency_other,
                'award_amount': pf.award_amount,
                'award_number': pf.award_number,
                'directorate': pf.directorate,
                'id': pf.id,
                'projects_id': pf.projects_id
            }
            projects_funding.append(data)
        output_dict = {'projects_funding': projects_funding}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_funding-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_members as JSON output file
def dump_projects_members_data():
    """
    projects_members
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    Table "public.projects_members"
       Column    |  Type   | Collation | Nullable | Default
    -------------+---------+-----------+----------+---------
     people_id   | integer |           | not null |
     projects_id | integer |           | not null |
    """
    try:
        projects_members = []
        query = text("SELECT people_id, projects_id FROM projects_members")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'people_id': row[0],
                'projects_id': row[1]
            }
            projects_members.append(data)
        output_dict = {'projects_members': projects_members}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_members-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_owners as JSON output file
def dump_projects_owners_data():
    """
    projects_owners
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    Table "public.projects_owners"
       Column    |  Type   | Collation | Nullable | Default
    -------------+---------+-----------+----------+---------
     people_id   | integer |           | not null |
     projects_id | integer |           | not null |
    """
    try:
        projects_owners = []
        query = text("SELECT people_id, projects_id FROM projects_owners")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'people_id': row[0],
                'projects_id': row[1]
            }
            projects_owners.append(data)
        output_dict = {'projects_owners': projects_owners}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_owners-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_projects_storage_data():
    """
    projects_storage
    - storage_id = db.Column('storage_id', db.Integer, db.ForeignKey('storage.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    Table "public.projects_storage"
       Column    |  Type   | Collation | Nullable | Default
    -------------+---------+-----------+----------+---------
     storage_id  | integer |           | not null |
     projects_id | integer |           | not null |
    """
    try:
        projects_storage = []
        query = text("SELECT storage_id, projects_id FROM projects_storage")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'storage_id': row[0],
                'projects_id': row[1]
            }
            projects_storage.append(data)
        output_dict = {'projects_storage': projects_storage}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_storage-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_tags as JSON output file
def dump_projects_tags_data():
    """
    ProjectsTags(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - projects_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    - tag = db.Column(db.Text, nullable=False)

    Table "public.projects_tags"
       Column    |  Type   | Collation | Nullable |                  Default
    -------------+---------+-----------+----------+-------------------------------------------
     projects_id | integer |           | not null |
     tag         | text    |           | not null |
     id          | integer |           | not null | nextval('projects_tags_id_seq'::regclass)
    """
    try:
        projects_tags = []
        fab_projects_tags = ProjectsTags.query.order_by('id').all()
        for t in fab_projects_tags:
            data = {
                'id': t.id,
                'projects_id': t.projects_id,
                'tag': t.tag
            }
            projects_tags.append(data)
        output_dict = {'projects_tags': projects_tags}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_tags-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export projects_topics as JSON output file
def dump_projects_topics_data():
    """
    projects_topics
    - id - primary key (BaseMixin)
    - projects_id - foreignkey link to projects table
    - topic - topic as string

    Table "public.projects_topics"
       Column    |  Type   | Collation | Nullable |                   Default
    -------------+---------+-----------+----------+---------------------------------------------
     projects_id | integer |           | not null |
     topic       | text    |           | not null |
     id          | integer |           | not null | nextval('projects_topics_id_seq'::regclass)
    """
    try:
        projects_topics = []
        fab_projects_topics = ProjectsTopics.query.order_by('id').all()
        for t in fab_projects_topics:
            data = {
                'id': t.id,
                'projects_id': t.projects_id,
                'topic': t.topic
            }
            projects_topics.append(data)
        output_dict = {'projects_topics': projects_topics}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/projects_topics-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export sshkeys as JSON output file
def dump_sshkeys_data():
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

    Table "public.sshkeys"
           Column       |           Type           | Collation | Nullable |               Default
    --------------------+--------------------------+-----------+----------+-------------------------------------
     active             | boolean                  |           | not null |
     comment            | character varying        |           |          |
     deactivated_on     | timestamp with time zone |           |          |
     deactivated_reason | character varying        |           |          |
     description        | character varying        |           |          |
     expires_on         | timestamp with time zone |           | not null |
     fabric_key_type    | enumsshkeytypes          |           | not null |
     fingerprint        | character varying        |           |          |
     people_id          | integer                  |           | not null |
     public_key         | character varying        |           |          |
     ssh_key_type       | character varying        |           |          |
     status             | enumsshkeystatus         |           | not null |
     uuid               | character varying        |           | not null |
     id                 | integer                  |           | not null | nextval('sshkeys_id_seq'::regclass)
     created            | timestamp with time zone |           | not null |
     modified           | timestamp with time zone |           |          |
    """
    try:
        sshkeys = []
        fab_sshkeys = FabricSshKeys.query.order_by('id').all()
        for k in fab_sshkeys:
            data = {
                'active': k.active,
                'comment': k.comment,
                'created': normalize_date_to_utc(date_str=str(k.created), return_type='str') if k.created else None,
                'deactivated_on': normalize_date_to_utc(date_str=str(k.deactivated_on),
                                                        return_type='str') if k.deactivated_on else None,
                'deactivated_reason': k.deactivated_reason,
                'description': k.description,
                'expires_on': normalize_date_to_utc(date_str=str(k.expires_on),
                                                    return_type='str') if k.expires_on else None,
                'fabric_key_type': str(k.fabric_key_type.name),
                'fingerprint': k.fingerprint,
                'id': k.id,
                'modified': normalize_date_to_utc(date_str=str(k.modified), return_type='str') if k.modified else None,
                'people_id': k.people_id,
                'public_key': k.public_key,
                'ssh_key_type': str(k.ssh_key_type),
                'status': str(k.status.name),
                'uuid': k.uuid
            }
            sshkeys.append(data)
        output_dict = {'sshkeys': sshkeys}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/sshkeys-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_storage_data():
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

    Table "public.storage"
          Column      |           Type           | Collation | Nullable |               Default
    ------------------+--------------------------+-----------+----------+-------------------------------------
     active           | boolean                  |           | not null |
     expires_on       | timestamp with time zone |           | not null |
     project_id       | integer                  |           | not null |
     requested_by_id  | integer                  |           | not null |
     uuid             | character varying        |           | not null |
     volume_name      | character varying        |           |          |
     volume_size_gb   | integer                  |           |          |
     id               | integer                  |           | not null | nextval('storage_id_seq'::regclass)
     created          | timestamp with time zone |           | not null |
     modified         | timestamp with time zone |           |          |
     created_by_uuid  | character varying        |           |          |
     modified_by_uuid | character varying        |           |          |
    """
    try:
        storage = []
        fab_storage = FabricStorage.query.order_by('id').all()
        for s in fab_storage:
            data = {
                'active': s.active,
                'created': normalize_date_to_utc(date_str=str(s.created), return_type='str'),
                'created_by_uuid': str(s.created_by_uuid),
                'expires_on': normalize_date_to_utc(date_str=str(s.expires_on), return_type='str'),
                'id': s.id,
                'modified': normalize_date_to_utc(date_str=str(s.modified), return_type='str'),
                'modified_by_uuid': str(s.modified_by_uuid),
                'project_id': s.project_id,
                'requested_by_id': s.requested_by_id,
                'sites': [site.id for site in s.sites],  # [StorageSites.id]
                'uuid': str(s.uuid),
                'volume_name': s.volume_name,
                'volume_size_gb': s.volume_size_gb
            }
            storage.append(data)
        output_dict = {'storage': storage}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(storage, indent=2))
        with open(BACKUP_DATA_DIR + '/storage-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_storage_sites_data():
    """
    StorageSites(BaseMixin, db.Model)
    - id = db.Column(db.Integer, nullable=False, primary_key=True)
    - storage_id = db.Column(db.Integer, db.ForeignKey('storage.id'), nullable=False)
    - site = db.Column(db.Text, nullable=False)

    Table "public.storage_sites"
       Column   |  Type   | Collation | Nullable |                  Default
    ------------+---------+-----------+----------+-------------------------------------------
     storage_id | integer |           | not null |
     site       | text    |           | not null |
     id         | integer |           | not null | nextval('storage_sites_id_seq'::regclass)
    """
    try:
        storage_sites = []
        fab_storage_sites = StorageSites.query.order_by('id').all()
        for s in fab_storage_sites:
            data = {
                'id': s.id,
                'storage_id': s.storage_id,
                'site': s.site
            }
            storage_sites.append(data)
        output_dict = {'storage_sites': storage_sites}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(storage_sites, indent=2))
        with open(BACKUP_DATA_DIR + '/storage_sites-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_task_timeout_tracker_data():
    """
    Task Timeout Tracker
    - description
    - * id - primary key (BaseMixin)
    - last_updated
    - name
    - timeout_in_seconds
    - uuid
    - value

    Table "public.task_timeout_tracker"
           Column       |           Type           | Collation | Nullable |                     Default
    --------------------+--------------------------+-----------+----------+--------------------------------------------------
     description        | character varying        |           | not null |
     last_updated       | timestamp with time zone |           | not null |
     name               | character varying        |           | not null |
     timeout_in_seconds | integer                  |           | not null |
     uuid               | character varying        |           | not null |
     value              | character varying        |           |          |
     id                 | integer                  |           | not null | nextval('task_timeout_tracker_id_seq'::regclass)
    """
    try:
        task_timeout_tracker = []
        fab_storage_sites = TaskTimeoutTracker.query.order_by('id').all()
        for t in fab_storage_sites:
            data = {
                'description': t.description,
                'id': t.id,
                'last_updated': normalize_date_to_utc(date_str=str(t.last_updated), return_type='str'),
                'name': t.name,
                'timeout_in_seconds': int(t.timeout_in_seconds),
                'uuid': t.uuid,
                'value': t.value
            }
            task_timeout_tracker.append(data)
        output_dict = {'task_timeout_tracker': task_timeout_tracker}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(task_timeout_tracker, indent=2))
        with open(BACKUP_DATA_DIR + '/task_timeout_tracker-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export testbed_info as JSON output file
def dump_testbed_info_data():
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

    Table "public.testbed_info"
          Column      |           Type           | Collation | Nullable |                 Default
    ------------------+--------------------------+-----------+----------+------------------------------------------
     is_active        | boolean                  |           |          |
     json_data        | jsonb                    |           | not null |
     uuid             | character varying        |           | not null |
     id               | integer                  |           | not null | nextval('testbed_info_id_seq'::regclass)
     created          | timestamp with time zone |           | not null |
     modified         | timestamp with time zone |           |          |
     created_by_uuid  | character varying        |           |          |
     modified_by_uuid | character varying        |           |          |
    """
    try:
        testbed_info = []
        fab_testbed_info = FabricTestbedInfo.query.order_by('id').all()
        for i in fab_testbed_info:
            data = {
                'created': normalize_date_to_utc(date_str=str(i.created), return_type='str') if i.created else None,
                'created_by_uuid': str(i.created_by_uuid),
                'id': i.id,
                'is_active': i.is_active,
                'json_data': i.json_data,
                'modified': normalize_date_to_utc(date_str=str(i.modified), return_type='str') if i.modified else None,
                'modified_by_uuid': str(i.modified_by_uuid),
                'uuid': str(i.uuid)
            }
            testbed_info.append(data)
        output_dict = {'testbed_info': testbed_info}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/testbed_info-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


# export token_holders as JSON output file
def dump_token_holders_data():
    """
    token_holders
    - people_id = db.Column('people_id', db.Integer, db.ForeignKey('people.id'), primary_key=True),
    - projects_id = db.Column('projects_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True)

    Table "public.token_holders"
       Column    |  Type   | Collation | Nullable | Default
    -------------+---------+-----------+----------+---------
     people_id   | integer |           | not null |
     projects_id | integer |           | not null |
    """
    try:
        token_holders = []
        query = text("SELECT people_id, projects_id FROM token_holders")
        result = db.session.execute(query).fetchall()
        for row in result:
            data = {
                'people_id': row[0],
                'projects_id': row[1]
            }
            token_holders.append(data)
        output_dict = {'token_holders': token_holders}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/token_holders-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_user_org_affiliations_data():
    """
    UserOrgAffiliations(BaseMixin, db.Model):
    - id - primary key (BaseMixin)
    - people_id - foreignkey link to people table
    - affiliation - affiliation as string

    Table "public.user_org_affiliations"
       Column    |  Type   | Collation | Nullable |                      Default
    -------------+---------+-----------+----------+---------------------------------------------------
     people_id   | integer |           | not null |
     affiliation | text    |           | not null |
     id          | integer |           | not null | nextval('user_org_affiliations_id_seq'::regclass)
    """
    try:
        user_org_affiliations = []
        fab_user_org_affiliations = UserOrgAffiliations.query.order_by('id').all()
        for i in fab_user_org_affiliations:
            data = {
                'affiliation': i.affiliation,
                'id': i.id,
                'people_id': i.people_id
            }
            user_org_affiliations.append(data)
        output_dict = {'user_org_affiliations': user_org_affiliations}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/user_org_affiliations-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


def dump_user_subject_identifiers_data():
    """
    UserSubjectIdentifiers(BaseMixin, db.Model):
    - id - primary key (BaseMixin)
    - people_id - foreignkey link to people table
    - sub - subject identifier as string

    Table "public.user_subject_identifiers"
      Column   |  Type   | Collation | Nullable |                       Default
    -----------+---------+-----------+----------+------------------------------------------------------
     people_id | integer |           | not null |
     sub       | text    |           | not null |
     id        | integer |           | not null | nextval('user_subject_identifiers_id_seq'::regclass)
    """
    try:
        user_subject_identifiers = []
        fab_user_subject_identifiers = UserSubjectIdentifiers.query.order_by('id').all()
        for i in fab_user_subject_identifiers:
            data = {
                'id': i.id,
                'people_id': i.people_id,
                'sub': i.sub
            }
            user_subject_identifiers.append(data)
        output_dict = {'user_subject_identifiers': user_subject_identifiers}
        output_json = json.dumps(output_dict, indent=2)
        # print(json.dumps(output_dict, indent=2))
        with open(BACKUP_DATA_DIR + '/user_subject_identifiers-v{0}.json'.format(__API_VERSION__), 'w') as outfile:
            outfile.write(output_json)
    except Exception as exc:
        consoleLogger.error(exc)


if __name__ == '__main__':
    app.app_context().push()
    consoleLogger.info('Exporter for API version {0}'.format(__API_VERSION__))
    #                    List of relations
    #  Schema |           Name            | Type  |  Owner
    # --------+---------------------------+-------+----------
    #  public | alembic_version           | table | postgres
    consoleLogger.info('dump alembic_version table')
    dump_alembic_version_data()

    #  public | announcements             | table | postgres
    consoleLogger.info('dump announcements table')
    dump_announcements_data()

    #  public | core_api_metrics          | table | postgres
    consoleLogger.info('dump core_api_metrics table')
    dump_core_api_metrics_data()

    #  public | groups                    | table | postgres
    consoleLogger.info('dump groups table')
    dump_groups_data()

    #  public | people                    | table | postgres
    consoleLogger.info('dump people table')
    dump_people_data()

    #  public | people_email_addresses    | table | postgres
    consoleLogger.info('dump people_email_addresses table')
    dump_people_email_addresses_data()

    #  public | people_organizations      | table | postgres
    consoleLogger.info('dump people_organizations table')
    dump_people_organizations_data()

    #  public | people_roles              | table | postgres
    consoleLogger.info('dump people_roles table')
    dump_people_roles_data()

    #  public | preferences               | table | postgres
    consoleLogger.info('dump preferences table')
    dump_preferences_data()

    #  public | profiles_keywords         | table | postgres
    consoleLogger.info('dump profiles_keywords table')
    dump_profiles_keywords_data()

    #  public | profiles_other_identities | table | postgres
    consoleLogger.info('dump profiles_other_identities table')
    dump_profiles_other_identities_data()

    #  public | profiles_people           | table | postgres
    consoleLogger.info('dump profiles_people table')
    dump_profiles_people_data()

    #  public | profiles_personal_pages   | table | postgres
    consoleLogger.info('dump profiles_personal_pages table')
    dump_profiles_personal_pages_data()

    #  public | profiles_projects         | table | postgres
    consoleLogger.info('dump profiles_projects table')
    dump_profiles_projects_data()

    #  public | profiles_references       | table | postgres
    consoleLogger.info('dump profiles_references table')
    dump_profiles_references_data()

    #  public | projects                  | table | postgres
    consoleLogger.info('dump projects table')
    dump_projects_data()

    # public | projects_communities       | table | postgres
    consoleLogger.info('dump projects_communities table')
    dump_projects_communities_data()

    #  public | projects_creators         | table | postgres
    consoleLogger.info('dump projects_creators table')
    dump_projects_creators_data()

    # public | projects_funding           | table | postgres
    consoleLogger.info('dump projects_funding table')
    dump_projects_funding_data()

    #  public | projects_members          | table | postgres
    consoleLogger.info('dump projects_members table')
    dump_projects_members_data()

    #  public | projects_owners           | table | postgres
    consoleLogger.info('dump projects_owners table')
    dump_projects_owners_data()

    #  public | projects_storage          | table | postgres
    consoleLogger.info('dump projects_storage table')
    dump_projects_storage_data()

    #  public | projects_tags             | table | postgres
    consoleLogger.info('dump projects_tags table')
    dump_projects_tags_data()

    #  public | projects_topics           | table | postgres
    consoleLogger.info('dump projects_topics table')
    dump_projects_topics_data()

    #  public | sshkeys                   | table | postgres
    consoleLogger.info('dump sshkeys table')
    dump_sshkeys_data()

    #  public | storage                   | table | postgres
    consoleLogger.info('dump storage table')
    dump_storage_data()

    #  public | storage_sites             | table | postgres
    consoleLogger.info('dump storage_sites table')
    dump_storage_sites_data()

    #  public | task_timeout_tracker      | table | postgres
    consoleLogger.info('dump task_timeout_tracker table')
    dump_task_timeout_tracker_data()

    #  public | testbed_info              | table | postgres
    consoleLogger.info('dump testbed_info table')
    dump_testbed_info_data()

    #  public | token_holders             | table | postgres
    consoleLogger.info('dump token_holders table')
    dump_token_holders_data()

    #  public | user_org_affiliations     | table | postgres
    consoleLogger.info('dump user_org_affiliations table')
    dump_user_org_affiliations_data()

    #  public | user_subject_identifiers  | table | postgres
    consoleLogger.info('dump user_subject_identifiers table')
    dump_user_subject_identifiers_data()
