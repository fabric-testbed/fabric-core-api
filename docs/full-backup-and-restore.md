# Full Backup and Restore Guide

Complete backup and restore procedures for migrating the fabric-core-api application between VMs.

For the existing Docker-container-focused database backup/restore workflow, see [backup-and-restore.md](backup-and-restore.md).

## Overview

Two scripts work together to capture and restore the full application state:

| Script | Purpose |
|---|---|
| `full-backup.sh` | Creates a portable `.tar.gz` archive of the entire application |
| `full-restore.sh` | Restores the archive on a target VM with interactive prompts |

These scripts complement the existing table-level JSON export/import tools in `server/swagger_server/backup/utils/` by adding everything else needed for a complete migration.

## What Gets Backed Up

| Component | Directory in Archive | Description |
|---|---|---|
| PostgreSQL dump | `database/` | Full `pg_dump` in both custom (`.dump`) and plain SQL (`.sql`) formats — includes schema, data, sequences, indexes, and constraints |
| JSON table exports | `json-export/` | Per-table JSON files from `db_export.py` (34 tables) — human-readable fallback |
| Environment variables | `config/dot-env` | Production `.env` with all secrets and configuration |
| Environment template | `config/env.template` | Reference template for documentation |
| Docker Compose | `config/docker-compose.*` | Service definitions for all deployment variants |
| uWSGI config | `config/core-api.ini` | Application server configuration |
| SSL certificates | `ssl/` | `fullchain.pem`, `privkey.pem`, `chain.pem` |
| Vouch-Proxy config | `vouch/` | OIDC client configuration for all tiers (alpha, beta, prod) |
| Nginx config | `nginx/` | Reverse proxy, TLS termination, and auth\_request rules |
| Alembic migrations | `migrations/` | Database migration history and version state |
| Application logs | `logs/` | Metrics and audit logs (optional, may be large) |
| Manifest | `MANIFEST.txt` | Timestamp, git commit, API version, and restore instructions |

## Prerequisites

Both scripts require:

- **Environment variables** — source `.env` before running, or have `POSTGRES_*` variables exported
- **Run from repo root** — scripts use their own location to find project files
- **PostgreSQL client tools OR Docker** — see next section

### Local vs Docker Database

The scripts auto-detect whether the database is running locally or inside Docker:

| Scenario | How it's detected | pg\_dump / pg\_restore runs via |
|---|---|---|
| Local database | `POSTGRES_SERVER` is an IP or resolvable hostname | Host `pg_dump` / `pg_restore` |
| Docker database | `POSTGRES_SERVER=database` (compose service name) | `docker exec` into `api-database` container |
| Host tools missing | `pg_dump` not found, but `api-database` container exists | Falls back to `docker exec` automatically |

When running entirely in Docker, you do **not** need `pg_dump` or `pg_restore` installed on the host — the scripts execute them inside the `api-database` container.

The container names default to `api-database` and `api-flask-server` (matching `docker-compose.yaml`). Override with environment variables if your container names differ:

```bash
DB_CONTAINER=my-db-container FLASK_CONTAINER=my-flask ./full-backup.sh
```

---

## Backup

### Usage

```bash
source .env
./full-backup.sh [BACKUP_DIR]
```

`BACKUP_DIR` is optional. Defaults to `./full-backup-<YYYYMMDD-HHMMSS>`.

### What It Does

1. Validates that `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_DB` are set
2. Detects whether the database is local or in Docker (auto-selects `docker exec` or host `pg_dump`)
3. Runs `pg_dump` twice — custom format (for `pg_restore`) and plain SQL (for portability)
4. Copies existing JSON table exports from host or from the Flask container if running in Docker
5. Copies `.env`, `env.template`, `docker-compose.yaml` variants, and `server/core-api.ini`
6. Copies `ssl/`, `vouch/`, `nginx/`, and `migrations/` directories
7. Copies `logs/` if present
8. Writes `MANIFEST.txt` with metadata (hostname, git commit, API version, timestamp)
9. Creates a `.tar.gz` archive and reports the final size

### Generating Fresh JSON Exports

The backup script copies whatever JSON files already exist in `server/swagger_server/backup/data/`. To ensure they are current, run the export first.

Local development:

```bash
source .env
python -m server.swagger_server.backup.utils.db_export
./full-backup.sh
```

Full Docker deployment:

```bash
source .env
docker exec -ti api-flask-server bash -c \
  'source .env && source .venv/bin/activate && python -m server.swagger_server.backup.utils.db_export'
./full-backup.sh
```

