# FABRIC Core API

A Python Flask REST API providing core services for the [FABRIC Testbed](https://fabric-testbed.net):

Built with [Connexion](https://connexion.readthedocs.io/) (OpenAPI 3.0.0) on top of Flask, backed by PostgreSQL, and federated with [COmanage Registry](https://www.cilogon.org/comanage) for identity and authorization.

> **DISCLAIMER:** This code may not be up-to-date with the latest package or security advisories. The review/update cadence is driven by the FABRIC project lifecycle and not actively maintained outside that scope. **Use at your own risk.**

---

## Table of Contents

- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Quick Start (Local Docker Compose)](#quick-start)
- [Configuration](#configuration)
- [Running Modes](#running-modes)
  - [All-in-Docker (recommended for local)](#mode-docker)
  - [Local Flask + Docker Postgres (development)](#mode-local)
- [Database Lifecycle](#database-lifecycle)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [API Documentation](#api-docs)
- [References](#references)

---

## <a name="architecture"></a>Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │                  Browser                     │
                    │           https://127.0.0.1:8443             │
                    └───────────────────┬──────────────────────────┘
                                        │ TLS
                    ┌───────────────────▼──────────────────────────┐
                    │  Nginx                  (TLS, CORS, auth)    │
                    │  - auth_request /validate ──► Vouch          │
                    │  - 401 ──► /login (CILogon OIDC)             │
                    │  - proxy_pass / ──► Flask                    │
                    └────────┬─────────────────────────┬───────────┘
                             │                         │
                  ┌──────────▼────────┐    ┌───────────▼──────────┐
                  │    Vouch Proxy    │    │   Flask / uWSGI      │
                  │  OIDC client      │    │   Connexion app      │
                  │  Issues JWT in    │    │   ── port 6000 ──    │
                  │  session cookie   │    └───────────┬──────────┘
                  └──────────┬────────┘                │
                             │                         │
                  ┌──────────▼─────────┐    ┌──────────▼──────────┐
                  │     CILogon        │    │     PostgreSQL      │
                  │     (OIDC IdP)     │    │   ── port 5432 ──   │
                  └────────────────────┘    └─────────────────────┘
                                                       │
                                            ┌──────────▼──────────┐
                                            │  COmanage Registry  │
                                            │  (synced via API)   │
                                            └─────────────────────┘
```

**Request flow:** Browser → Nginx (TLS, CORS) → `auth_request` to Vouch → on success, Nginx forwards to Flask. Flask routes by `operationId` from `swagger.yaml` to controllers, which delegate to `response_code/` business logic, which read/write Postgres and call out to COmanage as needed.

See [`CLAUDE.md`](./CLAUDE.md) for a deeper dive into request flow, code organization, auth decorators, and adding new endpoints.

---

## <a name="repository-layout"></a>Repository Layout

```
fabric-core-api/
├── server/swagger_server/        # Flask application
│   ├── swagger/swagger.yaml      #   OpenAPI 3.0.0 spec (source of truth)
│   ├── controllers/              #   Thin routing layer
│   ├── response_code/            #   Business logic
│   ├── database/models/          #   SQLAlchemy ORM models
│   └── backup/                   #   DB backup, restore, version updates
├── migrations/                   # Alembic migration history
├── nginx/default.conf.template   # Nginx reverse-proxy config
├── vouch/config.yml.template     # Vouch (OIDC) config
├── docker-compose.yml.template   # Compose stack (4 services)
├── env.template                  # Environment variables
├── ssl/                          # Self-signed dev certs (DO NOT USE IN PROD)
├── docs/                         # Endpoint-level docs
└── full-backup.sh / full-restore.sh   # VM-to-VM migration helpers
```

---

## <a name="quick-start"></a>Quick Start (Local Docker Compose)

The four `*.template` files in this repository are pre-configured for local development at **https://127.0.0.1:8443**. Copy them into place, fill in secrets, and bring the stack up.

### Prerequisites

- Docker (24+) and Docker Compose v2
- A registered OIDC client at [CILogon](https://www.cilogon.org/oidc) with redirect URI `https://127.0.0.1:8443/auth`
- Access credentials for a **COmanage Registry** API user (can be a sandbox/dev registry)
- (Optional) Python 3.12 + virtualenv if you also want to run Flask outside Docker

### Setup

```console
# 1. Render config files from templates
cp env.template .env
cp docker-compose.yml.template docker-compose.yml
cp nginx/default.conf.template nginx/default.conf
cp vouch/config.yml.template vouch/config.yml

# 2. Edit each file — search for `CHANGE-ME` markers in env.template,
#    set vouch_oidc_client_id / vouch_oidc_client_secret in vouch/config.yml,
#    and double-check the upstream proxy_pass in nginx/default.conf

# 3. Source the environment so Compose can interpolate variables
source .env

# 4. Pull images and bring everything up
docker compose pull
docker compose up -d

# 5. Initialize / migrate the database (one-time)
docker compose exec flask-server python -m flask db upgrade

# 6. Seed initial people, projects, and roles from COmanage
docker compose exec flask-server python -m server.swagger_server.database.db_load
```

The API is now reachable at **https://127.0.0.1:8443** (you'll need to accept the self-signed certificate on first visit).

Tail logs with `docker compose logs -f flask-server`.

---

## <a name="configuration"></a>Configuration

Four template files drive the deployment. All four are committed; the rendered (uncommitted) copies live alongside them.

| Template | Rendered to | Purpose |
|---|---|---|
| `env.template` | `.env` | All environment variables (Postgres, COmanage, Vouch, SSH, SMTP, …) |
| `docker-compose.yml.template` | `docker-compose.yml` | Compose stack: flask-server, database, nginx, vouch-proxy |
| `nginx/default.conf.template` | `nginx/default.conf` | TLS termination, CORS, `auth_request`, upstream `proxy_pass` |
| `vouch/config.yml.template` | `vouch/config.yml` | Vouch Proxy: OIDC client + cookie + JWT |

`env.template` is the master configuration document — every variable is grouped into one of 11 sections with inline comments describing what it controls and which other files it must stay in sync with. Markers used:

- `# CHANGE-ME` — placeholder values that MUST be replaced before deployment
- `# LOCAL` / `# DOCKER` — toggle between local-Flask and Docker-Compose modes (uncomment the appropriate line)

**Cross-file invariants** to watch when editing:

- `VOUCH_COOKIE_NAME` (.env) ↔ `vouch.cookie.name` (vouch/config.yml)
- `VOUCH_JWT_SECRET` (.env) ↔ `vouch.jwt.secret` (vouch/config.yml)
- nginx `/auth` location ↔ `oauth.callback_url` (vouch/config.yml) ↔ CILogon OIDC client redirect URI
- `NGINX_ACCESS_CONTROL_ALLOW_ORIGIN` (.env) ↔ nginx CORS `Access-Control-Allow-Origin`

---

## <a name="running-modes"></a>Running Modes

### <a name="mode-docker"></a>All-in-Docker (recommended for local)

Use the [Quick Start](#quick-start) above — every service (Postgres, Nginx, Vouch, Flask) runs in a container.

### <a name="mode-local"></a>Local Flask + Docker Postgres (development)

Useful when iterating on Python code (no rebuild on every change). Postgres still runs in Docker; Flask runs on the host so you can attach a debugger.

```console
# 1. Create and activate a virtualenv
virtualenv -p python3.12 venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Toggle .env for local Flask:
#    - uncomment   POSTGRES_SERVER=127.0.0.1
#    - comment out POSTGRES_SERVER=database
#    - use the LOCAL PYTHONPATH line
source .env

# 3. Start only Postgres in Docker
docker compose up -d database

# 4. Initialize / migrate the database
python -m flask db upgrade
python -m server.swagger_server.database.db_load

# 5. Run the Flask app on port 6000
python -m server.swagger_server
```

If you also want Nginx + Vouch in front of the host-bound Flask, edit `nginx/default.conf` to switch the upstream `proxy_pass` from `http://flask-server:6000` to `http://host.docker.internal:6000` (macOS) or `http://172.17.0.1:6000` (Linux), then bring those two services up: `docker compose up -d nginx vouch-proxy`.

---

## <a name="database-lifecycle"></a>Database Lifecycle

| Operation | Command |
|---|---|
| Apply migrations | `python -m flask db upgrade` |
| Generate a new migration | `python -m flask db migrate -m "description"` |
| Load people/projects/roles from COmanage | `python -m server.swagger_server.database.db_load` |
| Per-table JSON export (34 tables) | `python -m server.swagger_server.backup.utils.db_export` |
| Per-table JSON restore | `python -m server.swagger_server.backup.utils.db_restore` |
| Cross-version backfill | `python -m server.swagger_server.backup.utils.db_version_updates` |
| Full VM-to-VM backup | `./full-backup.sh` |
| Full VM-to-VM restore | `./full-restore.sh <archive>` |

Schema versioning lives in `server/swagger_server/__init__.py` (`__API_VERSION__`). Per-version backfill scripts live under `server/versions/<from>_to_<to>/` and are invoked after the corresponding Alembic migration. See [`docs/full-backup-and-restore.md`](./docs/full-backup-and-restore.md) for the full backup/restore workflow.

---

## <a name="testing"></a>Testing

```console
# Full suite via tox (py38)
tox

# Direct invocation
nosetests

# A single test file
nosetests server/swagger_server/test/test_people_controller.py
```

Tests live in `server/swagger_server/test/` and use [nose](https://nose.readthedocs.io/) with [flask_testing](https://flask-testing.readthedocs.io/).

---

## <a name="production-deployment"></a>Production Deployment

The templates are tuned for local development. **Do not deploy them as-is.** Before promoting to a production host:

### Networking

- **Replace the self-signed certs in `ssl/`** with real CA-issued certificates (Let's Encrypt, institutional CA, etc.). The included certs are CN=localhost.
- Set `server_name` and the `:8443` external port in `nginx/default.conf` to your production FQDN and port (typically `:443`).
- In `docker-compose.yml`, **remove the published ports for `flask-server`, `database`, and `vouch-proxy`** so only Nginx (`80`/`443`) is reachable from outside the host.

### CORS

- Replace `add_header 'Access-Control-Allow-Origin' '*'` in `nginx/default.conf` with the explicit origin from `NGINX_ACCESS_CONTROL_ALLOW_ORIGIN`. Wildcard origins are incompatible with credentialed requests.

### Vouch / OIDC

- In `vouch/config.yml`:
  - Set `vouch.cookie.secure: true` (requires HTTPS).
  - Set `vouch.cookie.domain` to your production domain.
  - Replace the placeholder `vouch_oidc_client_id` / `vouch_oidc_client_secret` with values from your CILogon OIDC client registration.
  - Update `oauth.callback_url` and `vouch.post_logout_redirect_uris` to use your production URL.
- Generate a fresh `VOUCH_JWT_SECRET` (≥44 chars / 256 bits, e.g. `openssl rand -base64 48`).

### Secrets

- Replace every `CHANGE-ME` value in `.env` (Postgres password, COmanage credentials, SMTP, SSH key secret, service-account auth tokens).
- Do not commit the rendered `.env`, `docker-compose.yml`, `nginx/default.conf`, or `vouch/config.yml` — `.gitignore` already excludes them.
- Keep the rendered `vouch/config.yml` locked down (`chmod 600`) since it contains the OIDC client secret.

### COmanage

- Point `COMANAGE_API_*` at your production registry, not a sandbox.
- Verify every `COU_ID_*` matches the COU IDs in the production registry — these are numeric and **will differ** between dev/prod registries even when names match.

### Database

- Use a managed Postgres or a separately-administered Postgres host rather than the in-stack `database` container for serious workloads. Update `POSTGRES_SERVER` accordingly.
- Configure regular `pg_dump` (or use `./full-backup.sh`) on a cron schedule.

### Tier flag

- Set `CORE_API_DEPLOYMENT_TIER=production` so production-only tag sets and feature flags are loaded.

---

## <a name="api-docs"></a>API Documentation

- [`docs/README.md`](./docs/README.md) — overall API documentation index
- Endpoint guides: [people](./docs/people.md), [projects](./docs/projects.md), [sshkeys](./docs/sshkeys.md), [storage](./docs/storage.md), [announcements](./docs/announcements.md), [whoami](./docs/whoami.md), [version](./docs/version.md), [testbed-info](./docs/testbed-info.md), [core-api-metrics](./docs/core-api-metrics.md)
- Operational guides: [pagination](./docs/pagination.md), [status codes](./docs/status-codes.md), [singleton resources](./docs/singleton.md), [check-cookie](./docs/check-cookie.md), [full backup & restore](./docs/full-backup-and-restore.md)
- The OpenAPI spec itself: [`server/swagger_server/swagger/swagger.yaml`](./server/swagger_server/swagger/swagger.yaml)

---

## <a name="references"></a>References

- [Connexion](https://connexion.readthedocs.io/en/stable/) — OpenAPI-first request routing
- [Flask](https://flask.palletsprojects.com)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) — Alembic for Flask
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Vouch Proxy](https://github.com/vouch/vouch-proxy) — OIDC reverse-proxy auth
- [CILogon](https://www.cilogon.org) — federated OIDC identity provider
- [COmanage Registry](https://www.cilogon.org/comanage) — collaborative organization management
