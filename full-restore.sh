#!/usr/bin/env bash
#
# full-restore.sh — Restore a fabric-core-api application from a full backup
# archive created by full-backup.sh.
#
# Usage:
#   ./full-restore.sh <BACKUP_DIR_OR_ARCHIVE> [--skip-db] [--skip-config] [--dry-run]
#
#   BACKUP_DIR_OR_ARCHIVE   Path to extracted backup directory or .tar.gz archive
#   --skip-db               Skip database restore (config files only)
#   --skip-config           Skip config file restore (database only)
#   --dry-run               Show what would be done without making changes
#
# Prerequisites:
#   - PostgreSQL client tools (pg_restore or psql)
#   - The fabric-core-api repository cloned on the target VM
#   - Run from the fabric-core-api repository root
#
# IMPORTANT: Review and edit .env after restore to update host-specific values
# (POSTGRES_SERVER, CORE_API_SERVER_URL, NGINX_ACCESS_CONTROL_ALLOW_ORIGIN, etc.)

set -euo pipefail

# ---------------------------------------------------------------------------
# Supported backup format versions — update when format changes
# ---------------------------------------------------------------------------
# This restore script can handle these backup format versions:
#   1.0.0  Initial format (no VERSION.json, MANIFEST.txt only)
#   1.1.0  Added VERSION.json with machine-readable version metadata
RESTORE_SUPPORTED_FORMATS=("1.0.0" "1.1.0")

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detect the API version from the local source tree. Same search order as
# full-backup.sh — the canonical location is server/swagger_server/__init__.py
# but may move in future revisions.
detect_api_version() {
    local version="unknown"
    local candidates=(
        "${SCRIPT_DIR}/server/swagger_server/__init__.py"
        "${SCRIPT_DIR}/server/swagger_server/version.py"
        "${SCRIPT_DIR}/server/version.py"
        "${SCRIPT_DIR}/version.py"
    )
    for f in "${candidates[@]}"; do
        if [[ -f "$f" ]]; then
            local match
            match=$(grep -oP "__API_VERSION__\s*=\s*['\"]([^'\"]+)['\"]" "$f" 2>/dev/null | head -1) || true
            if [[ -n "$match" ]]; then
                version=$(echo "$match" | grep -oP "['\"][^'\"]+['\"]" | tr -d "'\"")
                break
            fi
        fi
    done
    echo "$version"
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------

BACKUP_PATH=""
SKIP_DB=false
SKIP_CONFIG=false
DRY_RUN=false

for arg in "$@"; do
    case "$arg" in
        --skip-db)     SKIP_DB=true ;;
        --skip-config) SKIP_CONFIG=true ;;
        --dry-run)     DRY_RUN=true ;;
        -*)            echo "Unknown option: $arg" >&2; exit 1 ;;
        *)             BACKUP_PATH="$arg" ;;
    esac
done

if [[ -z "${BACKUP_PATH}" ]]; then
    echo "Usage: $0 <BACKUP_DIR_OR_ARCHIVE> [--skip-db] [--skip-config] [--dry-run]" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { echo "[restore] $(date '+%Y-%m-%d %H:%M:%S') $*"; }
warn() { echo "[restore] WARNING: $*" >&2; }

run() {
    if [[ "${DRY_RUN}" == "true" ]]; then
        echo "[dry-run] $*"
    else
        "$@"
    fi
}

confirm() {
    local msg="$1"
    if [[ "${DRY_RUN}" == "true" ]]; then
        return 0
    fi
    echo ""
    read -r -p "[restore] ${msg} [y/N] " response
    case "$response" in
        [yY][eE][sS]|[yY]) return 0 ;;
        *) return 1 ;;
    esac
}

# ---------------------------------------------------------------------------
# Extract archive if needed
# ---------------------------------------------------------------------------

