"""
v1.6.2 --> v1.7.0 - database tables

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

Changes from v1.6.2 --> v1.7.0
- table: people - added: receive_promotional_email
- TODO: table: projects_topics
- table: *core_api_metrics
- table: *projects_communities
- table: *projects_funding
- TODO: table: projects - added: *communities, *projects_funding, project_type, project_topics
"""

import os

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.projects import FabricProjects, ProjectsTags

# API version of data to restore from
api_version = '1.6.1'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


def projects_tags_slice_multisite_backfill():
    """
    Ensure that tag Slice.Multisite is applied to all projects
    """
    try:
        fab_projects = FabricProjects.query.all()
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1}'.format(fp.id, fp.uuid))
            fab_tag = ProjectsTags.query.filter(
                ProjectsTags.projects_id == fp.id,
                ProjectsTags.tag == 'Slice.Multisite'
            ).one_or_none()
            if not fab_tag:
                consoleLogger.info('  - add tag: Slice.Multisite to project: id {0}'.format(fp.id))
                fab_tag = ProjectsTags()
                fab_tag.projects_id = fp.id
                fab_tag.tag = 'Slice.Multisite'
                fp.tags.append(fab_tag)
                db.session.commit()
    except Exception as exc:
        consoleLogger.error(exc)


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Update data from API version {0}'.format(api_version))

    # Projects: backfill tag Slice.Multisite for all projects that don't already have it
    projects_tags_slice_multisite_backfill()
