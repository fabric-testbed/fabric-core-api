"""v1.11.0 — projects EnumProjectTypes update

Adds the new `infrastructure` project type. Aligned with the
EnumProjectTypes change in `server/swagger_server/database/models/projects.py`
(infrastructure = 7).

This file is the **reference Alembic migration** for the v1.10.0 → v1.11.0
upgrade. Because `migrations/` is gitignored (each deployment maintains
its own migration chain), it is shipped here under `server/versions/`.

To apply it on a deployment:

    1. Copy this file into `migrations/versions/`
    2. Edit `down_revision` to point at your current Alembic head
       (run `flask db current` to find it)
    3. `uv run python -m flask db upgrade`

Notes on Postgres ENUM semantics:

  - `ALTER TYPE … ADD VALUE` appends `infrastructure` after the existing
    values in the Postgres `enumprojecttypes` type. SQLAlchemy maps enum
    members by NAME, so the SQL-level ordering difference from the Python
    definition order is irrelevant.
  - `ALTER TYPE … ADD VALUE` requires Postgres 12+ to run inside a
    transaction. The project's `docker-compose.yml.template` pins
    postgres:14, so this is safe. (The PG14 → PG17 upgrade will be
    handled as a separate maintenance window, unrelated to this
    migration.)

Revision ID: 1f1100_projects_enum_v1_11_0
Revises: <SET TO YOUR CURRENT HEAD>
Create Date: 2026-07-24
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "1f1100_projects_enum_v1_11_0"
down_revision = None  # CHANGE-ME — set to the current Alembic head before applying
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


def upgrade():
    # Extend the Postgres ENUM with the new infrastructure project type.
    # `IF NOT EXISTS` makes the migration idempotent if a previous attempt
    # failed after adding the value.
    op.execute("ALTER TYPE enumprojecttypes ADD VALUE IF NOT EXISTS 'infrastructure'")


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------


def downgrade():
    """
    Postgres has no DROP VALUE for ENUM types — values added via
    `ALTER TYPE ... ADD VALUE` cannot be removed without rebuilding the
    type. No rows are modified by this migration, so downgrade is
    intentionally a no-op. If a true rollback is required (i.e. rows
    already reference 'infrastructure'), restore the database from the
    pre-migration backup.
    """
    pass
