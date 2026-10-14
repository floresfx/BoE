"""fase 3b fix: trial_ends_at

Revision ID: a84e5332bd50
Revises: 14eb4eb1d6bd
Create Date: 2026-10-14 16:43:55.524259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a84e5332bd50'
down_revision: Union[str, Sequence[str], None] = '14eb4eb1d6bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
