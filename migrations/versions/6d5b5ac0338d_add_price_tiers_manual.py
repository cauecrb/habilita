"""Add price tiers manual

Revision ID: 6d5b5ac0338d
Revises: 46dff0358b8f
Create Date: 2025-12-09 21:07:20.778573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d5b5ac0338d'
down_revision = '46dff0358b8f'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'price_tier' not in insp.get_table_names():
        op.create_table(
            'price_tier',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('lessons', sa.Integer(), nullable=False),
            sa.Column('price_min', sa.Numeric(10, 2), nullable=False),
            sa.Column('price_max', sa.Numeric(10, 2)),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        op.create_foreign_key(
            'fk_price_tier_user_id_user',
            'price_tier',
            'user',
            ['user_id'],
            ['id']
        )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'price_tier' in insp.get_table_names():
        op.drop_constraint('fk_price_tier_user_id_user', 'price_tier', type_='foreignkey')
        op.drop_table('price_tier')
