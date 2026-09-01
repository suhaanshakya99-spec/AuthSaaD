"""added verification to user

Revision ID: 84019d1469c6
Revises: 340bb07815bb
Create Date: 2026-08-31 08:19:20.541657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '84019d1469c6'
down_revision: Union[str, Sequence[str], None] = '340bb07815bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'end_users',
        sa.Column(
            'verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        )
    )


def downgrade() -> None:
    op.drop_column('end_users', 'verified')
