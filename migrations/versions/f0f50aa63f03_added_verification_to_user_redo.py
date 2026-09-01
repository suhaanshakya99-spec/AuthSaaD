"""added verification to user redo

Revision ID: f0f50aa63f03
Revises: 84019d1469c6
Create Date: 2026-08-31 08:28:26.332761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f0f50aa63f03'
down_revision: Union[str, Sequence[str], None] = '84019d1469c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'end_users',
        'verified',
        existing_type=sa.VARCHAR(),
        type_=sa.Boolean(),
        existing_nullable=False,
        postgresql_using="verified::boolean"
    )


def downgrade() -> None:
    op.alter_column(
        'end_users',
        'verified',
        existing_type=sa.Boolean(),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="verified::text"
    )
