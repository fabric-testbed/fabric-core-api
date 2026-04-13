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

## Versioning

Both scripts carry version information to ensure backwards compatibility as the application and backup format evolve.

### Backup format version

Each backup archive includes a `VERSION.json` file with machine-readable metadata:

```json
{
    "backup_format_version": "1.1.0",
    "api_version": "1.9.0",
    "created": "2026-04-13T14:30:00Z",
    "hostname": "alpha-6.fabric-testbed.net",
    "git_branch": "develop",
    "git_commit": "ab35789...",
    "postgres_db": "postgres",
    "postgres_server": "database:5432"
}
```

The `backup_format_version` tracks the archive layout itself (directory structure, which files are present). The `api_version` tracks the fabric-core-api application version the data was exported from.

| Format Version | Date | Changes |
|---|---|---|
| `1.0.0` | 2026-04-12 | Initial format — `MANIFEST.txt` only, no `VERSION.json` |
| `1.1.0` | 2026-04-13 | Added `VERSION.json` with machine-readable version metadata |

When the archive layout changes (new directories, renamed files, changed dump format), increment the backup format version and update `RESTORE_SUPPORTED_FORMATS` in `full-restore.sh`.

### API version detection

The API version is read from `__API_VERSION__` in the source tree. Both scripts search these locations in order, stopping at the first match:

1. `server/swagger_server/__init__.py` (current location)
2. `server/swagger_server/version.py`
3. `server/version.py`
4. `version.py`

If `__API_VERSION__` moves to a new file in a future revision, add the new path to the `detect_api_version()` function in both scripts.

### Version checks during restore

When `full-restore.sh` runs, it:

1. **Reads `VERSION.json`** from the backup (falls back to parsing `MANIFEST.txt` for pre-1.1.0 backups)
2. **Validates the backup format version** against `RESTORE_SUPPORTED_FORMATS` — refuses to restore if the format is unrecognized
3. **Compares the backup API version** with the local codebase — warns if they differ and suggests running migrations:
   ```
   WARNING: API version mismatch: backup=1.8.0, local codebase=1.9.0
   WARNING: You may need to run database migrations or version update scripts after restore:
              python -m flask db upgrade
              python -m server.swagger_server.backup.utils.db_version_updates
   ```

This means a backup from API version 1.8.0 can be restored into a 1.9.0 codebase — the restore proceeds with a warning, and the operator runs migrations afterward.

## What Gets Backed Up

| Component | Directory in Archive | Description |
|---|---|---|
| Version metadata | `VERSION.json` | Machine-readable backup format version, API version, git commit, timestamps |
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
| Manifest | `MANIFEST.txt` | Human-readable summary with restore instructions |

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

## Walkthrough: Restore to a Fresh Clone (Docker)

This section documents a tested end-to-end restore from a backup archive (`full-backup-20260412-203800.tar.gz` captured from `alpha-6.fabric-testbed.net`) into a fresh `git clone` of the repository, deploying entirely in Docker at `127.0.0.1:8443`.

### Starting point

- A fresh `git clone` of `fabric-core-api` — no `.env`, no database, no prior state
- The backup `.tar.gz` placed in the repo root
- Docker Desktop running

### Step 1: Extract the backup and restore config files

```bash
cd /path/to/fabric-core-api
tar -xzf full-backup-20260412-203800.tar.gz
```

Copy config files from the extracted backup into place. The Dockerfile copies `.env` into the image at build time, so `.env` **must** exist and be correct before `docker compose build`:

```bash
cp full-backup-20260412-203800/config/dot-env .env
cp full-backup-20260412-203800/nginx/default.conf nginx/default.conf
cp full-backup-20260412-203800/vouch/config vouch/config
cp -a full-backup-20260412-203800/migrations/ migrations/
```

> **Note:** `full-restore.sh --skip-db` can do this for you interactively, but for a fresh clone with no existing files, manual copy is straightforward.

### Step 2: Generate self-signed SSL certificates

The backup contains SSL certificates issued for the source domain (e.g., `fabric-testbed.net`). These won't work for `127.0.0.1`. Generate a self-signed certificate:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/CN=127.0.0.1" \
  -addext "subjectAltName=IP:127.0.0.1"
```

### Step 3: Update configuration for the new host

All three config files contain host-specific values from the source VM. The table below shows every change needed when moving from a production domain to `127.0.0.1:8443`:

#### `.env`

| Variable | Source value | Local value |
|---|---|---|
| `CORE_API_SERVER_URL` | `https://alpha-6.fabric-testbed.net` | `https://127.0.0.1:8443` |
| `NGINX_ACCESS_CONTROL_ALLOW_ORIGIN` | `https://alpha-4.fabric-testbed.net` | `https://127.0.0.1:8443` |
| `FABRIC_CORE_API` | `https://alpha-6.fabric-testbed.net` | `https://127.0.0.1:8443` |