### Example Output

```
[backup] 2026-04-12 14:30:00 Creating backup at: ./full-backup-20260412-143000
[backup] 2026-04-12 14:30:00 Dumping PostgreSQL database (pg_dump)...
[backup] 2026-04-12 14:30:05 Dumping PostgreSQL database (plain SQL for portability)...
[backup] 2026-04-12 14:30:09 Copying JSON table exports...
[backup] 2026-04-12 14:30:09 Backing up .env...
[backup] 2026-04-12 14:30:09 Backing up SSL certificates...
[backup] 2026-04-12 14:30:09 Backing up Vouch-Proxy configuration...
[backup] 2026-04-12 14:30:09 Backing up Nginx configuration...
[backup] 2026-04-12 14:30:09 Backing up Docker Compose files...
[backup] 2026-04-12 14:30:09 Backing up Alembic migrations...
[backup] 2026-04-12 14:30:09 Backing up uWSGI config...
[backup] 2026-04-12 14:30:09 Writing backup manifest...
[backup] 2026-04-12 14:30:10 Creating archive: ./full-backup-20260412-143000.tar.gz
[backup] 2026-04-12 14:30:12 Backup complete!
[backup] 2026-04-12 14:30:12 Archive: ./full-backup-20260412-143000.tar.gz
[backup] 2026-04-12 14:30:12 Size:    48M
```

---

## Restore

### Usage

```bash
./full-restore.sh <BACKUP_DIR_OR_ARCHIVE> [OPTIONS]
```

Accepts either a `.tar.gz` archive (auto-extracts) or an already-extracted backup directory.

### Options

| Flag | Effect |
|---|---|
| `--skip-db` | Restore config files only, skip database restore |
| `--skip-config` | Restore database only, skip config files |
| `--dry-run` | Print what would be done without making changes |

### What It Does

**Configuration restore** (unless `--skip-config`):

1. Restores `.env` — if one already exists, prompts before overwriting and saves the current file as `.env.pre-restore`
2. Restores `ssl/`, `vouch/`, `nginx/` directories
3. Restores `docker-compose.yaml` variants and `server/core-api.ini`
4. Restores `migrations/` directory
5. Prompts before restoring `logs/` (can be large)
6. Restores JSON exports to `server/swagger_server/backup/data/`

**Database restore** (unless `--skip-db`):

1. Sources `.env` for PostgreSQL connection variables
2. Detects whether the database is local or in Docker (same auto-detection as backup)
3. Prefers the custom-format `.dump` file with `pg_restore --clean --if-exists --no-owner --no-privileges`
4. Falls back to plain SQL with `psql` if no `.dump` file is found
5. Pipes dump data into the container via `docker exec -i` when using Docker
6. Prompts for confirmation before executing (destructive operation)

**Post-restore checklist** — prints a reminder of host-specific values to update.

### Examples

Full restore from archive:

```bash
./full-restore.sh full-backup-20260412-143000.tar.gz
```

Preview what would happen:

```bash
./full-restore.sh full-backup-20260412-143000.tar.gz --dry-run
```

Config only (database is already set up separately):

```bash
./full-restore.sh full-backup-20260412-143000.tar.gz --skip-db
```

Database only (config was restored manually):

```bash
./full-restore.sh full-backup-20260412-143000.tar.gz --skip-config
```

---

## Complete Migration Workflow

### 1. On the source VM (local development)

```bash
cd /path/to/fabric-core-api
source .env

# Optional: generate fresh JSON table exports
python -m server.swagger_server.backup.utils.db_export

# Create the backup
./full-backup.sh
```

### 1. On the source VM (full Docker deployment)

```bash
cd /path/to/fabric-core-api
source .env

# Optional: generate fresh JSON table exports from the Flask container
docker exec -ti api-flask-server bash -c \
  'source .env && source .venv/bin/activate && python -m server.swagger_server.backup.utils.db_export'
# Copy exports to host so full-backup.sh can find them
docker cp api-flask-server:/code/server/swagger_server/backup/data/. \
  server/swagger_server/backup/data/

# Create the backup (auto-detects Docker database)
./full-backup.sh
```

### 2. Transfer

```bash
scp full-backup-20260412-*.tar.gz user@target-vm:/path/to/fabric-core-api/
```

### 3. On the target VM

