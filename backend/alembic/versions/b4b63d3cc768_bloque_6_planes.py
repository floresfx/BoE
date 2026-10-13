"""bloque 6: planes

Revision ID: b4b63d3cc768
Revises: dde40b4784b7
Create Date: 2026-10-13 18:54:45.800764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b4b63d3cc768'
down_revision: Union[str, Sequence[str], None] = 'dde40b4784b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Crear plan_features
    op.create_table(
        'plan_features',
        sa.Column('plan_id', sa.UUID(), nullable=False),
        sa.Column('feature_id', sa.UUID(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['feature_id'], ['features.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_id', 'feature_id', name='uq_plan_feature')
    )
    op.create_index(op.f('ix_plan_features_feature_id'), 'plan_features', ['feature_id'], unique=False)
    op.create_index(op.f('ix_plan_features_plan_id'), 'plan_features', ['plan_id'], unique=False)

    # 2. Crear plan_limits
    op.create_table(
        'plan_limits',
        sa.Column('plan_id', sa.UUID(), nullable=False),
        sa.Column('limit_code', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_id', 'limit_code', name='uq_plan_limit')
    )
    op.create_index(op.f('ix_plan_limits_plan_id'), 'plan_limits', ['plan_id'], unique=False)

    # 3. Modificar plans: añadir columnas nuevas
    op.add_column('plans', sa.Column('code', sa.String(length=30), nullable=False))
    op.add_column('plans', sa.Column('currency_id', sa.UUID(), nullable=False))
    op.add_column('plans', sa.Column('interval', sa.String(length=20), nullable=False))
    op.add_column('plans', sa.Column('trial_days', sa.SmallInteger(), nullable=False))

    # 4. Quitar unique de name (constraint por defecto)
    op.drop_constraint('plans_name_key', 'plans', type_='unique')

    # 5. Index único en code
    op.create_index(op.f('ix_plans_code'), 'plans', ['code'], unique=True)

    # 6. FK a currencies (con nombre explícito)
    op.create_foreign_key(
        'plans_currency_id_fkey',
        'plans',
        'currencies',
        ['currency_id'],
        ['id'],
    )

    # 7. Quitar columnas viejas
    op.drop_column('plans', 'limits')
    op.drop_column('plans', 'features')
    op.drop_column('plans', 'currency')
    op.drop_column('plans', 'description')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Restaurar columnas viejas
    op.add_column('plans', sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('plans', sa.Column('currency', sa.VARCHAR(length=10), autoincrement=False, nullable=False))
    op.add_column('plans', sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.add_column('plans', sa.Column('limits', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True))

    # 2. Quitar FK a currencies (con nombre explícito)
    op.drop_constraint('plans_currency_id_fkey', 'plans', type_='foreignkey')

    # 3. Quitar index de code
    op.drop_index(op.f('ix_plans_code'), table_name='plans')

    # 4. Restaurar unique de name
    op.create_unique_constraint(
        'plans_name_key', 'plans', ['name'], postgresql_nulls_not_distinct=False
    )

    # 5. Quitar columnas nuevas
    op.drop_column('plans', 'trial_days')
    op.drop_column('plans', 'interval')
    op.drop_column('plans', 'currency_id')
    op.drop_column('plans', 'code')

    # 6. Borrar plan_limits
    op.drop_index(op.f('ix_plan_limits_plan_id'), table_name='plan_limits')
    op.drop_table('plan_limits')

    # 7. Borrar plan_features
    op.drop_index(op.f('ix_plan_features_plan_id'), table_name='plan_features')
    op.drop_index(op.f('ix_plan_features_feature_id'), table_name='plan_features')
    op.drop_table('plan_features')