import uuid
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, String, Integer
from sqlalchemy.orm import relationship

from app.db.database import Base


class ModelSubscriptions(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, default=0)
    description = Column(String, nullable=False)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("ModelUserSubscription")


# временная таблица, пока в проект не добавлена таблица users из Auth
class ModelUsers(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    subscription = relationship("ModelUserSubscription")


class ModelUserSubscription(Base):
    __tablename__ = 'user_subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    sub_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.id'))
    expired_time = Column(DateTime(), default=datetime.utcnow)
    created_on = Column(DateTime(), default=datetime.utcnow)
    updated_on = Column(DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
