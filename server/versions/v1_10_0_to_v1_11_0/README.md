# v1.10.0 → v1.11.0

## New `infrastructure` project type

Adds `infrastructure` to `EnumProjectTypes` (`infrastructure = 7`).

Code changes (already in this release):

- `server/swagger_server/database/models/projects.py` — enum member `infrastructure = 7`
- `server/swagger_server/swagger/swagger.yaml` — `projects_post` / `projects_patch` `project_type` enums
- `server/swagger_server/models/projects_post.py` / `projects_patch.py` — `allowed_values`
- `server/swagger_server/response_code/projects_controller.py` — `infrastructure` joins
  `maintenance` / `service` / `industry` as facility-operator-only in project POST/PATCH
- `server/swagger_server/response_code/projects_utils.py` — project creation persists the
  requested `project_type`
- `server/swagger_server/response_code/people_utils.py` — active `infrastructure` projects
  qualify their users for JupyterHub access; only `service` projects remain excluded
- `server/swagger_server/test/test_project_type_regressions.py` — focused POST/PATCH,
  enum-exposure, and JupyterHub policy coverage
- **Bug fix**: `projects_patch` no longer declares `default: research` on `project_type`
  (spec + generated model). Previously a PATCH that omitted `project_type` deserialized
  as `research` and silently reset the project's type — undoing facility-operator-assigned
  types (`infrastructure`, `maintenance`, `service`, `industry`) on any unrelated field
  edit. An omitted `project_type` now leaves the stored type unchanged.

Database change (apply per deployment):

- `project_types_alembic.py` — reference Alembic migration adding the value to the
  Postgres `enumprojecttypes` type via `ALTER TYPE … ADD VALUE IF NOT EXISTS`.
  Copy into `migrations/versions/`, set `down_revision` to your current head
  (`flask db current`), then `uv run python -m flask db upgrade`.

No data backfill required — the change is purely additive. New projects continue to
default to `research` when `project_type` is omitted. A facility operator can select
`infrastructure` through either `POST /projects` or `PATCH /projects/{uuid}`.
