# Versions

Version changelog and migration information

## Table of Contents

- [v1.11.2](#v1112) - released TBD
- [v1.11.1](#v1111) - released TBD
- [v1.11.0](#v1110) - released 07/24/2026
- [v1.6.1](#v161) - released TBD
- [v1.6.0](#v160) - released 09/21/2023
- [v1.5.2](#v152) - released 09/06/2023
- [v1.4.2](#v142) - released 03/16/2023
- [v1.4.1](#v141) - released 02/07/2023
- [v1.4.0](#v140) - released 01/23/2023
- [v1.3.0](#v130) - released 08/29/2022

### <a name="v1112"></a>v1.11.2

Deployed on: TBD

Dependency security release. No schema change — no migration or backfill is required.

- security: bump `cryptography` 48.0.1 → 50.0.0 for CVE-2026-69247 (Bleichenbacher-oracle hardening in PKCS7 decryption). This API reaches `cryptography` only transitively — via `authlib`, `joserfc`, and `fabric-fss-utils` — and none of those touch the affected PKCS7 path, so exposure was nil; the bump clears the shipped vulnerable code and the Dependabot alert. Verified against the JWT (RS256/HS256) and SSH key generation (ecdsa/rsa) paths. (#178)
- config: `env.template` § 5 now documents the `SKE_*` trio (`SKE_DESCRIPTION`, `SKE_NAME`, `SKE_TIMEOUT_IN_SECONDS`). Without them, `init_task_tracker.py` fails to seed the `ssh_key_expiry` tracker row on fresh installs and `GET /start` errors instead of launching the SSH key expiry notification monitor. Existing deployments carrying a populated `.env` should add the trio by hand. (#180)

### <a name="v1111"></a>v1.11.1

Deployed on: TBD

Security patch release. No schema change — no migration or backfill is required.

- security: `GET /projects/{uuid}` no longer discloses private projects to unauthenticated callers. The anonymous branch had no `is_public` check while the authenticated non-member branch already returned 403 for the same condition, so an anonymous caller received strictly more of a private project (name, description, communities, project_funding, fabric_matrix, project_type) than a signed-in non-member. The guard mirrors that branch. `GET /projects` was already safe.
- security: 500 responses no longer echo exception text. Both the body `details` field and the `X-Error` header now return the constant `An internal server error occurred.` — SQLAlchemy/driver strings could carry SQL, bound parameters, and control characters. Diagnostics are not lost; they moved to the server log.
- `GET /announcements` rejects NUL bytes in `search` at the spec layer (`pattern: '^[^\x00]*$'`), returning 400 instead of reaching the driver and producing a 500.
- repository: releases are now mirrored to the public [fabric-testbed/fabric-core-api](https://github.com/fabric-testbed/fabric-core-api) — see `.publish-include` for what ships.

**Client-visible wire change.** Any consumer or operator tooling that parsed `Oops! something went wrong with X(): <exc>` out of a 500 body or the `X-Error` header now receives a constant instead. This affects every 500 the API can emit (93 `cors_500` call sites), so troubleshooting that relied on reading the exception off the wire now needs the server log.

### <a name="v1110"></a>v1.11.0

Deployed on: TBD

- new `infrastructure` project type (`EnumProjectTypes.infrastructure = 7`) across spec, models, and authorization
- `infrastructure`/`maintenance`/`service`/`industry` are facility-operator-only on both `POST /projects` and `PATCH /projects/{uuid}`
- `POST /projects` now persists the requested `project_type` (omitted still defaults to `research`)
- bug fix: `PATCH /projects/{uuid}` omitting `project_type` no longer silently resets the project's type to `research`
- active `infrastructure` projects qualify users for JupyterHub access (only `service` remains excluded)
- database: apply `v1_10_0_to_v1_11_0/project_types_alembic.py` (`ALTER TYPE enumprojecttypes ADD VALUE IF NOT EXISTS 'infrastructure'`) before or with the code rollout — see [v1_10_0_to_v1_11_0/README.md](./v1_10_0_to_v1_11_0/README.md)

### <a name="v161"></a>v1.6.1

Deployed on: TBD

### <a name="v160"></a>v1.6.0

Deployed on: 09/21/2023

- long lived tokens model updates and endpoints
- check cookie user validation endpoint
- reframe user model to not rely on `email` claim alone, but also function using `sub` claim when email not provided
- export and reload scripts
- add `exact_match` parameter to `/people` and `/projects` searches (default is False)
- misc bug fixes

### <a name="v152"></a>v1.5.2

Deployed on: 09/06/2023

- if `email` is found as a claim, use it
- if `email` is not found, pull in user `sub` claim and interrogate COmanage API for CoPerson by Identifier until either an email is found, or account creation fails 
- if an email is not found in COmanage (which should never be the case) an account cannot be created for the user - individual consultation at that time (lets hope we don’t see this)

### <a name="v150"></a>v1.5.0

Deployed on: 08/17/2023

### <a name="v142"></a>v1.4.2

Deployed on: 03/16/2023

- Add site storage endpoints:
  - [/storage]() - GET, POST
  - [/storage/sites]() - GET
  - [/storage/{uuid}]() - GET, PATCH, DELETE
- Add `is_locked` and `expires_on` to FabricProjects model
- Add [/projects/{uuid}/expires-on]() API endpoint
- Add more robust DB export and restore scripts
- [migration details](./v1.4.1-to-v1.4.2/README.md)

### <a name="v141"></a>v1.4.1

Deployed on: 02/07/2023

- Hotfix for bastion response that are missing `bastion_login` attribute
- No change to database

### <a name="v140"></a>v1.4.0

Deployed on: 01/23/2023

- No change to database

### <a name="v130"></a>v1.3.0

Deployed on: 08/29/2022

- Initial deployment of fabric-core-api
- [migration details](./pr-uis-to-v1.3.0/README.md)
