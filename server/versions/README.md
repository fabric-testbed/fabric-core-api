# Versions

Version changelog and migration information

## Table of Contents

- [v1.11.5](#v1115) - released TBD
- [v1.11.4](#v1114) - released TBD
- [v1.11.3](#v1113) - released TBD
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

### <a name="v1115"></a>v1.11.5

Deployed on: TBD

Data-correctness patch release. No schema change - no migration is required.

- fix: an organization affiliation is now resolved even when the identity provider sends no `eduPersonAffiliation`. Storing the OrgIdentity was conditional on that attribute, so when it was absent the organization *name* was discarded along with it and `people.org_affiliation` was left NULL. `journey_tracker_utils`, `people_uuid_get` and `core_api_metrics` read affiliation only through that foreign key, so those people render as `null` / `'Unknown'`. `organizations.affiliation` is NOT NULL, so every write now falls back to `UNSPECIFIED_ORG_AFFILIATION` (`'unspecified'`) rather than skipping the row. Affects `comanage_utils.update_org_affiliation`, `update_organizations` and `update_user_org_affiliations`, and `load_organizations` in both `db_load` and `db_verify`.

**Scale, measured on production.** 617 of 3,289 people (19%) carried a NULL `org_affiliation` on 2026-09-01, and the count was still climbing - the same walk read 613 of 3,285 one day earlier, so every affected new enrollment was landing NULL. This release stops the population growing; it does not repair the people already affected.

**The existing backlog needs a one-shot repair.** The ordinary heal is login-driven, so dormant accounts never recover on their own. `swagger_server.database.utils.repair_org_affiliation` walks the whole NULL population once and is idempotent. It is not shipped in the image - it is mounted read-only into a throwaway container by `scripts/org-affiliation-dry-pass.sh` on the `v2-develop` branch, which never touches the serving stack. Dry passes against both 1.x tiers on 2026-09-01 resolved every affected person with nothing unresolved. Run the repair only after this release is deployed: `--apply` needs `UNSPECIFIED_ORG_AFFILIATION`, which does not exist on 1.11.4, and the script guards against exactly that.

### <a name="v1114"></a>v1.11.4

Deployed on: TBD

Reliability patch release. No schema change — no migration or backfill is required.

- fix: SSH key expiry notifications are scheduled by the uWSGI master process instead of a thread inside a worker. `GET /start` launched a `threading.Thread` in whichever of the eight workers served the request; `core-api.ini` sets `max-requests = 5000`, so uWSGI recycled that worker and destroyed the thread with it — silently, with no error and no restart — while `task_timeout_tracker.value` still read `running`, which made a later `GET /start` answer "Task Monitor Already Running" and refuse to launch a replacement. The task then stayed dead until someone noticed and reset the row by hand. Found on all three tiers in August 2026: production had run the check once in four days across 22 worker respawns, alpha-6 had been dead for 16 days, and beta-3 for 7. The master process is never recycled by `max-requests`, so the schedule cannot be lost this way.
- removed: `GET /start`. It existed only to launch that thread, it was never in the OpenAPI spec, and the operation count is unchanged. It was also an unauthenticated public route that triggered a mail run on its first call. Access logs across all three tiers show no legitimate caller — only internet scanners probing `/start.action`. To run the check by hand inside the container: `python -c "from swagger_server.__main__ import app; from swagger_server.response_code.task_monitor import check_sshkey_expiry_and_email; check_sshkey_expiry_and_email(app)"`.
- fix: a 400 response now says which field failed validation and why. `flask_bad_request` formatted the exception itself, and Connexion's `BadRequestProblem` carries its message on `.detail` while stringifying to an empty string, so every body-validation rejection arrived as the bare prefix `Validation error or other malformed request type:` in both the body and the `X-Error` header. Measured cost: `broker.fabric-testbed.net` sent 3,602 `PUT /quotas/{uuid}` requests to production and received 3,602 400s with no indication of the cause, while `quota_used` stayed 0 across 5,678 rows. The detail is collapsed to one line and capped at 200 characters because `cors_400` copies it into `X-Error`, where a newline invalidates the response.
- config: `SKE_CRON_HOUR` (default `6`) and `SKE_CRON_MINUTE` (default `0`) set the daily fire time, in the container's timezone, using uWSGI cron semantics where `-1` is a wildcard. Both are optional — existing `.env` files need no change. `SKE_TIMEOUT_IN_SECONDS` no longer sets the cadence; half its value is now the debounce that keeps a second fire in the same day from re-sending notifications.

**Operational change.** The post-deploy step of resetting `task_timeout_tracker` and calling `GET /start` is obsolete and must be dropped from the runbook — nothing needs to be started by hand after a redeploy. Verify instead that the container logs the scheduled run at `SKE_CRON_HOUR` and that `last_updated` on the `ssh_key_expiry` row advances. There is no scheduler outside uWSGI, so a local `flask run` never sends expiry mail.

**Client-visible wire change.** The `details` field and `X-Error` header of a 400 now carry the validation message instead of an empty string. Callers matching on the exact prefix string are unaffected; the prefix is unchanged.

### <a name="v1113"></a>v1.11.3

Deployed on: TBD

Security patch release. No schema change — no migration or backfill is required.

- security: the `/storage` write operations (`POST /storage`, `PATCH /storage/{uuid}`, `DELETE /storage/{uuid}`) no longer substitute an identity. Each operation used to promote any caller whose identity resolved to no local person to the first active facility operator, after which the facility-operator check passed and the write proceeded. A `readonly` bearer token, a `services` bearer token, or any authenticated user whose `sub` is not in the local people table could create, modify, and delete persistent volumes. Those callers now receive 403.
- security: `GET /storage` and `GET /storage/{uuid}` keep the existing global-read behavior only for the named `readonly` and `services` service tokens. An authenticated human whose `sub` is unknown locally now receives 403 instead of being promoted to facility-operator visibility over all storage.
- security: an unset or blank static service-token environment variable (`ANSIBLE_AUTHORIZATION_TOKEN`, `READONLY_AUTHORIZATION_TOKEN`, `SERVICES_AUTHORIZATION_TOKEN`) no longer matches any caller. `os.getenv()` returns `None` for an unset variable and the comparison stringified it to `'None'`, so a caller sending the literal token `None` matched the ansible branch and resolved to a real facility operator. The comparison now runs only when the variable is configured.
- internal: static service tokens are resolved before JWT handling, so they no longer touch the PSK/JWKS lookup or the credential-manager fetch. The ansible integration continues to resolve to a real facility operator via `first_valid_facility_operator()`.

**Client-visible wire change.** Callers that relied on the removed identity substitution now receive 403 — `readonly`/`services` tokens and unknown-`sub` users on `/storage` writes, and unknown-`sub` human callers on `/storage` reads. The named `readonly`/`services` service tokens retain their existing `/storage` read access.

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
