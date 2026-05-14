# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FABRIC Core API — a Python Flask REST API providing User Information Service (UIS) and Project Registry (PR) for the FABRIC testbed. Built with Connexion (OpenAPI 3.0.0) on top of Flask, backed by PostgreSQL 14. Current API version: `1.10.0` (defined in `server/swagger_server/__init__.py`).

> **Postgres version note:** Deployments are currently pinned to `postgres:14` to match the on-disk format in existing `pg_data/` volumes. A PG14 → PG17 upgrade (via `pg_upgrade` or dump-and-reload) will be handled as a separate maintenance window, independent of the v1.9.0 → v1.10.0 API migration.

## Development Setup

Dependencies are managed by [uv](https://docs.astral.sh/uv/). The project manifest is `pyproject.toml`; the lockfile (`uv.lock`) and `.python-version` (3.12) are committed.

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies into ./.venv (creates the venv, installs the pinned Python 3.12)
uv sync --group dev

# Load environment variables (copy env.template to .env first)
source .env

# Start database (only need PostgreSQL container)
docker compose up -d database

# Initialize/migrate database
uv run python -m flask db init
uv run python -m flask db migrate
uv run python -m flask db upgrade

# Populate initial data from COmanage
uv run python -m server.swagger_server.database.db_load

# Run the server (port 6000)
uv run python -m server.swagger_server
```

Note: `PYTHONPATH` must include `./server` (set in `env.template`).

There is no `requirements.txt`, `setup.py`, or `tox.ini` — all package management goes through `pyproject.toml` + `uv`.

## Running Tests

```bash
# All tests
uv run nosetests

# Single test file
uv run nosetests server/swagger_server/test/test_people_controller.py
```

Test framework: nose (with flask_testing). Tests live in `server/swagger_server/test/`. Test deps are declared in the `[dependency-groups] dev` section of `pyproject.toml`.

## Docker Services

`docker-compose.yml` (rendered from `docker-compose.yml.template`) orchestrates:
- **database**: PostgreSQL 14 on port 5432 (PG17 upgrade pending — separate maintenance window)
- **nginx**: Reverse proxy with SSL on ports 8080/8443
- **vouch-proxy**: OAuth/OIDC authentication proxy on port 9090
- **flask-server**: uWSGI app (8 processes × 8 threads) on port 6000 (config: `server/core-api.ini`)

For local development, typically only `database` runs in Docker; Flask runs directly via `uv run`.

The Dockerfile uses `uv sync --frozen --no-install-project --no-dev` at build time, so the venv (`/code/.venv`) is baked into the image — no runtime pip install. Compiling uWSGI from sdist requires `build-essential`, `libpcre2-dev`, and `libpq-dev` (already in the Dockerfile).

## Architecture

### Request Flow

```
Client → Nginx (SSL/CORS) → Vouch-Proxy (auth) → Flask/Connexion (port 6000)
```

Connexion routes requests based on `operationId` in the OpenAPI spec (`server/swagger_server/swagger/swagger.yaml`) to controllers.

### Code Organization (`server/swagger_server/`)

- **`swagger/swagger.yaml`** — OpenAPI 3.0.0 spec (single large file, ~160KB). Connexion uses this to route requests and validate input/output.
- **`controllers/`** — Thin routing layer (~14 files). Each controller function delegates to the corresponding `response_code/` module.
- **`response_code/`** — Business logic (~33 files). This is where the real work happens. Key files: `people_utils.py`, `projects_utils.py`, `comanage_utils.py`, `decorators.py`.
- **`models/`** — Auto-generated from Swagger spec (110+ files). Do not hand-edit.
- **`database/models/`** — SQLAlchemy ORM models (~13 files). Key: `people.py`, `projects.py`, `announcements.py`, `profiles.py`, `storage.py`, `sshkeys.py`.
- **`database/models/mixins.py`** — BaseMixin (id), TimestampMixin (created/modified), TrackingMixin (created_by_uuid/modified_by_uuid). Models compose these via multiple inheritance.
- **`backup/utils/`** — Database backup, restore, and version update scripts.
- **`response_code/json_data/`** — Static JSON files for dropdown options (communities, funding agencies, tags, etc.), loaded by `CoreApiOptions` in `response_code/__init__.py`.

### Adding a New Endpoint

Full flow: `swagger.yaml` → `controllers/` → `response_code/` → `database/models/`

1. Define path, operationId, parameters, and schemas in `swagger/swagger.yaml`
2. The `operationId` (e.g., `announcements_get`) maps directly to a function name in `controllers/announcements_controller.py`
3. Controller functions are thin — they import and delegate: `from swagger_server.response_code import announcements_controller as rc` then call `rc.announcements_get(...)`
4. Write business logic in the corresponding `response_code/` module with auth decorators
5. Use `cors_response.py` helpers (`cors_200()`, `cors_400()`, etc.) to wrap responses

The script `helper_scripts/update-server-stub.sh` automates stub regeneration: archives `server/` to `server_archive/`, copies fresh codegen from `python-flask-server-generated/`, and restores custom directories (`response_code/`, `database/`, `backup/`).

### Authentication

Three auth mechanisms, implemented as decorators in `response_code/decorators.py`:
- `@login_required` — Vouch cookie (browser sessions)
- `@login_or_token_required` — Cookie OR JWT from FABRIC Credential Manager (includes token revocation list checking)
- `@secret_required` — SSH key secret validation (for bastion host endpoints)

Authorization uses COmanage COU (Collaborative Organization Unit) roles synced via `fabric_comanage_api`.

### Database

PostgreSQL with Flask-SQLAlchemy + Flask-Migrate (Alembic). Migrations in `/migrations/`.

Key database operations:
- **Sync from COmanage**: `server/swagger_server/database/db_load.py` — imports people, projects, roles from COmanage registry
- **Backup/Restore**: `server/swagger_server/backup/utils/db_export.py` and `db_restore.py` — JSON-based per-table backup (34 tables)
- **Version updates**: `server/swagger_server/backup/utils/db_version_updates.py` — backfill scripts for schema changes between API versions (run after migrations)
- **Per-version scripts**: `server/versions/<from>_to_<to>/` — one-off migration helpers (e.g. `purge_pc_cous.py`, `purge_project_leads.py` for the v1.9 → v1.10 transition)

### v1.10.0 schema/role changes worth knowing about

- Project creators are no longer represented by a COmanage COU. The legacy `<uuid>-pc` COUs are being purged; creator membership lives only in the `projects_creators` junction table. `is_project_creator()` checks the junction table, not COU roles.
- The `project-leads` facility-wide COU is being deprecated and purged via `server/versions/v1_9_0_to_v1_10_0/purge_project_leads.py`. The role-equivalent for project creation is now `project-admins` (`COU_ID_PROJECT_ADMINS` in `.env`).
- Storage `expires_on` is constrained to be ≤ the parent project's `expires_on` (enforced in `storage_controller.py` and backfilled by `storage_align_expires_on_with_project()` in `db_version_updates.py`).
- `created_by_uuid` is backfilled for legacy projects from `projects_creators` first, then `project_lead`.

### Background Tasks

`TaskTimeoutTracker` table manages periodic background tasks. A monitor thread (`response_code/task_monitor.py`) checks SSH key expiry and sends notification emails. Triggered via the `/start` endpoint with configurable cooldown intervals (PSK: 86400s, TRL: 300s).

### Logging

Two-tier logging configured in `server/swagger_server/logging.ini`:
- **consoleLogger** — DEBUG level to stdout (general application logs)
- **metricsLogger** — INFO level to rotating file (`./logs/metrics/core-api-metrics.log`) for auditable events (user create/modify/delete with UUIDs)

### Key Environment Variables

All variables documented in `env.template`. Critical groups:
- `POSTGRES_*` — Database connection
- `COMANAGE_API_*` — COmanage registry integration
- `COU_ID_*` / `COU_NAME_*` — COmanage COU role mappings (facility-operators, project-admins, active-users, etc.)
- `VOUCH_*` — Authentication proxy config
- `SSH_KEY_*` — SSH key management (algorithm, validity days, garbage collection)
- `PSK_*` / `TRL_*` — Task timeout intervals for public signing key and token revocation list caching
- `FABRIC_CORE_API`, `FABRIC_CREDENTIAL_MANAGER` — Service URLs
- `CORE_API_DEPLOYMENT_TIER` — Environment tier (alpha/beta/production), affects which tag sets are loaded

### Entry Point

`server/swagger_server/__main__.py` — Creates Connexion app with `pythonic_params=True`, configures Flask + SQLAlchemy, registers error handlers for Connexion exceptions, and starts the background task monitor thread.

API version is defined in `server/swagger_server/__init__.py` (`__API_VERSION__`).
