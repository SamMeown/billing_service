"""init

Revision ID: fac8f648fd3f
Revises: 
Create Date: 2022-05-03 17:44:41.824584

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, INTEGER, ForeignKey
import uuid
from datetime import datetime, timedelta

# revision identifiers, used by Alembic.
revision = 'fac8f648fd3f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subscriptions',

        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('price', sa.Integer, default=0),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False)
    ),
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    ),
    op.create_table(
        'user_subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('expired_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
        sa.Column('sub_id', UUID(as_uuid=True), ForeignKey('subscriptions.id')),
    )


def downgrade():
    op.drop_table('subscriptions'),
    op.drop_table('users')
    op.drop_table('user_subscriptions')
