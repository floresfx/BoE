"""roles_globales_sin_tenant

Revision ID: 4f872f9dc741
Revises: 5617086e8609
Create Date: 2026-10-10 17:08:44.108528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f872f9dc741'
down_revision: Union[str, Sequence[str], None] = '5617086e8609'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
