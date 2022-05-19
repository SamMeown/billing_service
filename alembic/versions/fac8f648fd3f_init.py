"""init

Revision ID: fac8f648fd3f
Revises: 
Create Date: 2022-05-03 17:44:41.824584

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey

import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'fac8f648fd3f'
down_revision = None
branch_labels = None
depends_on = None

from sqlalchemy.sql import func
from fastapi_utils.guid_type import GUID, GUID_SERVER_DEFAULT_POSTGRESQL


def upgrade():
    op.create_table(
        'subscriptions',

        sa.Column('id', GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String),
        sa.Column('price', sa.Integer, nullable=False, server_default='0'),
        sa.Column('period', sa.Integer, nullable=False, server_default='30'),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now(),
                  onupdate=datetime.utcnow)
    ),

    op.create_table(
        'user_subscriptions',

        sa.Column('id', GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL),
        sa.Column('sub_id', UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False),
        sa.Column('recurring', sa.Boolean, nullable=False, server_default='True'),
        sa.Column('status', sa.String, nullable=False, server_default='ACTIVE'),
        sa.Column('grace_days', sa.Integer, nullable=False, server_default='3'),
        sa.Column('expires', sa.DateTime(), nullable=False),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now(),
                  onupdate=datetime.utcnow)
    ),
    op.create_index(op.f('ix_user_subscriptions_expires'), 'user_subscriptions', ['expires'], unique=False),

    op.create_table(
        'users',

        sa.Column('id', GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL),
        sa.Column('stripe_cus_id', sa.String(256), nullable=True),
        sa.Column('user_subscription_id', UUID(as_uuid=True), ForeignKey('user_subscriptions.id'), nullable=True,
                  unique=True),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now(),
                  onupdate=datetime.utcnow)
    ),

    op.create_table(
        'movies',

        sa.Column('id', GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String),
        sa.Column('price', sa.Integer, nullable=False, server_default='0'),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now(),
                  onupdate=datetime.utcnow)
    ),
    op.create_table(
        'user_movies',

        sa.Column('id', GUID, primary_key=True, server_default=GUID_SERVER_DEFAULT_POSTGRESQL),
        sa.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
        sa.Column('movie_id', UUID(as_uuid=True), ForeignKey('movies.id')),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, server_default=func.now(),
                  onupdate=datetime.utcnow)
    ),


def downgrade():
    op.drop_index(op.f('ix_user_subscriptions_expires'), table_name='user_subscriptions')
    op.drop_table('user_subscriptions')
    op.drop_table('user_movies')
    op.drop_table('subscriptions')
    op.drop_table('users')
    op.drop_table('movies')
