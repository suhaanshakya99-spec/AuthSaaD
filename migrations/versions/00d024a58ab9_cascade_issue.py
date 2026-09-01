"""cascade issue

Revision ID: 00d024a58ab9
Revises: f0f50aa63f03
Create Date: 2026-08-31 08:54:27.796824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '00d024a58ab9'
down_revision: Union[str, Sequence[str], None] = 'f0f50aa63f03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "end_users_project_id_fkey",
        "end_users",
        type_="foreignkey"
    )

    op.create_foreign_key(
        "end_users_project_id_fkey",
        "end_users",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint(
        "end_users_project_id_fkey",
        "end_users",
        type_="foreignkey"
    )

    op.create_foreign_key(
        "end_users_project_id_fkey",
        "end_users",
        "projects",
        ["project_id"],
        ["id"]
    )
