#!/usr/bin/env python3
"""
Purge project-leads role memberships from COmanage registry.

Reads the manifest file (comanage_project_leads_to_purge.json) and for each
listed role membership:
  1. Deletes the CoPersonRole entry (removes the user from the project-leads COU)

After all memberships are removed, the project-leads COU itself is deleted
unless --keep-cou is passed.

This script is standalone — it only requires the comanage_api library and the
COmanage API environment variables. It does not need the Flask app or database.

Usage:
    # Source env for COmanage API credentials
    source .env

    # Dry run (report what would be done, no changes)
    python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads --dry-run

    # Execute the purge (also deletes the project-leads COU at the end)
    python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads

    # Purge memberships only; leave the COU itself in place
    python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads --keep-cou

    # Or run directly
    PYTHONPATH=./server python server/versions/v1_9_0_to_v1_10_0/purge_project_leads.py --dry-run
"""

import argparse
import json
import os
import sys

from comanage_api import ComanageApi

# Default path to the manifest file (relative to the repository root)
DEFAULT_MANIFEST = os.path.join(
    os.path.dirname(__file__),
    '..', '..', 'swagger_server', 'backup', 'data', 'comanage_project_leads_to_purge.json'
)


def init_api() -> ComanageApi:
    """Initialize the COmanage API client from environment variables."""
    required_vars = [
        'COMANAGE_API_URL', 'COMANAGE_API_USER', 'COMANAGE_API_PASS',
        'COMANAGE_API_CO_ID', 'COMANAGE_API_CO_NAME'
    ]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print('ERROR: Missing required environment variables: {0}'.format(', '.join(missing)))
        print('       Source your .env file before running this script.')
        sys.exit(1)

    return ComanageApi(
        co_api_url=os.getenv('COMANAGE_API_URL'),
        co_api_user=os.getenv('COMANAGE_API_USER'),
        co_api_pass=os.getenv('COMANAGE_API_PASS'),
        co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
        co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
        co_ssh_key_authenticator_id=os.getenv('COMANAGE_API_SSH_KEY_AUTHENTICATOR_ID')
    )


def load_manifest(manifest_path: str) -> dict:
    """Load and return the project-leads purge manifest."""
    manifest_path = os.path.abspath(manifest_path)
    if not os.path.isfile(manifest_path):
        print('ERROR: Manifest file not found: {0}'.format(manifest_path))
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        data = json.load(f)

    cou = data.get('cou', {})
    memberships = data.get('memberships', [])
    print('Loaded manifest: {0} membership(s) in COU {1} ({2})'.format(
        len(memberships), cou.get('co_cou_id'), cou.get('name')))
    print('  Description: {0}'.format(data.get('description', '')))
    print('  Exported at: {0}'.format(data.get('exported_at', '')))
    print()
    return data


def purge_membership(api: ComanageApi, entry: dict, dry_run: bool = False) -> bool:
    """Delete a single CoPersonRole entry. Returns True on success."""
    role_id = entry['co_person_role_id']
    people_name = entry.get('people_name', '?')
    people_uuid = entry.get('people_uuid', '?')

    print('  role_id={0}: {1} ({2})'.format(role_id, people_name, people_uuid))

    if dry_run:
        print('    [DRY RUN] Would delete CoPersonRole {0}'.format(role_id))
        return True

    try:
        api.coperson_roles_delete(coperson_role_id=role_id)
        print('    Deleted CoPersonRole {0}'.format(role_id))
        return True
    except Exception as exc:
        print('    ERROR: Failed to delete CoPersonRole {0}: {1}'.format(role_id, exc))
        return False


def purge_cou(api: ComanageApi, cou: dict, dry_run: bool = False) -> bool:
    """Delete the project-leads COU itself. Returns True on success."""
    cou_id = cou['co_cou_id']
    cou_name = cou.get('name', '?')

    print('Deleting COU {0} ({1})'.format(cou_id, cou_name))
    if dry_run:
        print('  [DRY RUN] Would delete COU {0}'.format(cou_id))
        return True

    try:
        is_deleted = api.cous_delete(cou_id=cou_id)
        if is_deleted:
            print('  Deleted COU {0}'.format(cou_id))
            return True
        print('  ERROR: COU deletion returned False for {0}'.format(cou_id))
        return False
    except Exception as exc:
        print('  ERROR: Failed to delete COU {0}: {1}'.format(cou_id, exc))
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Purge project-leads role memberships (and optionally the COU) from COmanage'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be done without making changes'
    )
    parser.add_argument(
        '--keep-cou',
        action='store_true',
        help='Purge memberships but leave the project-leads COU itself in place'
    )
    parser.add_argument(
        '--manifest',
        default=DEFAULT_MANIFEST,
        help='Path to the comanage_project_leads_to_purge.json manifest file'
    )
    args = parser.parse_args()

    if args.dry_run:
        print('=== DRY RUN MODE — no changes will be made ===')
        print()

    api = init_api()
    data = load_manifest(args.manifest)
    cou = data.get('cou', {})
    memberships = data.get('memberships', [])

    if not memberships:
        print('No memberships to purge.')
    else:
        print('Processing {0} membership(s)...'.format(len(memberships)))
        print()

    success = 0
    failed = 0
    for entry in memberships:
        if purge_membership(api, entry, dry_run=args.dry_run):
            success += 1
        else:
            failed += 1
    if memberships:
        print()

    cou_deleted = None
    if args.keep_cou:
        print('--keep-cou specified; leaving COU {0} in place.'.format(cou.get('co_cou_id')))
    elif failed:
        print('Skipping COU deletion because {0} membership purge(s) failed.'.format(failed))
        cou_deleted = False
    elif cou:
        cou_deleted = purge_cou(api, cou, dry_run=args.dry_run)

    print()
    print('=' * 50)
    print('Summary:')
    print('  Memberships total:   {0}'.format(len(memberships)))
    print('  Memberships success: {0}'.format(success))
    print('  Memberships failed:  {0}'.format(failed))
    if cou_deleted is True:
        print('  COU deleted:         yes')
    elif cou_deleted is False:
        print('  COU deleted:         no (failed or skipped)')
    else:
        print('  COU deleted:         no (--keep-cou)')
    if args.dry_run:
        print('  (DRY RUN — no changes were made)')


if __name__ == '__main__':
    main()