if [[ -f "${BACKUP_PATH}" && "${BACKUP_PATH}" == *.tar.gz ]]; then
    log "Extracting archive: ${BACKUP_PATH}"
    EXTRACT_DIR="$(mktemp -d)"
    tar -xzf "${BACKUP_PATH}" -C "${EXTRACT_DIR}"
    # Find the extracted directory (should be the only item)
    BACKUP_DIR="$(find "${EXTRACT_DIR}" -mindepth 1 -maxdepth 1 -type d | head -1)"
    if [[ -z "${BACKUP_DIR}" ]]; then
        echo "ERROR: Could not find backup directory in archive." >&2
        exit 1
    fi
    log "Extracted to: ${BACKUP_DIR}"
elif [[ -d "${BACKUP_PATH}" ]]; then
    BACKUP_DIR="${BACKUP_PATH}"
else
    echo "ERROR: ${BACKUP_PATH} is not a valid directory or .tar.gz archive." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Validate backup contents and version compatibility
# ---------------------------------------------------------------------------

BACKUP_FORMAT_VERSION="unknown"
BACKUP_API_VERSION="unknown"

if [[ -f "${BACKUP_DIR}/VERSION.json" ]]; then
    # Parse VERSION.json (no jq dependency — use grep/sed)
    BACKUP_FORMAT_VERSION=$(grep -oP '"backup_format_version"\s*:\s*"[^"]+"' "${BACKUP_DIR}/VERSION.json" | grep -oP '"[^"]+"\s*$' | tr -d '"' || echo "unknown")
    BACKUP_API_VERSION=$(grep -oP '"api_version"\s*:\s*"[^"]+"' "${BACKUP_DIR}/VERSION.json" | grep -oP '"[^"]+"\s*$' | tr -d '"' || echo "unknown")
elif [[ -f "${BACKUP_DIR}/MANIFEST.txt" ]]; then
    # Pre-1.1.0 backup — no VERSION.json, infer from MANIFEST.txt
    BACKUP_FORMAT_VERSION="1.0.0"
    BACKUP_API_VERSION=$(grep -oP "API version:\s*.*?'([^']+)'" "${BACKUP_DIR}/MANIFEST.txt" | grep -oP "'[^']+'" | tr -d "'" || echo "unknown")
    if [[ "${BACKUP_API_VERSION}" == "unknown" ]]; then
        BACKUP_API_VERSION=$(grep -oP "API version:\s*(\S+)" "${BACKUP_DIR}/MANIFEST.txt" | awk '{print $NF}' || echo "unknown")
    fi
else
    warn "No VERSION.json or MANIFEST.txt found — this may not be a valid full-backup archive."
fi

# Check format version compatibility
FORMAT_SUPPORTED=false
for supported in "${RESTORE_SUPPORTED_FORMATS[@]}"; do
    if [[ "${BACKUP_FORMAT_VERSION}" == "${supported}" ]]; then
        FORMAT_SUPPORTED=true
        break
    fi
done

if [[ "${FORMAT_SUPPORTED}" == "false" && "${BACKUP_FORMAT_VERSION}" != "unknown" ]]; then
    echo "ERROR: Backup format version '${BACKUP_FORMAT_VERSION}' is not supported by this restore script." >&2
    echo "       Supported formats: ${RESTORE_SUPPORTED_FORMATS[*]}" >&2
    echo "       Update full-restore.sh to a version that supports this backup format." >&2
    exit 1
fi

# Compare backup API version with local codebase
LOCAL_API_VERSION="$(detect_api_version)"
if [[ "${BACKUP_API_VERSION}" != "unknown" && "${LOCAL_API_VERSION}" != "unknown" ]]; then
    if [[ "${BACKUP_API_VERSION}" != "${LOCAL_API_VERSION}" ]]; then
        warn "API version mismatch: backup=${BACKUP_API_VERSION}, local codebase=${LOCAL_API_VERSION}"
        warn "The backup was created with a different API version than the code you are restoring into."
        warn "You may need to run database migrations or version update scripts after restore:"
        warn "  python -m flask db upgrade"
        warn "  python -m server.swagger_server.backup.utils.db_version_updates"
    fi