```bash
cd /path/to/fabric-core-api

# Restore config files first (before starting Docker)
./full-restore.sh full-backup-20260412-143000.tar.gz --skip-db

# Update host-specific configuration (see next section)
vi .env
vi vouch/config
vi nginx/default.conf

# Replace SSL certs if domain changed
# cp /etc/letsencrypt/live/newdomain/fullchain.pem ssl/
# cp /etc/letsencrypt/live/newdomain/privkey.pem ssl/

# Start database first
source .env
docker-compose up -d database
sleep 5  # wait for PostgreSQL to initialize

# Now restore the database
./full-restore.sh full-backup-20260412-143000.tar.gz --skip-config

# Start remaining services
docker-compose up -d nginx vouch-proxy
# For local Flask:
python -m server.swagger_server
# Or for Docker Flask:
docker-compose up -d flask-server

# Verify
curl -k https://localhost:8443/ui/
```

---

## Host-Specific Values to Update After Restore

These values are tied to the source VM and almost always need updating on the target:

| File | Variable / Key | Why It Changes |
|---|---|---|
| `.env` | `CORE_API_SERVER_URL` | New hostname or IP |
| `.env` | `POSTGRES_SERVER` | `127.0.0.1` vs `database` (local vs Docker) |
| `.env` | `NGINX_ACCESS_CONTROL_ALLOW_ORIGIN` | Must match new URL |
| `.env` | `FABRIC_CORE_API` | Public-facing API URL |
| `.env` | `FABRIC_CREDENTIAL_MANAGER` | Credential manager URL |
| `.env` | `PYTHONPATH` | Local vs Docker path layout |
| `vouch/config` | `cookie.domain` | New domain for auth cookies |
| `vouch/config` | `post_logout_redirect_uris` | New portal URL |
| `vouch/config` | CILogon callback URL | Must be re-registered with CILogon |
| `nginx/default.conf` | `server_name`, upstream | New hostname, port mapping |
| `ssl/*` | Certificate files | New certs for new domain |

---

## Relationship to Existing Backup Tools

The existing scripts in `server/swagger_server/backup/utils/` remain useful for targeted operations:

| Script | Purpose | When to Use |
|---|---|---|
| `db_export.py` | Export all 34 tables to JSON | Routine data snapshots, human-readable backups |
| `db_restore.py` | Import JSON files back into database | Restoring individual tables, data repair |
| `db_version_updates.py` | Backfill data after schema changes | After running Alembic migrations between API versions |
| **`full-backup.sh`** | **Complete application archive** | **VM migration, disaster recovery, full environment cloning** |
| **`full-restore.sh`** | **Restore from full archive** | **Standing up on a new machine** |

The full backup includes the JSON exports as a secondary data format. The primary database restore uses `pg_dump`/`pg_restore` because it preserves schema-level details (sequences, indexes, constraints, enum types) that JSON table exports cannot capture.

---

## Database Restore Methods Compared

| Method | Tool | Preserves Schema | Preserves Sequences | Human-Readable | Selective Restore |
|---|---|---|---|---|---|
| Custom format dump | `pg_restore` | Yes | Yes | No | Yes (per-table) |
| Plain SQL dump | `psql` | Yes | Yes | Yes | Manual (edit SQL) |
| JSON table exports | `db_restore.py` | No (relies on ORM) | Resets manually | Yes | Yes (per-table) |

For a full VM migration, use `pg_restore` (the default in `full-restore.sh`). The JSON exports serve as a safety net and are useful for inspecting data or restoring individual tables.

---

## Troubleshooting

**`pg_restore` warnings about objects not existing**

Normal when restoring to a fresh database with `--clean --if-exists`. The script handles this gracefully.

**Permission errors on SSL private key**

Ensure `ssl/privkey.pem` has restricted permissions:

```bash
chmod 600 ssl/privkey.pem
```

**Database connection refused**

Ensure PostgreSQL is running and accepting connections before restoring:

```bash
docker-compose up -d database
sleep 5  # wait for startup
pg_isready -h 127.0.0.1 -p 5432
```

**Vouch-Proxy fails to start**

The CILogon callback URL is registered per-client. If the domain changed, update the callback URL in the CILogon OIDC client registration and in `vouch/config`.

**Sequence out of sync after JSON restore**

If using `db_restore.py` instead of `pg_restore`, sequences may not reflect the max ID. Fix with:

```sql
SELECT setval('people_id_seq', (SELECT MAX(id) FROM people));
-- Repeat for other tables as needed
```
