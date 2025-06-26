"""
REV: v1.8.1
v1.8.0 --> v1.8.1 - database tables

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

Changes from v1.8.0 --> v1.8.1
- update table: quotas, EnumResourceTypes changes
- update existing projects data with new logic
- backfill core_api_events data
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.core_api_metrics import CoreApiEvents, EnumEvents, EnumEventTypes
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.quotas import EnumResourceTypes, EnumResourceUnits, FabricQuotas
from swagger_server.response_code.core_api_utils import add_core_api_event

# API version of data to restore from
api_version = '1.8.0'

# relative to the top level of the repository
BACKUP_DATA_DIR = os.getcwd() + '/server/swagger_server/backup/data'


def projects_project_lead_backfill():
    """
    Backfill projects project_lead information
    - make first project owner the project lead
    - if no project owner exists, make the project creator the project lead
    """
    default_pl = FabricPeople.query.filter(
        FabricPeople.uuid == '593dd0d3-cedb-4bc6-9522-a945da0a8a8e'
    ).first()
    try:
        fab_projects = FabricProjects.query.all()
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1}'.format(fp.id, fp.uuid))
            po_list = fp.project_owners
            print(' - ', po_list)
            if len(po_list) > 0:
                proj_lead = po_list[0]
            elif len(fp.project_creators) > 0:
                proj_lead = fp.project_creators[0]
            else:
                proj_lead = default_pl
            print(' - ', proj_lead)
            fp.project_lead = proj_lead
            db.session.commit()

    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


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


def projects_retire_after_365_days_expired():
    """
    Migrate projects that have expired for more than 180 days to retired status
    """
    try:
        fab_projects = FabricProjects.query.order_by(FabricProjects.created).all()
        now = datetime.now(timezone.utc)
        retire_check_date = now - timedelta(days=int(os.getenv('PROJECTS_RETIRE_POST_EXPIRY_IN_DAYS')))
        for fp in fab_projects:
            consoleLogger.info('Project: id {0}, uuid {1} created: {2}'.format(fp.id, fp.uuid, fp.created))
            # Retired projects
            if fp.expires_on < retire_check_date:
                if not fp.retired_date:
                    fp.retired_date = now
                fp.active = False
                fp.is_locked = True
                fp.review_required = False
                console_output = ' - Retired on date: {0}'.format(fp.retired_date)
            # Expired projects
            elif retire_check_date < fp.expires_on < now:
                fp.active = False
                fp.is_locked = False
                fp.retired_date = None
                fp.review_required = True
                console_output = ' - Expired on date: {0}'.format(fp.expires_on)
            # Active projects
            elif fp.expires_on > now:
                fp.active = True
                fp.is_locked = False
                fp.retired_date = None
                fp.review_required = False
                console_output = ' - Active until date: {0}'.format(fp.expires_on)
            # Should not get here
            else:
                fp.active = False
                fp.is_locked = True
                fp.retired_date = None
                fp.review_required = True
                console_output = ' - Unknown status date: {0}'.format(fp.expires_on)
            db.session.commit()
            consoleLogger.info(console_output)
    except Exception as exc:
        consoleLogger.error(exc)


def backfill_core_api_projects():
    """
    Generate core api events for existing projects

    add_core_api_event(event, event_date, event_triggered_by, event_type,
                       people_uuid, project_is_public, project_uuid):
    """
    projects = FabricProjects.query.order_by(FabricProjects.created).all()
    for fp in projects:
        # event project_create
        event = EnumEvents.project_create.name
        event_date = fp.created
        if len(fp.project_creators) > 0:
            event_triggered_by = fp.project_creators[0].uuid
        else:
            event_triggered_by = os.getenv('SERVICE_ACCOUNT_UUID')
        event_type = EnumEventTypes.projects.name
        people_uuid = event_triggered_by
        project_is_public = fp.is_public
        project_uuid = fp.uuid
        add_core_api_event(
            event=event,
            event_date=event_date,
            event_triggered_by=event_triggered_by,
            event_type=event_type,
            people_uuid=people_uuid,
            project_uuid=project_uuid,
            project_is_public=project_is_public
        )
        # check for project_retire
        if fp.retired_date:
            if not CoreApiEvents.query.filter(
                    CoreApiEvents.project_uuid == project_uuid,
                    CoreApiEvents.event == EnumEvents.project_retire.name
            ).first():
                event = EnumEvents.project_retire.name
                event_date = fp.retired_date
                people_uuid = event_triggered_by
                event_triggered_by = os.getenv('SERVICE_ACCOUNT_UUID')
                add_core_api_event(
                    event=event,
                    event_date=event_date,
                    event_triggered_by=event_triggered_by,
                    event_type=event_type,
                    people_uuid=people_uuid,
                    project_uuid=project_uuid,
                    project_is_public=project_is_public
                )


def backfill_core_api_people():
    """
    Generate core api events for existing people

    add_core_api_event(event, event_date, event_triggered_by, event_type,
                       people_uuid, project_is_public, project_uuid):
    """
    people = FabricPeople.query.order_by(FabricPeople.registered_on).all()
    for fp in people:
        # event people_create
        event = EnumEvents.people_create.name
        event_date = fp.registered_on
        event_triggered_by = fp.uuid
        event_type = EnumEventTypes.people.name
        people_uuid = fp.uuid
        project_is_public = None
        project_uuid = None
        add_core_api_event(
            event=event,
            event_date=event_date,
            event_triggered_by=event_triggered_by,
            event_type=event_type,
            people_uuid=people_uuid,
            project_uuid=project_uuid,
            project_is_public=project_is_public
        )
        # check for people_retire
        if not fp.active:
            if not CoreApiEvents.query.filter(
                    CoreApiEvents.people_uuid == people_uuid,
                    CoreApiEvents.event == EnumEvents.people_retire.name
            ).first():
                event = EnumEvents.people_retire.name
                event_date = datetime.now(timezone.utc)
                event_triggered_by = os.getenv('SERVICE_ACCOUNT_UUID')
                add_core_api_event(
                    event=event,
                    event_date=event_date,
                    event_triggered_by=event_triggered_by,
                    event_type=event_type,
                    people_uuid=people_uuid,
                    project_uuid=project_uuid,
                    project_is_public=project_is_public
                )
        # event project_creator/member/owner/tokenholder
        event_type = EnumEventTypes.projects.name
        for r in fp.roles:
            role_suffix = r.name[-3:]
            if role_suffix in ['-pc', '-pm', '-po', '-tk']:
                project_uuid = r.name[:-3]
                project = FabricProjects.query.filter_by(uuid=project_uuid).first()
                if project:
                    event = None
                    if role_suffix == '-pc':
                        event = EnumEvents.project_add_creator.name
                    elif role_suffix == '-pm':
                        event = EnumEvents.project_add_member.name
                    elif role_suffix == '-po':
                        event = EnumEvents.project_add_owner.name
                    elif role_suffix == '-tk':
                        event = EnumEvents.project_add_tokenholder.name
                    if fp.registered_on > project.created:
                        event_date = fp.registered_on
                    else:
                        event_date = project.created
                    if len(project.project_creators) > 0:
                        event_triggered_by = project.project_creators[0].uuid
                    else:
                        event_triggered_by = os.getenv('SERVICE_ACCOUNT_UUID')
                    people_uuid = fp.uuid
                    project_is_public = project.is_public
                    add_core_api_event(
                        event=event,
                        event_date=event_date,
                        event_triggered_by=event_triggered_by,
                        event_type=event_type,
                        people_uuid=people_uuid,
                        project_uuid=project_uuid,
                        project_is_public=project_is_public
                    )


if __name__ == '__main__':
    app.app_context().push()

    consoleLogger.info('Update data from API version {0}'.format(api_version))

    # Projects: backfill project_lead information for existing projects that don't already have it
    consoleLogger.info('Projects: backfill project_lead information for existing projects that don\'t already have it')
    projects_project_lead_backfill()
    #
    # # Projects: backfill quota information for existing projects that don't already have it
    # consoleLogger.info('Projects: backfill quota information for existing projects that don\'t already have it')
    # projects_quota_placeholder_backfill()
    #
    # # Projects: migrate projects that have expired for more than 365 days to retired status
    # consoleLogger.info('Projects: migrate projects that have expired for more than 365 days to retired status')
    # projects_retire_after_365_days_expired()
    #
    # # Projects: backfill core-api projects with event data
    # consoleLogger.info('Projects: backfill core-api projects with event data')
    # backfill_core_api_projects()
    #
    # # People: backfill core-api people with event data
    # consoleLogger.info('People: backfill core-api people with event data')
    # backfill_core_api_people()