fi

log "Backup format version: ${BACKUP_FORMAT_VERSION}"
log "Backup API version:    ${BACKUP_API_VERSION}"
log "Local API version:     ${LOCAL_API_VERSION}"

if [[ -f "${BACKUP_DIR}/MANIFEST.txt" ]]; then
    log "Backup manifest:"
    head -10 "${BACKUP_DIR}/MANIFEST.txt" | sed 's/^/  /'
fi
echo ""

# ---------------------------------------------------------------------------
# Restore configuration files
# ---------------------------------------------------------------------------

if [[ "${SKIP_CONFIG}" == "false" ]]; then
    log "=== Restoring configuration files ==="

    # .env
    if [[ -f "${BACKUP_DIR}/config/dot-env" ]]; then
        if [[ -f "${SCRIPT_DIR}/.env" ]]; then
            if confirm "Overwrite existing .env? (current will be saved as .env.pre-restore)"; then
                run cp "${SCRIPT_DIR}/.env" "${SCRIPT_DIR}/.env.pre-restore"
                run cp "${BACKUP_DIR}/config/dot-env" "${SCRIPT_DIR}/.env"
                log "Restored .env (previous saved as .env.pre-restore)"
                warn "IMPORTANT: Edit .env to update host-specific values before starting services!"
            fi
        else
            run cp "${BACKUP_DIR}/config/dot-env" "${SCRIPT_DIR}/.env"
            log "Restored .env"
            warn "IMPORTANT: Edit .env to update host-specific values before starting services!"
        fi
    else
        warn "No .env backup found — you will need to create one from env.template."
    fi

    # SSL certificates
    if [[ -d "${BACKUP_DIR}/ssl" ]] && ls "${BACKUP_DIR}/ssl/"*.pem &>/dev/null 2>&1; then
        log "Restoring SSL certificates..."
        run mkdir -p "${SCRIPT_DIR}/ssl"
        run cp -a "${BACKUP_DIR}/ssl/." "${SCRIPT_DIR}/ssl/"
        log "Restored ssl/"
    else
        warn "No SSL certificates in backup."
    fi

    # Vouch-Proxy
    if [[ -d "${BACKUP_DIR}/vouch" ]]; then
        log "Restoring Vouch-Proxy configuration..."
        run mkdir -p "${SCRIPT_DIR}/vouch"
        run cp -a "${BACKUP_DIR}/vouch/." "${SCRIPT_DIR}/vouch/"
        log "Restored vouch/"
    else
        warn "No Vouch-Proxy configuration in backup."
    fi

    # Nginx
    if [[ -d "${BACKUP_DIR}/nginx" ]]; then
        log "Restoring Nginx configuration..."
        run mkdir -p "${SCRIPT_DIR}/nginx"
        run cp -a "${BACKUP_DIR}/nginx/." "${SCRIPT_DIR}/nginx/"
        log "Restored nginx/"
    else
        warn "No Nginx configuration in backup."
    fi

    # Docker Compose
    for f in docker-compose.yaml docker-compose.yaml.docker docker-compose.yaml.local; do
        if [[ -f "${BACKUP_DIR}/config/${f}" ]]; then
            log "Restoring ${f}..."
            run cp "${BACKUP_DIR}/config/${f}" "${SCRIPT_DIR}/${f}"
        fi
    done

    # uWSGI config
    if [[ -f "${BACKUP_DIR}/config/core-api.ini" ]]; then
        log "Restoring uWSGI config..."
        run mkdir -p "${SCRIPT_DIR}/server"
        run cp "${BACKUP_DIR}/config/core-api.ini" "${SCRIPT_DIR}/server/core-api.ini"
    fi

    # Alembic migrations
    if [[ -d "${BACKUP_DIR}/migrations" ]]; then
        log "Restoring Alembic migrations..."
        run cp -a "${BACKUP_DIR}/migrations/." "${SCRIPT_DIR}/migrations/"
        log "Restored migrations/"
    fi

    # Application logs (optional)
    if [[ -d "${BACKUP_DIR}/logs" ]]; then
        if confirm "Restore application logs?"; then
            run mkdir -p "${SCRIPT_DIR}/logs"
            run cp -a "${BACKUP_DIR}/logs/." "${SCRIPT_DIR}/logs/"
            log "Restored logs/"
        fi
    fi

    # JSON table exports
    if [[ -d "${BACKUP_DIR}/json-export" ]] && ls "${BACKUP_DIR}/json-export/"*.json &>/dev/null 2>&1; then
        log "Restoring JSON table exports..."
        run mkdir -p "${SCRIPT_DIR}/server/swagger_server/backup/data"
        run cp "${BACKUP_DIR}/json-export/"*.json "${SCRIPT_DIR}/server/swagger_server/backup/data/"
        log "Restored JSON exports to server/swagger_server/backup/data/"
    fi

    log "=== Configuration restore complete ==="
    echo ""
