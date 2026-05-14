"""v1.10.0 — quotas EnumResourceTypes update

Removes the obsolete `smartnic_bluefield_2_connectx_6` resource type and
adds two new ConnectX 7 variants. Aligned with the EnumResourceTypes
change in `server/swagger_server/database/models/quotas.py`.

This file is the **reference Alembic migration** for the v1.9.0 → v1.10.0
upgrade. Because `migrations/` is gitignored (each deployment maintains
its own migration chain), it is shipped here under `server/versions/`.

To apply it on a deployment:

    1. Copy this file into `migrations/versions/`
    2. Edit `down_revision` to point at your current Alembic head
       (run `flask db current` to find it)
    3. `uv run python -m flask db upgrade`

Notes on Postgres ENUM semantics:

  - Removing a Python enum member does NOT remove the value from the
    Postgres `enumresourcetypes` type. This migration deletes any
    `quotas` rows that reference the obsolete value, but leaves the
    Postgres ENUM type alone (the orphaned value is unreachable
    through the ORM but remains a valid SQL-level value).
  - Fully removing the orphaned ENUM value would require creating a
    new ENUM type, casting the column, and dropping the old type — a
    much heavier migration. Skipped here as cosmetic.
  - `ALTER TYPE … ADD VALUE` requires Postgres 12+ to run inside a
    transaction. The project's `docker-compose.yml.template` pins
    postgres:14, so this is safe. (The PG14 → PG17 upgrade will be
    handled as a separate maintenance window, unrelated to this
    migration.)

Revision ID: 1f10a0_quotas_enum_v1_10_0
Revises: <SET TO YOUR CURRENT HEAD>
Create Date: 2026-04-27
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '1f10a0_quotas_enum_v1_10_0'
down_revision = None  # CHANGE-ME — set to the current Alembic head before applying
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------

def upgrade():
    # Step 1 — delete any quota rows still referencing the obsolete
    # bluefield-2 resource type. Without this, the ORM will raise
    # LookupError the next time it tries to map such a row.
    op.execute(
        "DELETE FROM quotas "
        "WHERE resource_type = 'smartnic_bluefield_2_connectx_6'"
    )

    # Step 2 — extend the Postgres ENUM with the two new ConnectX 7 variants.
    # `IF NOT EXISTS` makes the migration idempotent if a previous attempt
    # added one of the values before failing.
    op.execute(
        "ALTER TYPE enumresourcetypes "
        "ADD VALUE IF NOT EXISTS 'smartnic_connectx_7_100'"
    )
    op.execute(
        "ALTER TYPE enumresourcetypes "
        "ADD VALUE IF NOT EXISTS 'smartnic_connectx_7_400'"
    )


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------

def downgrade():
    """
    Postgres has no DROP VALUE for ENUM types — values added via
    `ALTER TYPE ... ADD VALUE` cannot be removed without rebuilding the
    type. Likewise, the deleted bluefield rows cannot be reconstructed.

    Downgrade is therefore intentionally a no-op. If a true rollback is
    required, restore the database from the pre-migration backup taken
    in Phase 0 of the v1.9.0 → v1.10.0 migration guide.
    """
    pass
