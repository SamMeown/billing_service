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


# Added m2m tables for user and movies just to try admin features
user_movie = Table(
    'user_movie',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('movie_id', UUID(as_uuid=True), ForeignKey('movies.id'), primary_key=True)
)


class ModelMovies(Base):
    __tablename__ = 'movies'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, default=0)
    description = Column(String, nullable=False)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'Movie {self.name}'


class ModelSubscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, default=12)
    description = Column(String, nullable=False)
    period = Column(Integer, default=30)
    recurring = Column(Boolean, default=True)
    status = Column(Enum(STATUS), default=STATUS.ACTIVE)
    grace_days = Column(Integer, default=3)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f'Subs. {self.name} - {self.price}'


# временная таблица, пока в проект не добавлена таблица users из Auth
class ModelUsers(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    subscriptions = relationship("ModelUserSubscription", back_populates='user')
    movies = relationship('ModelMovies', secondary=user_movie)

    def __str__(self):
        return f'User {self.name}<{self.email}>'


class ModelUserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    sub_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'))
    expired_time = Column(DateTime(), default=datetime.utcnow)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('ModelUsers', back_populates='subscriptions')
    subscription = relationship('ModelSubscriptions')
