# v1.9.0 → v1.10.0 Migration Guide

This directory contains the helper scripts and manifests required to migrate a deployed FABRIC Core API instance from API version **1.9.0** to **1.10.0**.

The migration covers four classes of change:

1. **Project creator decoupling** — the per-project `<uuid>-pc` COU is removed from COmanage; creators are tracked only in the local `projects_creators` junction table.
2. **`project-leads` role deprecation** — the facility-wide `project-leads` COU is purged; the role-equivalent for project creation is now `project-admins`.
3. **Storage expiry alignment** — every storage allocation's `expires_on` is brought into line with its parent project's `expires_on`.
4. **`created_by_uuid` backfill** — projects missing `created_by_uuid` are populated from the `projects_creators` junction table (preferred) or `project_lead` (fallback).

The migration is performed in five phases. Phases 1–3 modify the local database; Phases 4–5 touch the remote COmanage registry and the operator's `.env`. Take a full backup before starting.

---

## Files in this directory

| File | Type | Purpose |
|---|---|---|
| `README.md` | docs | This guide |
| `db_version_updates_v1.10.0.py` | script (legacy) | Carried over from the previous directory layout; superseded by the canonical `server/swagger_server/backup/utils/db_version_updates.py` (which contains the full set of v1.10.0 backfill functions). Kept here for historical reference; **do not use for the migration** |
| `purge_pc_cous.py` | script | Removes per-project `-pc` COUs from COmanage after they've been NULLed locally |
| `purge_project_leads.py` | script | Removes `project-leads` role memberships and (optionally) the COU itself |

The canonical backfill driver lives at:

```
server/swagger_server/backup/utils/db_version_updates.py
```

It runs all five backfill functions in sequence (export → NULL → backfill `created_by_uuid` → export creator/owner report → align storage expiry).

The two purge manifests it produces, plus the project-leads manifest pre-populated from `people_roles.json`, live in:

```
server/swagger_server/backup/data/comanage_pc_cous_to_purge.json
server/swagger_server/backup/data/comanage_project_leads_to_purge.json
server/swagger_server/backup/data/project_creator_owners.md
```

---

## Phase 0 — Pre-flight (REQUIRED)

Take a full backup. Both database and config are touched; rollback requires a known-good archive.

```bash
source .env
./full-backup.sh
# Move/copy the resulting full-backup-*.tar.gz off-host
```

Snapshot the current state of the relevant COUs in case manual rollback is needed:

```bash
# From a clean shell:
source .env

# Save the project-leads COU members as JSON (will be reused by purge_project_leads.py)
# This file is already committed at server/swagger_server/backup/data/comanage_project_leads_to_purge.json

# (Optional) Save the full COU listing as a sanity-check snapshot
uv run python -c "
import os, json
from comanage_api import ComanageApi
api = ComanageApi(
    co_api_url=os.getenv('COMANAGE_API_URL'),
    co_api_user=os.getenv('COMANAGE_API_USER'),
    co_api_pass=os.getenv('COMANAGE_API_PASS'),
    co_api_org_id=os.getenv('COMANAGE_API_CO_ID'),
    co_api_org_name=os.getenv('COMANAGE_API_CO_NAME'),
)
print(json.dumps(api.cous_view_per_co(), indent=2))
" > /tmp/cous-pre-migration.json
```

Confirm:

- A recoverable backup archive exists.
- COmanage credentials in `.env` point at the right registry (alpha vs beta vs prod).
- No background jobs are writing to the database (stop the Flask container or pause cron jobs).

---

## Phase 1 — Pull v1.10.0 code & dependencies

```bash
# Code
git fetch origin
git checkout v1.10.0   # or the appropriate branch/tag

# Dependencies (uv replaces pip/virtualenv in v1.10.0)
uv sync --group dev

# Verify
uv run python -c "from swagger_server import __API_VERSION__; print(__API_VERSION__)"
# → 1.10.0
```

If the deployment was using `pip install -r requirements.txt` (v1.9.0 style), there is **no migration step needed for the dep manager itself** — the new `pyproject.toml` + `uv.lock` replace the old `requirements.txt` and the previous virtualenv can be removed (`rm -rf venv/`).

