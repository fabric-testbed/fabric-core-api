"""Pre-flight: generate project_creator_owners.md against the v1.9.0 schema.

Mirrors `projects_export_creator_owners_report()` from db_version_updates.py,
but uses raw psycopg2 (no SQLAlchemy / Flask app) so it can be run BEFORE
Phase 1 against a still-live v1.9.0 deployment. Operators use the report to
reconcile creator/owner mismatches via the existing v1.9.0 API ahead of
Phase 0's full-backup, so the migration starts from a clean state.

Read-only: queries projects, people, projects_creators, projects_owners.
Makes no DB writes. Writes the markdown to stdout (caller redirects).

Required env vars (all already in .env on every deployment):
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
    POSTGRES_SERVER (default 'database'), POSTGRES_PORT (default '5432')

Recommended invocation — run inside the live v1.9.0 flask-server container
so the 'database' hostname resolves on the internal Docker network and
psycopg2 is already installed:

    docker cp server/versions/v1_9_0_to_v1_10_0/pre_flight_creator_owner_report.py \
        api-flask-server:/tmp/
    docker exec api-flask-server bash -lc \
        'source /code/.env && python /tmp/pre_flight_creator_owner_report.py' \
        > server/swagger_server/backup/data/project_creator_owners.md
"""

import os
import sys
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras


def connect():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_SERVER', 'database'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
    )


def main():
    with connect() as conn, conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT id, uuid, name FROM projects ORDER BY id
        """)
        projects = cur.fetchall()

        cur.execute("""
            SELECT pc.projects_id, p.id, p.uuid, p.display_name
            FROM projects_creators pc
            JOIN people p ON p.id = pc.people_id
        """)
        creators_by_project = {}
        for row in cur.fetchall():
            creators_by_project.setdefault(row['projects_id'], []).append(
                (row['id'], row['uuid'], row['display_name']))

        cur.execute("""
            SELECT po.projects_id, p.id, p.display_name
            FROM projects_owners po
            JOIN people p ON p.id = po.people_id
        """)
        owners_by_project = {}
        for row in cur.fetchall():
            owners_by_project.setdefault(row['projects_id'], []).append(
                (row['id'], row['display_name']))

    out = [
        '# Project Creator vs. Owner Report',
        '',
        'Generated: {0} (pre-flight, v1.9.0 schema)'.format(
            datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')),
        '',
        '| Project | Creator | Owners | Creator is Owner? |',
        '|---|---|---|---|',
    ]
    mismatch_count = 0
    for proj in projects:
        creators = creators_by_project.get(proj['id'], [])
        owners = owners_by_project.get(proj['id'], [])
        creator_entries = ['{0} ({1})'.format(name, uuid) for _, uuid, name in creators]
        owner_names = [name for _, name in owners]
        creator_ids = {cid for cid, _, _ in creators}
        owner_ids = {oid for oid, _ in owners}
        not_owners = creator_ids - owner_ids
        creators_md = ', '.join(creator_entries) if creator_entries else '*(none)*'
        owners_md = ', '.join(owner_names) if owner_names else '*(none)*'
        if not_owners:
            mismatch_count += 1
            out.append('| **{0} ({1})** | **{2}** | **{3}** | **No** |'.format(
                proj['name'], proj['uuid'], creators_md, owners_md))
        else:
            flag = 'Yes' if creator_ids else 'N/A'
            out.append('| {0} ({1}) | {2} | {3} | {4} |'.format(
                proj['name'], proj['uuid'], creators_md, owners_md, flag))

    out.append('')
    out.append('**{0}** project(s) where a creator is not an owner.'.format(mismatch_count))
    out.append('')

    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main()
