"""
REV: v1.10.0
v1.9.0 --> v1.10.0 - database tables

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

Changes from v1.9.0 --> v1.10.0
- NULL out co_cou_id_pc for all projects (project creators decoupled from COmanage)
"""

import json
import os
from datetime import datetime, timezone

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.projects import FabricProjects

# API version of data to restore from
api_version = '1.9.0'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


def projects_export_co_cou_id_pc():
    """
    Export co_cou_id_pc values to a JSON file before NULLing them.
    This manifest can be used to purge the orphaned -pc COUs from the
    remote COmanage registry on a separate schedule.

    Output: BACKUP_DATA_DIR/comanage_pc_cous_to_purge.json
    """
    try:
        cous_to_purge = []
        fab_projects = FabricProjects.query.order_by('id').all()
        for fp in fab_projects:
            if fp.co_cou_id_pc is not None:
                cous_to_purge.append({
                    'project_uuid': str(fp.uuid),
                    'project_name': fp.name,
                    'co_cou_id_pc': fp.co_cou_id_pc,
                    'cou_name': str(fp.uuid) + '-pc'
                })
        output = {
            'description': 'Project-creator COUs to purge from COmanage registry (v1.9.0 -> v1.10.0)',
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'count': len(cous_to_purge),
            'cous': cous_to_purge
        }
        output_file = BACKUP_DATA_DIR + '/comanage_pc_cous_to_purge.json'
        with open(output_file, 'w') as outfile:
            outfile.write(json.dumps(output, indent=2))
        consoleLogger.info('Exported {0} co_cou_id_pc entries to {1}'.format(len(cous_to_purge), output_file))
    except Exception as exc:
        consoleLogger.error(exc)


def projects_null_co_cou_id_pc():
    """
    NULL out co_cou_id_pc for all projects
    - project creators decoupled from COmanage in v1.10.0
    - creator membership now tracked via projects_creators junction table only
    """
    try:
        fab_projects = FabricProjects.query.all()
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1}'.format(fp.id, fp.uuid))
            if fp.co_cou_id_pc is not None:
                print(' - NULL out co_cou_id_pc (was {0})'.format(fp.co_cou_id_pc))
                fp.co_cou_id_pc = None
                db.session.commit()
            else:
                print(' - co_cou_id_pc already NULL')

    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Update data from API version {0}'.format(api_version))

    # Projects: export co_cou_id_pc values before NULLing
    consoleLogger.info('Projects: exporting co_cou_id_pc manifest for COmanage COU purge')
    projects_export_co_cou_id_pc()

    # Projects: NULL out co_cou_id_pc (creators decoupled from COmanage)
    consoleLogger.info('Projects: NULL out co_cou_id_pc (creators decoupled from COmanage)')
    projects_null_co_cou_id_pc()
