#!/usr/bin/env python3
"""
Purge project-creator COUs from COmanage registry.

Reads the manifest file (comanage_pc_cous_to_purge.json) exported by
db_version_updates.py and for each entry:
  1. Removes all role memberships from the COU
  2. Deletes the COU itself

This script is standalone — it only requires the comanage_api library
and the COmanage API environment variables. It does not need the Flask
app or database.

Usage:
    # Source env for COmanage API credentials
    source .env

    # Dry run (report what would be done, no changes)
    python -m server.versions.v1_9_0_to_v1_10_0.purge_pc_cous --dry-run

    # Execute the purge
    python -m server.versions.v1_9_0_to_v1_10_0.purge_pc_cous

    # Or run directly
    PYTHONPATH=./server python server/versions/v1_9_0_to_v1_10_0/purge_pc_cous.py --dry-run
    PYTHONPATH=./server python server/versions/v1.9.0-to-v1.10.0/purge_pc_cous.py
"""

import argparse
import json
import os
import sys

from comanage_api import ComanageApi

# Default path to the manifest file (relative to the repository root)
DEFAULT_MANIFEST = os.path.join(
    os.path.dirname(__file__),
    '..', '..', 'swagger_server', 'backup', 'data', 'comanage_pc_cous_to_purge.json'
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


def load_manifest(manifest_path: str) -> list:
    """Load and return the COU purge manifest."""
    manifest_path = os.path.abspath(manifest_path)
    if not os.path.isfile(manifest_path):
        print('ERROR: Manifest file not found: {0}'.format(manifest_path))
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        data = json.load(f)

    cous = data.get('cous', [])
    print('Loaded manifest: {0} COUs to purge'.format(len(cous)))
    print('  Description: {0}'.format(data.get('description', '')))
    print('  Exported at: {0}'.format(data.get('exported_at', '')))
    print()
    return cous


def purge_cou(api: ComanageApi, cou_entry: dict, dry_run: bool = False) -> bool:
    """
    Purge a single project-creator COU.
    Returns True on success, False on failure.
    """
    cou_id = cou_entry['co_cou_id_pc']
    cou_name = cou_entry['cou_name']
    project_name = cou_entry['project_name']

    print('  [{0}] {1} (project: {2})'.format(cou_id, cou_name, project_name))

    # Step 1: Get all role memberships for this COU
    try:
        roles_response = api.coperson_roles_view_per_cou(cou_id=cou_id)
    except Exception as exc:
        print('    ERROR: Failed to list roles for COU {0}: {1}'.format(cou_id, exc))
        return False

    # Extract role IDs from the response
    role_ids = []
    if isinstance(roles_response, dict):
        co_person_roles = roles_response.get('CoPersonRoles', [])
        for role in co_person_roles:
            role_id = role.get('Id')
            if role_id:
                role_ids.append(int(role_id))

    print('    Found {0} role membership(s)'.format(len(role_ids)))

    # Step 2: Remove each role membership
    for role_id in role_ids:
        if dry_run:
            print('    [DRY RUN] Would delete role ID {0}'.format(role_id))
        else:
            try:
                api.coperson_roles_delete(coperson_role_id=role_id)
                print('    Deleted role ID {0}'.format(role_id))
            except Exception as exc:
                print('    ERROR: Failed to delete role ID {0}: {1}'.format(role_id, exc))
                return False

    # Step 3: Delete the COU itself
    if dry_run:
        print('    [DRY RUN] Would delete COU {0}'.format(cou_id))
    else:
        try:
            is_deleted = api.cous_delete(cou_id=cou_id)
            if is_deleted:
                print('    Deleted COU {0}'.format(cou_id))
            else:
                print('    ERROR: COU deletion returned False for {0}'.format(cou_id))
                return False
        except Exception as exc:
            print('    ERROR: Failed to delete COU {0}: {1}'.format(cou_id, exc))
            return False

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Purge project-creator COUs from COmanage registry'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Report what would be done without making changes'
    )
    parser.add_argument(
        '--manifest',
        default=DEFAULT_MANIFEST,
        help='Path to the comanage_pc_cous_to_purge.json manifest file'
    )
    args = parser.parse_args()

    if args.dry_run:
        print('=== DRY RUN MODE — no changes will be made ===')
        print()

    # Initialize API and load manifest
    api = init_api()
    cous = load_manifest(args.manifest)

    if not cous:
        print('No COUs to purge.')
        return

    # Process each COU
    success = 0
    failed = 0
    print('Processing {0} COUs...'.format(len(cous)))
    print()

    for cou_entry in cous:
        if purge_cou(api, cou_entry, dry_run=args.dry_run):
            success += 1
        else:
            failed += 1
        print()

    # Summary
    print('=' * 50)
    print('Summary:')
    print('  Total:   {0}'.format(len(cous)))
    print('  Success: {0}'.format(success))
    print('  Failed:  {0}'.format(failed))
    if args.dry_run:
        print('  (DRY RUN — no changes were made)')


if __name__ == '__main__':
    main()
