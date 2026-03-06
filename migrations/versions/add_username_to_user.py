"""add username to user

Revision ID: 20260306_add_username
Revises: 2f9ac99a21d0
Create Date: 2026-03-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '20260306_add_username'
down_revision = '2f9ac99a21d0'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('username', sa.String(), nullable=False, server_default=''))
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_column('user', 'username')