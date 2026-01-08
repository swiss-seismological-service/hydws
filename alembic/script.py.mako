"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


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
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