fi

# ---------------------------------------------------------------------------
# Restore database
# ---------------------------------------------------------------------------

if [[ "${SKIP_DB}" == "false" ]]; then
    log "=== Restoring database ==="

    # Source .env if available (for POSTGRES_* variables)
    if [[ -f "${SCRIPT_DIR}/.env" ]]; then
        # shellcheck disable=SC1091
        source "${SCRIPT_DIR}/.env"
    fi

    for var in POSTGRES_SERVER POSTGRES_PORT POSTGRES_USER POSTGRES_DB; do
        if [[ -z "${!var:-}" ]]; then
            echo "ERROR: ${var} is not set. Source .env or export POSTGRES_* variables." >&2
            exit 1
        fi
    done

    # Detect Docker vs local database
    DB_CONTAINER="${DB_CONTAINER:-api-database}"
    USE_DOCKER_DB=false

    if [[ "${POSTGRES_SERVER}" == "database" ]] || [[ "${POSTGRES_SERVER}" == "${DB_CONTAINER}" ]]; then
        if docker inspect "${DB_CONTAINER}" &>/dev/null 2>&1; then
            USE_DOCKER_DB=true
            log "Detected Docker database (container: ${DB_CONTAINER})"
        else
            echo "ERROR: POSTGRES_SERVER=${POSTGRES_SERVER} looks like a Docker service name," >&2
            echo "       but container '${DB_CONTAINER}' is not running." >&2
            echo "       Start it with: docker-compose up -d database" >&2
            exit 1
        fi
    elif ! command -v pg_restore &>/dev/null && ! command -v psql &>/dev/null; then
        if docker inspect "${DB_CONTAINER}" &>/dev/null 2>&1; then
            USE_DOCKER_DB=true
            log "pg_restore/psql not found on host; falling back to Docker container '${DB_CONTAINER}'"
        else
            echo "ERROR: pg_restore/psql not found and database container '${DB_CONTAINER}' is not running." >&2
            echo "       Install PostgreSQL client tools or start the Docker stack." >&2
            exit 1
        fi
    fi

    # Find the dump file
    DUMP_FILE="$(find "${BACKUP_DIR}/database" -name "*.dump" -type f 2>/dev/null | head -1)"
    SQL_FILE="$(find "${BACKUP_DIR}/database" -name "*.sql" -type f 2>/dev/null | head -1)"

    if [[ -n "${DUMP_FILE}" ]]; then
        log "Found pg_dump custom format: $(basename "${DUMP_FILE}")"

        if [[ "${USE_DOCKER_DB}" == "true" ]]; then
            log "Target: container '${DB_CONTAINER}' / database '${POSTGRES_DB}'"
        else
            log "Target: ${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}"
        fi

        if confirm "Restore database from pg_dump? This will DROP and recreate objects."; then
            log "Restoring with pg_restore..."
            if [[ "${USE_DOCKER_DB}" == "true" ]]; then
                run docker exec -i -e PGPASSWORD="${POSTGRES_PASSWORD:-}" "${DB_CONTAINER}" \
                    pg_restore -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
                    --clean --if-exists --no-owner --no-privileges \
                    < "${DUMP_FILE}" || {
                        warn "pg_restore reported warnings (this is often normal for --clean on a fresh database)."
                    }
            else
                run env PGPASSWORD="${POSTGRES_PASSWORD:-}" pg_restore \
                    -h "${POSTGRES_SERVER}" \
                    -p "${POSTGRES_PORT}" \
                    -U "${POSTGRES_USER}" \
                    -d "${POSTGRES_DB}" \
                    --clean --if-exists \
                    --no-owner --no-privileges \
                    "${DUMP_FILE}" || {
                        warn "pg_restore reported warnings (this is often normal for --clean on a fresh database)."
                    }
            fi
            log "Database restore complete."
        fi
    elif [[ -n "${SQL_FILE}" ]]; then
        log "Found plain SQL dump: $(basename "${SQL_FILE}")"

        if [[ "${USE_DOCKER_DB}" == "true" ]]; then
            log "Target: container '${DB_CONTAINER}' / database '${POSTGRES_DB}'"
        else
            log "Target: ${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}"
        fi

        if confirm "Restore database from SQL dump? This will DROP and recreate objects."; then
            log "Restoring with psql..."
            if [[ "${USE_DOCKER_DB}" == "true" ]]; then
                run docker exec -i -e PGPASSWORD="${POSTGRES_PASSWORD:-}" "${DB_CONTAINER}" \
                    psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
                    < "${SQL_FILE}"
            else
                run env PGPASSWORD="${POSTGRES_PASSWORD:-}" psql \
                    -h "${POSTGRES_SERVER}" \
                    -p "${POSTGRES_PORT}" \
                    -U "${POSTGRES_USER}" \
                    -d "${POSTGRES_DB}" \
                    -f "${SQL_FILE}"
            fi
            log "Database restore complete."
        fi
    else
        warn "No database dump found in ${BACKUP_DIR}/database/."
        warn "You can restore from JSON exports using:"
        warn "  python -m server.swagger_server.backup.utils.db_restore"
    fi

    log "=== Database restore complete ==="
    echo ""
