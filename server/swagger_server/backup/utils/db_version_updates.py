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
- Backfill created_by_uuid from projects_creators or project_lead
"""

import json
import os
from datetime import datetime, timezone
from uuid import uuid4

from swagger_server.__main__ import app, db
from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.people import FabricGroups, FabricRoles
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.quotas import EnumResourceTypes, EnumResourceUnits, FabricQuotas
from swagger_server.database.models.storage import FabricStorage

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


def storage_align_expires_on_with_project():
    """
    Backfill: align storage expires_on with the expires_on of the associated project.
    - Only updates storage where the dates differ and the project has an expires_on set.
    """
    try:
        updated = 0
        fab_storage_all = FabricStorage.query.all()
        for fs in fab_storage_all:
            fp = FabricProjects.query.filter_by(id=fs.project_id).one_or_none()
            if fp and fp.expires_on and fs.expires_on != fp.expires_on:
                print(' - Storage uuid={0}: expires_on {1} -> {2} (project uuid={3})'.format(
                    fs.uuid, fs.expires_on, fp.expires_on, fp.uuid))
                fs.expires_on = fp.expires_on
                updated += 1
        db.session.commit()
        consoleLogger.info('Aligned expires_on for {0} storage allocation(s)'.format(updated))
    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


def projects_backfill_created_by_uuid():
    """
    Backfill created_by_uuid for projects that are missing it.
    - First tries the projects_creators junction table (takes the first creator)
    - Falls back to the project_lead relationship
    """
    try:
        updated = 0
        skipped = 0
        fab_projects = FabricProjects.query.order_by('id').all()
        for fp in fab_projects:
            if fp.created_by_uuid is not None:
                continue
            creator_uuid = None
            # try projects_creators first
            if fp.project_creators:
                creator_uuid = str(fp.project_creators[0].uuid)
                source = 'projects_creators'
            # fall back to project_lead
            elif fp.project_lead:
                creator_uuid = str(fp.project_lead.uuid)
                source = 'project_lead'
            if creator_uuid:
                print(' - Project id={0} ({1}): set created_by_uuid={2} (from {3})'.format(
                    fp.id, fp.name, creator_uuid, source))
                fp.created_by_uuid = creator_uuid
                updated += 1
            else:
                print(' - Project id={0} ({1}): no creator found, skipping'.format(fp.id, fp.name))
                skipped += 1
        db.session.commit()
        consoleLogger.info('Backfilled created_by_uuid for {0} project(s), skipped {1}'.format(updated, skipped))
    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


def projects_export_creator_owners_report():
    """
    Export a markdown report of project creators vs. owners.
    Flags projects where the creator is not an owner.

    Output: BACKUP_DATA_DIR/project_creator_owners.md
    """
    try:
        fab_projects = FabricProjects.query.order_by('id').all()
        lines = [
            '# Project Creator vs. Owner Report',
            '',
            'Generated: {0}'.format(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
            '',
            '| Project | Creator | Owners | Creator is Owner? |',
            '|---|---|---|---|',
        ]
        mismatch_count = 0
        for fp in fab_projects:
            creator_entries = ['{0} ({1})'.format(p.display_name, p.uuid) for p in fp.project_creators]
            owner_names = [p.display_name for p in fp.project_owners]
            creator_set = set(c.id for c in fp.project_creators)
            owner_set = set(o.id for o in fp.project_owners)
            not_owners = creator_set - owner_set
            if not_owners:
                flag = '**No**'
                mismatch_count += 1
                lines.append('| **{0} ({1})** | **{2}** | **{3}** | {4} |'.format(
                    fp.name,
                    fp.uuid,
                    ', '.join(creator_entries) if creator_entries else '*(none)*',
                    ', '.join(owner_names) if owner_names else '*(none)*',
                    flag,
                ))
            else:
                flag = 'Yes' if creator_set else 'N/A'
                lines.append('| {0} ({1}) | {2} | {3} | {4} |'.format(
                    fp.name,
                    fp.uuid,
                    ', '.join(creator_entries) if creator_entries else '*(none)*',
                    ', '.join(owner_names) if owner_names else '*(none)*',
                    flag,
                ))
        lines.append('')
        lines.append('**{0}** project(s) where a creator is not an owner.'.format(mismatch_count))
        lines.append('')

        output_file = BACKUP_DATA_DIR + '/project_creator_owners.md'
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
        consoleLogger.info('Exported creator/owner report to {0}'.format(output_file))
    except Exception as exc:
        consoleLogger.error(exc)


def cleanup_pc_roles_and_groups():
    """
    v1.10.0: drop stale `<uuid>-pc` entries from FabricRoles and FabricGroups.

    Project-creator membership is no longer represented as a COmanage role.
    After Phase 4a (purge_pc_cous.py) deletes the COUs from COmanage, the
    next `update_people_roles` sync will eventually clean up FabricRoles,
    but FabricGroups isn't touched by that sync. This function does both
    proactively so the local DB lands in a consistent state.

    Run this AFTER `purge_pc_cous.py` has completed (Phase 4a). Running it
    earlier is harmless, but the next COmanage sync would recreate the rows.
    """
    try:
        deleted_roles = FabricRoles.query.filter(
            FabricRoles.name.like('%-pc')
        ).delete(synchronize_session=False)
        deleted_groups = FabricGroups.query.filter(
            FabricGroups.name.like('%-pc')
        ).delete(synchronize_session=False)
        db.session.commit()
        consoleLogger.info(
            'Removed {0} stale -pc role(s) and {1} stale -pc group(s)'.format(
                deleted_roles, deleted_groups))
    except Exception as exc:
        consoleLogger.error(exc)
        db.session.rollback()


def quotas_backfill_missing_resource_types():
    """
    Ensure every project has one FabricQuotas row per current EnumResourceTypes
    member.

    A project created on an older schema may be missing rows for resource
    types added in v1.10.0 (smartnic_connectx_7_100, smartnic_connectx_7_400).
    Conversely, the obsolete smartnic_bluefield_2_connectx_6 row is removed
    by the Alembic migration before this runs.

    Defaults for newly-inserted rows match `create_fabric_project_from_api`:
      - quota_limit = 0.0
      - quota_used  = 0.0
      - resource_unit = hours
    Existing rows are left untouched.

    This function is idempotent — running it twice is a no-op on the second
    pass. It must be invoked AFTER the Alembic migration that adds the new
    ENUM values, otherwise the inserts will fail.
    """
    try:
        now = datetime.now(timezone.utc)
        added_total = 0
        fab_projects = FabricProjects.query.order_by('id').all()
        for fp in fab_projects:
            existing_types = {
                q.resource_type.name
                for q in FabricQuotas.query.filter_by(project_uuid=str(fp.uuid)).all()
            }
            missing_types = [
                rt for rt in EnumResourceTypes if rt.name not in existing_types
            ]
            if not missing_types:
                continue
            for rt in missing_types:
                fab_quota = FabricQuotas()
                fab_quota.created_at = now
                fab_quota.project_uuid = str(fp.uuid)
                fab_quota.quota_limit = 0.0
                fab_quota.quota_used = 0.0
                fab_quota.resource_type = rt.name
                fab_quota.resource_unit = EnumResourceUnits.hours.name
                fab_quota.updated_at = now
                fab_quota.uuid = str(uuid4())
                db.session.add(fab_quota)
                added_total += 1
                print(' - Project id={0} ({1}): added quota for resource_type={2}'.format(
                    fp.id, fp.name, rt.name))
            db.session.commit()
        consoleLogger.info('Backfilled {0} missing quota row(s) across {1} project(s)'.format(
            added_total, len(fab_projects)))
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

    # Projects: backfill created_by_uuid from projects_creators or project_lead
    consoleLogger.info('Projects: backfilling created_by_uuid for projects missing it')
    projects_backfill_created_by_uuid()

    # Projects: export creator vs. owner report
    consoleLogger.info('Projects: exporting creator vs. owner report')
    projects_export_creator_owners_report()

    # Storage: align expires_on with project expires_on
    consoleLogger.info('Storage: aligning storage expires_on with project expires_on')
    storage_align_expires_on_with_project()

    # Quotas: backfill any missing resource_type rows on existing projects
    consoleLogger.info('Quotas: backfilling missing resource_type rows for existing projects')
    quotas_backfill_missing_resource_types()
