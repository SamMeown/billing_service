import uuid
from datetime import datetime, timedelta
import enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, Table, Boolean, Enum
from sqlalchemy.orm import relationship

from app.db.database import Base


class STATUS(enum.Enum):
    ACTIVE = "ACTIVE"
    NEEDS_PAYMENT = "NEEDS_PAYMENT"
    EXPIRED = "EXPIRED"


class ModelMovies(Base):
    __tablename__ = 'movies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    price = Column(Integer, default=0, nullable=False)
    type = Column(String, default='movie', nullable=False)

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
    type = Column(String, default='subscription', nullable=False)

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'Subs. {self.name} - {self.price}'


class ModelUsers(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    stripe_cus_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    subscriptions = relationship("ModelUserSubscription", back_populates='user')
    movies = relationship('ModelUserMovies', back_populates='user')

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'User {self.id}<{self.stripe_cus_id}>'


class ModelUserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    sub_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'), nullable=False)
    recurring = Column(Boolean, default=True, nullable=False)
    status = Column(Enum(STATUS), default=STATUS.ACTIVE, nullable=False)
    grace_days = Column(Integer, default=3, nullable=False)
    user = relationship('ModelUsers', back_populates='subscriptions')
    subscription = relationship('ModelSubscriptions')

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelUserMovies(Base):
    __tablename__ = 'user_movies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    movie_id = Column(UUID(as_uuid=True), ForeignKey('movies.id'), nullable=False)
    status = Column(Enum(STATUS), default=STATUS.ACTIVE, nullable=False)
    user = relationship('ModelUsers', back_populates='movies')
    movie = relationship('ModelMovies')

    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)