Leave `POSTGRES_SERVER=database` as-is for Docker deployment (this is the compose service name).

#### `nginx/default.conf`

| Setting | Source value | Local value |
|---|---|---|
| `ssl_certificate` | `/etc/ssl/alphabeta_fabric-testbed_net.pem` | `/etc/ssl/fullchain.pem` |
| `ssl_certificate_key` | `/etc/ssl/fabric-alpha-beta.key` | `/etc/ssl/privkey.pem` |
| HTTP->HTTPS redirect | `return 301 https://$host$request_uri` | `return 301 https://$host:8443$request_uri` |
| CORS `Access-Control-Allow-Origin` | `https://alpha-4.fabric-testbed.net` | `https://127.0.0.1:8443` |

The `proxy_pass http://flask-server:6000/` line should remain as-is for Docker deployment.

#### `vouch/config`

| Setting | Source value | Local value |
|---|---|---|
| `vouch.post_logout_redirect_uris` | `https://alpha-6.fabric-testbed.net/ui/#` | `https://127.0.0.1:8443/ui/#` |
| `vouch.cookie.domain` | `fabric-testbed.net` | `127.0.0.1` |
| `oauth.callback_url` | `https://alpha-6.fabric-testbed.net/auth` | `https://127.0.0.1:8443/auth` |

### Step 4: Start the database and restore data

```bash
source .env
docker compose up -d database

# Wait for PostgreSQL to accept connections
sleep 5
docker exec api-database pg_isready -U postgres
```

Restore the database using the dump file inside the extracted backup:

```bash
docker exec -i -e PGPASSWORD="${POSTGRES_PASSWORD}" api-database \
  pg_restore -U postgres -d postgres --clean --if-exists --no-owner --no-privileges \
  < full-backup-20260412-203800/database/postgres-20260412-203800.dump
```

Verify the restore:

```bash
docker exec -e PGPASSWORD="${POSTGRES_PASSWORD}" api-database \
  psql -U postgres -d postgres -c "\dt"
```

Expected: all 34 tables listed.

### Step 5: Start all services

```bash
docker compose up -d nginx vouch-proxy
docker compose build flask-server   # builds image with .env baked in
docker compose up -d flask-server
```

The Flask container takes 1-2 minutes on first start — it creates a virtualenv, installs `requirements.txt`, and launches uWSGI (8 workers x 8 threads). Monitor progress with:

```bash
docker logs -f api-flask-server
```

Wait until you see:

```
WSGI app 0 (mountpoint='') ready in N seconds on interpreter ... (default app)
spawned uWSGI worker 1 ...
```

### Step 6: Verify

```bash
# All containers healthy
docker ps --filter "name=api-"

# Swagger UI
curl -sk https://127.0.0.1:8443/ui/ | head -5

# API version
curl -sk https://127.0.0.1:8443/version

# Public endpoint (no auth required)
curl -sk 'https://127.0.0.1:8443/projects?search=test' | python3 -m json.tool | head -20

# Auth-protected endpoint (should return 401)
curl -sk 'https://127.0.0.1:8443/people?search=fabric'
```

Expected results:
- `/ui/` — returns Swagger UI HTML (HTTP 200)
- `/version` — returns `{"version": "1.9.0"}` with correct API reference
- `/projects` — returns project data with pagination links rewritten to `127.0.0.1:8443`
- `/people` — returns HTTP 401 ("Login or Valid Token required"), confirming Vouch-Proxy auth gate works

### Known limitations of a local deployment

| Area | Limitation | Workaround |
|---|---|---|
| **OIDC login** | CILogon callback URL is registered to the source domain — login redirects back to the source, not `127.0.0.1` | Register a new CILogon OIDC client with `https://127.0.0.1:8443/auth` as the callback URL, and update `vouch/config` with the new `client_id` |
| **COmanage API** | Credentials in `.env` point to the source tier's COmanage registry; sync operations will hit the real registry | Acceptable for read-only testing; for isolation, disable COmanage-dependent features or point to a test registry |
| **SMTP** | Email settings point to the source mail server | Change `SMTP_SERVER` in `.env` to a local mail sink (e.g., [MailHog](https://github.com/mailhog/MailHog)) or disable email features |
| **Self-signed cert** | Browsers show security warnings; API clients need `-k` / `verify=False` | Expected for local development; use a real cert or add the self-signed cert to your trust store |
| **First startup time** | Flask container installs dependencies on every fresh start (~1-2 minutes) | Normal — the virtualenv is created inside the container at runtime per `docker-entrypoint.sh` |

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
