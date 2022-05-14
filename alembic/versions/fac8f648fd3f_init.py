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


def upgrade():
    op.create_table(
        'subscriptions',

        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4()),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String),
        sa.Column('price', sa.Integer, nullable=False, default=0),
        sa.Column('period', sa.Integer, default=30),
        sa.Column('type', sa.String, nullable=False, default='subscription'),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow,
                  onupdate=datetime.utcnow)
    ),

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4()),
        sa.Column('stripe_cus_id', UUID(as_uuid=True), nullable=False, default=uuid.uuid4()),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow,
                  onupdate=datetime.utcnow)
    ),

    op.create_table(
        'user_subscriptions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
        sa.Column('sub_id', UUID(as_uuid=True), ForeignKey('subscriptions.id')),
        sa.Column('recurring', sa.Boolean, default=True),
        sa.Column('status', sa.String, nullable=False, default="ACTIVE"),
        sa.Column('grace_days', sa.Integer, default=3),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow,
                  onupdate=datetime.utcnow)
    ),

    op.create_table(
        'movies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4()),
        sa.Column('name', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String),
        sa.Column('price', sa.Integer, nullable=False, default=0),
        sa.Column('type', sa.String, nullable=False, default='movie'),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow,
                  onupdate=datetime.utcnow)
    ),
    op.create_table(
        'user_movies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), ForeignKey('users.id')),
        sa.Column('movie_id', UUID(as_uuid=True), ForeignKey('movies.id')),
        sa.Column('status', sa.String, nullable=False, default="ACTIVE"),

        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_on', sa.DateTime(timezone=True), nullable=False, default=datetime.utcnow,
                  onupdate=datetime.utcnow)
    ),


def downgrade():
    op.drop_table('subscriptions'),
    op.drop_table('users')
    op.drop_table('user_subscriptions')
    op.drop_table('movies')
    op.drop_table('user_movies')
