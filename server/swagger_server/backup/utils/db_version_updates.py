"""
REV: v1.9.1
v1.9.0 --> v1.9.1 - database tables

                   List of relations
 Schema |           Name            | Type  |  Owner
--------+---------------------------+-------+----------
 public | alembic_version           | table | postgres  <-- alembic_version-v<VERSION>.json
 public | announcements             | table | postgres  <-- announcements-v<VERSION>.json
 public | core_api_events           | table | postgres  <-- core_api_events-v<VERSION>.json
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
(34 rows)

Changes from v1.9.0 --> v1.9.1
- backfill people: project_lead_approved
"""

import os

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.projects import FabricProjects

# API version of data to restore from
api_version = '1.9.0'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


def people_project_lead_approved_backfill():
    """
    Backfill project_lead_approved information
    - based on existing project_lead data in projects
    """
    try:
        fab_projects = FabricProjects.query.all()
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1}'.format(fp.id, fp.uuid))
            if fp.project_lead_id:
                pl = fp.project_lead
                if not pl.project_lead_approved:
                    print(' - set project_lead_approved = True for user {0}'.format(pl.uuid))
                    pl.project_lead_approved = True
                    db.session.commit()
                else:
                    print(' - project_lead_approved already True for user {0}'.format(pl.uuid))
            else:
                print(' - PROJECT LEAD NOT FOUND')

    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Update data from API version {0}'.format(api_version))

    # People: backfill project_lead_approved based on existing project_lead data in projects
    consoleLogger.info('People: backfill project_lead_approved based on existing project_lead data in projects')
    people_project_lead_approved_backfill()
