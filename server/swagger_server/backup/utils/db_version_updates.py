"""
REV: v1.8.1
v1.8.0 --> v1.8.1 - database tables

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

Changes from v1.8.0 --> v1.8.1
- update table: quotas, EnumResourceTypes changes
"""

import os
from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.quotas import EnumResourceTypes, EnumResourceUnits, FabricQuotas

# API version of data to restore from
api_version = '1.8.0'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


def projects_quota_placeholder_backfill():
    """
    Backfill projects quota placeholder for the following
    - p4 = "P4"
    - core = "Core"
    - ram = "RAM"
    - disk = "Disk"
    - gpu_rtx6000 = "GPU RTX6000"
    - gpu_tesla_t4 = "GPU TESLA T4"
    - gpu_a40 = "GPU A40"
    - gpu_a30 = "GPU A30"
    - sharednic_connectx_6 = "ShareDNIC ConnectX 6"
    - smartnic_bluefield_2_connectx_6 = "SmartNIC Bluefield 2 ConnectX 6"
    - smartnic_connectx_6 = "SmartNIC ConnectX 6"
    - smartnic_connectx_5 = "SmartNIC ConnectX 5"
    - nvme_p4510 = "NVME P4510"
    - storage_nas = "Storage NAS"
    - fpga_xilinx_u280 = "FPGA XILINX U280"
    - fpga_xilinx_sn1022 = "FPGA XILINX SN1022"
    """
    resource_types = [r.name for r in EnumResourceTypes]
    try:
        fab_projects = FabricProjects.query.all()
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1}'.format(fp.id, fp.uuid))
            fp_quota_objs = FabricQuotas.query.filter(FabricQuotas.project_uuid == fp.uuid).all()
            fp_quota_list = [q.resource_type.name for q in fp_quota_objs]
            for rt in resource_types:
                if rt not in fp_quota_list:
                    # create Quota
                    now = datetime.now(timezone.utc)
                    fab_quota = FabricQuotas()
                    fab_quota.created_at = now
                    fab_quota.project_uuid = fp.uuid
                    fab_quota.quota_limit = 0.0
                    fab_quota.quota_used = 0.0
                    fab_quota.resource_type = rt
                    fab_quota.resource_unit = EnumResourceUnits.hours.name
                    fab_quota.updated_at = now
                    fab_quota.uuid = str(uuid4())
                    try:
                        db.session.add(fab_quota)
                        db.session.commit()
                    except Exception as exc:
                        db.session.rollback()
                        details = 'Oops! something went wrong with projects_quota_placeholder_backfill(): {0}'.format(
                            exc)
                        print(details)
    except Exception as exc:
        consoleLogger.error(exc)


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Update data from API version {0}'.format(api_version))

    # Projects: backfill quota information for existing projects that don't already have it
    projects_quota_placeholder_backfill()