---

## Phase 2 — Apply Alembic migrations

```bash
source .env
uv run python -m flask db upgrade
```

The v1.9.0 → v1.10.0 transition does **not** introduce any new schema (no column adds, no table drops). Alembic should report "already up to date" if the v1.9.0 database was current. The migration's data changes happen in Phase 3, not here.

If `flask db upgrade` reports a version drift, stop and investigate before proceeding.

---

## Phase 3 — Run local data backfills (scripted)

The canonical driver runs all five backfill functions in order:

```bash
source .env
uv run python -m server.swagger_server.backup.utils.db_version_updates
```

What it does (in order):

1. **`projects_export_co_cou_id_pc()`** — writes `comanage_pc_cous_to_purge.json` (one entry per project that still has a `-pc` COU). This manifest drives Phase 4a.
2. **`projects_null_co_cou_id_pc()`** — sets `co_cou_id_pc = NULL` on every project. The remote COUs still exist after this step; Phase 4 cleans them up.
3. **`projects_backfill_created_by_uuid()`** — populates `created_by_uuid` for projects missing it. Source preference: `projects_creators[0]` → `project_lead`.
4. **`projects_export_creator_owners_report()`** — writes `project_creator_owners.md` listing every project alongside its creators and owners, with rows bolded where the creator is not also an owner. **This is the input to Phase 5 manual review.**
5. **`storage_align_expires_on_with_project()`** — sets each storage allocation's `expires_on` to its parent project's `expires_on` whenever they differ.

After this phase, verify:

```bash
# No project should still have a co_cou_id_pc set
docker exec api-database psql -U postgres -d postgres -c \
  "SELECT id, uuid, name FROM projects WHERE co_cou_id_pc IS NOT NULL;"
# → expected: 0 rows

# No project should be missing created_by_uuid
docker exec api-database psql -U postgres -d postgres -c \
  "SELECT id, uuid, name FROM projects WHERE created_by_uuid IS NULL;"
# → expected: 0 rows (manual triage required if any are still NULL)

# No storage allocation should outlive its parent project
docker exec api-database psql -U postgres -d postgres -c \
  "SELECT s.id, s.uuid, s.expires_on, p.expires_on AS project_expires
   FROM storage s JOIN projects p ON p.id = s.project_id
   WHERE s.expires_on > p.expires_on;"
# → expected: 0 rows
```

---

## Phase 4 — Purge orphaned COmanage COUs (scripted, with dry runs)

These two scripts only need network access to COmanage and the env vars in `.env`. They do **not** require the Flask app or database.

### 4a. Purge per-project `-pc` COUs

Driven by `comanage_pc_cous_to_purge.json` (produced in Phase 3, step 1).

```bash
# Always start with a dry run — prints what would be deleted, makes no changes
uv run python -m server.versions.v1_9_0_to_v1_10_0.purge_pc_cous --dry-run

# Eyeball the dry-run output. When satisfied, run for real:
uv run python -m server.versions.v1_9_0_to_v1_10_0.purge_pc_cous
```

For each entry in the manifest, the script:

1. Lists all `CoPersonRole` memberships in the COU
2. Deletes each role membership
3. Deletes the COU itself

A failure on any single COU stops processing that COU but continues with the next.

### 4b. Purge `project-leads` role + COU

Driven by `comanage_project_leads_to_purge.json` (committed; contains the full membership snapshot taken from `people_roles.json`).

```bash
# Dry run first
uv run python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads --dry-run

# Cautious mode — purge memberships only, leave the COU itself in place
uv run python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads --keep-cou

# Full purge (memberships AND the COU). Skips COU deletion if any membership delete failed.
uv run python -m server.versions.v1_9_0_to_v1_10_0.purge_project_leads
```

Unlike the per-project `-pc` COUs, `project-leads` is a single facility-wide COU. Operators may prefer to purge memberships only (`--keep-cou`) on the first pass, verify nothing else in COmanage references the COU, and delete it manually later.

---

## Phase 5 — Manual review

### 5a. Creator-vs-owner reconciliation

`server/swagger_server/backup/data/project_creator_owners.md` (produced in Phase 3) lists every project with its creators, owners, and a `Creator is Owner?` column. Rows where the answer is **No** are bolded.

