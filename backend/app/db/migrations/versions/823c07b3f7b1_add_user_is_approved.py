"""add user is_approved

Revision ID: 823c07b3f7b1
Revises: a3d508b80950
Create Date: 2026-07-22 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '823c07b3f7b1'
down_revision: Union[str, None] = 'a3d508b80950'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills existing accounts to approved so nobody already
    # using the app gets locked out; new signups explicitly pass is_approved=False.
    op.add_column(
        'users',
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )


def downgrade() -> None:
    op.drop_column('users', 'is_approved')
