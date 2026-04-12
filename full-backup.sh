#!/usr/bin/env bash
#
# full-backup.sh — Create a complete, portable backup of the fabric-core-api
# application for VM-to-VM migration.
#
# This script captures everything needed to stand up the application on a new
# machine: database dump, table-level JSON exports, configuration files,
# SSL certificates, environment variables, and service configs.
#
# Usage:
#   ./full-backup.sh [BACKUP_DIR]
#
#   BACKUP_DIR  Optional destination directory (default: ./full-backup-<timestamp>)
#
# Prerequisites:
#   - PostgreSQL client tools (pg_dump) accessible
#   - .env sourced or POSTGRES_* variables set in the environment
#   - Run from the fabric-core-api repository root
#
# Output: A tar.gz archive ready for transfer to another VM.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="${1:-${SCRIPT_DIR}/full-backup-${TIMESTAMP}}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { echo "[backup] $(date '+%Y-%m-%d %H:%M:%S') $*"; }
warn() { echo "[backup] WARNING: $*" >&2; }

require_var() {
    local var_name="$1"
    if [[ -z "${!var_name:-}" ]]; then
        echo "ERROR: Required environment variable ${var_name} is not set." >&2
        echo "       Source your .env file first:  source .env" >&2
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Validate environment
# ---------------------------------------------------------------------------

for var in POSTGRES_SERVER POSTGRES_PORT POSTGRES_USER POSTGRES_DB; do
    require_var "$var"
done

# ---------------------------------------------------------------------------
# Detect Docker vs local database
# ---------------------------------------------------------------------------

DB_CONTAINER="${DB_CONTAINER:-api-database}"
USE_DOCKER_DB=false

if [[ "${POSTGRES_SERVER}" == "database" ]] || [[ "${POSTGRES_SERVER}" == "${DB_CONTAINER}" ]]; then
    # Docker-compose service name — database is only reachable from within Docker
    if docker inspect "${DB_CONTAINER}" &>/dev/null 2>&1; then
        USE_DOCKER_DB=true
        log "Detected Docker database (container: ${DB_CONTAINER})"
    else
        echo "ERROR: POSTGRES_SERVER=${POSTGRES_SERVER} looks like a Docker service name," >&2
        echo "       but container '${DB_CONTAINER}' is not running." >&2
        echo "       Start it with: docker-compose up -d database" >&2
        exit 1
    fi
else
    # Host-accessible database — need pg_dump on the host
    if ! command -v pg_dump &>/dev/null; then
        # Fall back to Docker if the container is running
        if docker inspect "${DB_CONTAINER}" &>/dev/null 2>&1; then
            USE_DOCKER_DB=true
            log "pg_dump not found on host; falling back to Docker container '${DB_CONTAINER}'"
        else
            echo "ERROR: pg_dump not found and database container '${DB_CONTAINER}' is not running." >&2
            echo "       Install PostgreSQL client tools or start the Docker stack." >&2
            exit 1
        fi
    fi
fi

# ---------------------------------------------------------------------------
# Create backup directory structure
# ---------------------------------------------------------------------------

log "Creating backup at: ${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"/{database,config,ssl,vouch,nginx,migrations,logs,json-export}

# ---------------------------------------------------------------------------
# 1. PostgreSQL full dump (schema + data, custom format for pg_restore)
# ---------------------------------------------------------------------------

if [[ "${USE_DOCKER_DB}" == "true" ]]; then
    log "Dumping PostgreSQL database via Docker container '${DB_CONTAINER}'..."

    # Custom format dump — pg_restore compatible
    docker exec -e PGPASSWORD="${POSTGRES_PASSWORD:-}" "${DB_CONTAINER}" \
        pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -Fc \
        > "${BACKUP_DIR}/database/${POSTGRES_DB}-${TIMESTAMP}.dump"

    # Plain SQL dump — human-readable, portable
    docker exec -e PGPASSWORD="${POSTGRES_PASSWORD:-}" "${DB_CONTAINER}" \
        pg_dump -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" --clean --if-exists \
        > "${BACKUP_DIR}/database/${POSTGRES_DB}-${TIMESTAMP}.sql"
else
    log "Dumping PostgreSQL database (pg_dump)..."

    PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
        -h "${POSTGRES_SERVER}" \
        -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        -Fc \
        -f "${BACKUP_DIR}/database/${POSTGRES_DB}-${TIMESTAMP}.dump"

    log "Dumping PostgreSQL database (plain SQL for portability)..."
    PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_dump \
        -h "${POSTGRES_SERVER}" \
        -p "${POSTGRES_PORT}" \
        -U "${POSTGRES_USER}" \
        -d "${POSTGRES_DB}" \
        --clean --if-exists \
        -f "${BACKUP_DIR}/database/${POSTGRES_DB}-${TIMESTAMP}.sql"
fi

# ---------------------------------------------------------------------------
# 2. JSON table exports (existing db_export.py output)
# ---------------------------------------------------------------------------

FLASK_CONTAINER="${FLASK_CONTAINER:-api-flask-server}"
JSON_DATA_DIR="${SCRIPT_DIR}/server/swagger_server/backup/data"

if [[ -d "${JSON_DATA_DIR}" ]] && ls "${JSON_DATA_DIR}"/*.json &>/dev/null 2>&1; then
    log "Copying JSON table exports from host..."
    cp "${JSON_DATA_DIR}"/*.json "${BACKUP_DIR}/json-export/"
elif docker inspect "${FLASK_CONTAINER}" &>/dev/null 2>&1; then
    # Try to copy JSON exports from the Flask container
    CONTAINER_DATA_DIR="/code/server/swagger_server/backup/data"
    if docker exec "${FLASK_CONTAINER}" test -d "${CONTAINER_DATA_DIR}" 2>/dev/null; then
        log "Copying JSON table exports from container '${FLASK_CONTAINER}'..."
        docker cp "${FLASK_CONTAINER}:${CONTAINER_DATA_DIR}/." "${BACKUP_DIR}/json-export/" 2>/dev/null || true
    fi
    if ! ls "${BACKUP_DIR}/json-export/"*.json &>/dev/null 2>&1; then
        warn "No JSON exports found in container. Run inside the container first:"
        warn "  docker exec -ti ${FLASK_CONTAINER} bash -c 'source .env && source .venv/bin/activate && python -m server.swagger_server.backup.utils.db_export'"
    fi
else
    warn "No JSON exports found in ${JSON_DATA_DIR}."
    warn "Run 'python -m server.swagger_server.backup.utils.db_export' first for table-level JSON backups."
fi

# ---------------------------------------------------------------------------
# 3. Environment file (.env)
# ---------------------------------------------------------------------------

if [[ -f "${SCRIPT_DIR}/.env" ]]; then
    log "Backing up .env..."
    cp "${SCRIPT_DIR}/.env" "${BACKUP_DIR}/config/dot-env"
else
    warn ".env file not found — secrets will need to be recreated manually."
fi

# Also capture the template for reference
if [[ -f "${SCRIPT_DIR}/env.template" ]]; then
    cp "${SCRIPT_DIR}/env.template" "${BACKUP_DIR}/config/env.template"
fi

# ---------------------------------------------------------------------------
# 4. SSL certificates
# ---------------------------------------------------------------------------

if [[ -d "${SCRIPT_DIR}/ssl" ]]; then
    log "Backing up SSL certificates..."
    cp -a "${SCRIPT_DIR}/ssl/." "${BACKUP_DIR}/ssl/"
else
    warn "ssl/ directory not found."
fi

# ---------------------------------------------------------------------------
# 5. Vouch-Proxy configuration
# ---------------------------------------------------------------------------

if [[ -d "${SCRIPT_DIR}/vouch" ]]; then
    log "Backing up Vouch-Proxy configuration..."
    cp -a "${SCRIPT_DIR}/vouch/." "${BACKUP_DIR}/vouch/"
else
    warn "vouch/ directory not found."
fi

# ---------------------------------------------------------------------------
# 6. Nginx configuration
# ---------------------------------------------------------------------------

if [[ -d "${SCRIPT_DIR}/nginx" ]]; then
    log "Backing up Nginx configuration..."
    cp -a "${SCRIPT_DIR}/nginx/." "${BACKUP_DIR}/nginx/"
else
    warn "nginx/ directory not found."
fi

# ---------------------------------------------------------------------------
# 7. Docker Compose files
# ---------------------------------------------------------------------------

log "Backing up Docker Compose files..."
for f in docker-compose.yaml docker-compose.yaml.docker docker-compose.yaml.local; do
    if [[ -f "${SCRIPT_DIR}/${f}" ]]; then
        cp "${SCRIPT_DIR}/${f}" "${BACKUP_DIR}/config/"
    fi
done

# ---------------------------------------------------------------------------
# 8. Alembic migrations
# ---------------------------------------------------------------------------

if [[ -d "${SCRIPT_DIR}/migrations" ]]; then
    log "Backing up Alembic migrations..."
    cp -a "${SCRIPT_DIR}/migrations/." "${BACKUP_DIR}/migrations/"
else
    warn "migrations/ directory not found."
fi

# ---------------------------------------------------------------------------
# 9. Application logs (optional, can be large)
# ---------------------------------------------------------------------------

if [[ -d "${SCRIPT_DIR}/logs" ]]; then
    log "Backing up application logs..."
    cp -a "${SCRIPT_DIR}/logs/." "${BACKUP_DIR}/logs/"
else
    log "No logs/ directory found (skipping)."
fi

# ---------------------------------------------------------------------------
# 10. uWSGI config
# ---------------------------------------------------------------------------

if [[ -f "${SCRIPT_DIR}/server/core-api.ini" ]]; then
    log "Backing up uWSGI config..."
    cp "${SCRIPT_DIR}/server/core-api.ini" "${BACKUP_DIR}/config/"
fi

# ---------------------------------------------------------------------------
# 11. Capture metadata
# ---------------------------------------------------------------------------

log "Writing backup manifest..."
cat > "${BACKUP_DIR}/MANIFEST.txt" <<MANIFEST
fabric-core-api Full Backup
============================
Created:    $(date -u '+%Y-%m-%d %H:%M:%S UTC')
Hostname:   $(hostname)
Git branch: $(git -C "${SCRIPT_DIR}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Git commit: $(git -C "${SCRIPT_DIR}" rev-parse HEAD 2>/dev/null || echo "unknown")
API version: $(grep -oP "__API_VERSION__\s*=\s*'[^']+'" "${SCRIPT_DIR}/server/swagger_server/__init__.py" 2>/dev/null || echo "unknown")
DB server:  ${POSTGRES_SERVER}:${POSTGRES_PORT}
DB name:    ${POSTGRES_DB}

Contents
--------
database/       PostgreSQL dump (custom + plain SQL formats)
json-export/    Per-table JSON exports from db_export.py
config/         .env, env.template, docker-compose files, uWSGI config
ssl/            TLS certificates and private key
vouch/          Vouch-Proxy OIDC configuration
nginx/          Nginx reverse proxy configuration
migrations/     Alembic database migration scripts
logs/           Application and metrics logs

Restore Instructions
--------------------
See full-restore.sh in the repository root, or follow these steps:

1. Clone the fabric-core-api repository on the target VM.
2. Extract this archive into the repo root.
3. Restore configuration:
     cp config/dot-env .env
     cp -a ssl/ ./ssl/
     cp -a vouch/ ./vouch/
     cp -a nginx/ ./nginx/
     cp -a migrations/ ./migrations/
4. Edit .env — update POSTGRES_SERVER, CORE_API_SERVER_URL,
   NGINX_ACCESS_CONTROL_ALLOW_ORIGIN, and any host-specific values.
5. Start database:
     docker-compose up -d database
6. Restore database (option A — pg_restore):
     pg_restore -h <host> -U postgres -d postgres --clean --if-exists \\
       database/${POSTGRES_DB}-${TIMESTAMP}.dump
   Or (option B — plain SQL):
     psql -h <host> -U postgres -d postgres \\
       -f database/${POSTGRES_DB}-${TIMESTAMP}.sql
7. Start remaining services:
     docker-compose up -d
8. Verify:
     curl -k https://localhost:8443/ui/
MANIFEST

# ---------------------------------------------------------------------------
# 12. Create tar.gz archive
# ---------------------------------------------------------------------------

ARCHIVE="${BACKUP_DIR}.tar.gz"
log "Creating archive: ${ARCHIVE}"
tar -czf "${ARCHIVE}" -C "$(dirname "${BACKUP_DIR}")" "$(basename "${BACKUP_DIR}")"

# Report sizes
log "Backup complete!"
log ""
log "Archive: ${ARCHIVE}"
log "Size:    $(du -h "${ARCHIVE}" | cut -f1)"
log ""
log "Directory contents:"
du -sh "${BACKUP_DIR}"/*/ "${BACKUP_DIR}"/*.txt 2>/dev/null | sed 's/^/  /'
log ""
log "Transfer this archive to the target VM and use full-restore.sh to restore."