Walk through each "No" row with the project lead / facility operator and decide:

- **Add the creator as an owner** — typical fix when the creator stepped out of ownership unintentionally.
- **Leave as-is** — common for test/dev projects on alpha where the creator was a facility operator acting on behalf of someone else.
- **Reassign creator** — if the original creator is no longer with the project, update `projects_creators` via `PATCH /projects/{uuid}/project-creators` (operation: `batch`).

Whichever you choose, update via the API rather than direct SQL so the metrics log captures the change.

### 5b. Spot-check `created_by_uuid` backfill

For any project that needed backfilling (output of Phase 3 step 3), confirm the chosen creator UUID is sensible — particularly the small number of projects backfilled from `project_lead` rather than `projects_creators`.

---

## Phase 6 — Configuration cleanup

Once the COmanage purge is complete, remove the now-unused environment variables.

### 6a. `.env`

Delete these lines from `.env` on every deployment host (already removed from `env.template`):

```
COU_ID_PROJECT_LEADS=...
COU_NAME_PROJECT_LEADS=project-leads
```

The application no longer reads them; leaving them in `.env` is harmless but misleading.

### 6b. CILogon / portal config (out of scope here)

If the portal or other relying parties were issuing the `project-leads` claim or using it for UI gating, coordinate with those teams to switch to `project-admins`. The portal must be updated **before** anyone relying on the `project-leads` claim loses it.

---

## Phase 7 — Deploy and verify

```bash
# Rebuild the Flask image (uWSGI compile takes a few minutes the first time)
docker compose build flask-server
docker compose up -d flask-server
docker compose logs -f flask-server   # watch for errors
```

Verification checklist:

- `curl -sk https://<host>/version` → `{"version": "1.10.0", ...}`
- `/check-cookie` for an authenticated user — `roles` array contains `project-admins` (where appropriate) and **no** `<uuid>-pc` or `project-leads` entries.
- `GET /projects/{uuid}` returns the project with `project_creators` populated from the local junction table (no COmanage round-trip).
- `PATCH /projects` smoke test — create-then-delete a throwaway project to exercise the new authz path (`project-admins` / `facility-operators`).
- `GET /core-api-metrics/overview` returns a 200 (sanity check that the metrics task still runs).

---

## Rollback

There is no automated rollback. If the migration fails:

1. Stop the Flask container.
2. Restore the database from the Phase 0 backup:
   ```bash
   ./full-restore.sh full-backup-<timestamp>.tar.gz --skip-config
   ```
3. Re-create any deleted COmanage COUs from `/tmp/cous-pre-migration.json` (Phase 0 snapshot) using the COmanage admin UI or `cous_add` API. Re-creation will assign new COU IDs, so the local `co_cou_id_pc` / project-leads bindings in the restored database will need a manual fix-up.
4. Restore the previous `.env` (the COU_ID_PROJECT_LEADS / COU_NAME_PROJECT_LEADS lines must come back).
5. Roll the deployment back to the v1.9.0 code (`git checkout v1.9.0`, `pip install -r requirements.txt` since v1.9.0 didn't use uv).

Because step 3 is destructive (new COU IDs ≠ old IDs), prefer to fix-forward rather than roll back wherever possible.

---

## Phase summary (TL;DR)

| Phase | Action | Type |
|---|---|---|
| 0 | `full-backup.sh` + COU snapshot | Manual |
| 1 | `git checkout v1.10.0` + `uv sync --group dev` | Manual |
| 2 | `uv run python -m flask db upgrade` | Scripted |
| 3 | `uv run python -m server.swagger_server.backup.utils.db_version_updates` | Scripted |
| 4a | `purge_pc_cous.py --dry-run` → live | Scripted (with manual gate) |
| 4b | `purge_project_leads.py --dry-run` → `--keep-cou` → live | Scripted (with manual gate) |
| 5 | Review `project_creator_owners.md`; fix mismatches via API | Manual |
| 6 | Remove `COU_*_PROJECT_LEADS` from `.env`; coordinate with portal team | Manual |
| 7 | `docker compose build && up`; smoke-test endpoints | Manual |
