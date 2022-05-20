import uuid
from datetime import datetime, timedelta
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, Boolean, Enum, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class STATUS(enum.Enum):
    ACTIVE = "ACTIVE"
    NEEDS_PAYMENT = "NEEDS_PAYMENT"
    NEEDS_PAYMENT_AUTH = "NEEDS_PAYMENT_AUTH"
    EXPIRED = "EXPIRED"


class ModelMovies(Base):
    __tablename__ = 'movies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String)
    price = Column(Integer, default=0, nullable=False)

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'Movie {self.name}'


class ModelSubscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    price = Column(Integer, default=0, nullable=False)
    period = Column(Integer, default=30, nullable=False)

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'Subs. {self.name} - {self.price}'


class ModelUsers(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    stripe_cus_id = Column(String(256), nullable=True, index=True)
    user_subscription_id = Column(UUID(as_uuid=True), ForeignKey('user_subscriptions.id'), nullable=True, unique=True,
                                  index=True)
    subscription = relationship("ModelUserSubscription", back_populates='users')
    movies = relationship('ModelMovies', secondary='user_movies')

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'User {self.id}<{self.stripe_cus_id}>'


class ModelUserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    sub_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    recurring = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(STATUS), default=STATUS.ACTIVE, nullable=False)
    expires = Column(DateTime(), nullable=False, index=True)
    grace_days = Column(Integer, default=3, nullable=False)
    users = relationship('ModelUsers', back_populates='subscription')
    subscription = relationship('ModelSubscriptions')

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('user_subscription_status_expires_idx', status, expires),
    )


class ModelUserMovies(Base):
    __tablename__ = 'user_movies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey('movies.id'), nullable=False)

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('user_movies_user_movie_unique_idx', user_id, movie_id, unique=True),
        Index('user_movies_movie_idx', movie_id)
    )
