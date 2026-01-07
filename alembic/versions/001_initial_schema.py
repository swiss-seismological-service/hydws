"""Initial database schema and partition function

Revision ID: 001
Revises:
Create Date: 2025-01-07

"""
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op
from hydws.datamodel.base import ORMBase

revision: str = '001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def execute_sql_file(filename: str) -> None:
    """Execute a SQL file from the scripts directory."""
    sql_file = Path(__file__).parent.parent / "scripts" / filename
    if sql_file.exists():
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        op.execute(sa.text(sql_content))
        print(f"Executed SQL file: {filename}")
    else:
        raise FileNotFoundError(f"SQL file not found: {sql_file}")


def upgrade() -> None:
    """Create initial schema and partition function."""
    print("Creating HYDWS database schema...")

    bind = op.get_bind()
    ORMBase.metadata.create_all(bind)

    print("Installing partition generation procedure...")
    execute_sql_file("create_partitions.sql")

    print("Database schema created successfully!")


def downgrade() -> None:
    """Remove all HYDWS database objects."""
    print("Removing HYDWS database schema...")

    bind = op.get_bind()

    bind.execute(sa.text(
        "DROP PROCEDURE IF EXISTS generate_partitioned_tables CASCADE;"
    ))
    print("Dropped partition procedure.")

    result = bind.execute(sa.text("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename LIKE 'hydraulicsample_%'
        ORDER BY tablename;
    """))
    partitions = [row[0] for row in result]
    for partition in partitions:
        bind.execute(sa.text(f"DROP TABLE IF EXISTS {partition} CASCADE;"))
    print(f"Dropped {len(partitions)} partition tables.")

    bind.execute(sa.text("DROP TABLE IF EXISTS hydraulicsample CASCADE;"))
    bind.execute(sa.text("DROP TABLE IF EXISTS boreholesection CASCADE;"))
    bind.execute(sa.text("DROP TABLE IF EXISTS borehole CASCADE;"))
    print("Dropped main tables.")

    print("Database schema removed.")
