"""Add Testimonial manual

Revision ID: a98ce549f1dd
Revises: 6d5b5ac0338d
Create Date: 2025-12-09 21:33:52.801590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a98ce549f1dd'
down_revision = '6d5b5ac0338d'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'testimonial' not in insp.get_table_names():
        op.create_table(
            'testimonial',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('city', sa.String(length=255)),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('rating', sa.Integer()),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'testimonial' in insp.get_table_names():
        op.drop_table('testimonial')