fi

# ---------------------------------------------------------------------------
# Post-restore checklist
# ---------------------------------------------------------------------------

log ""
log "============================================"
log "  Restore finished — post-restore checklist"
log "============================================"
log ""
log "  1. Edit .env and update host-specific values:"
log "       - POSTGRES_SERVER (if database host changed)"
log "       - CORE_API_SERVER_URL (new VM hostname/IP)"
log "       - NGINX_ACCESS_CONTROL_ALLOW_ORIGIN"
log "       - FABRIC_CORE_API / FABRIC_CREDENTIAL_MANAGER"
log ""
log "  2. Update vouch/config if the domain changed:"
log "       - cookie.domain"
log "       - post_logout_redirect_uris"
log "       - callback URL registered with CILogon"
log ""
log "  3. Update nginx/default.conf if hostname/ports changed."
log ""
log "  4. If SSL certs are host-specific, replace ssl/ contents"
log "     with certs for the new domain."
log ""
log "  5. Start services:"
log "       source .env"
log "       docker-compose up -d database"
log "       # Wait for PostgreSQL to be ready, then:"
log "       docker-compose up -d nginx vouch-proxy"
log "       python -m server.swagger_server  # or docker-compose up flask-server"
log ""
log "  6. Verify:"
log "       curl -k https://localhost:8443/ui/"
log ""
