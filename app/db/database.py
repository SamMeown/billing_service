import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

user = os.environ.get('POSTGRES_USER', 'local_user')
password = os.environ.get('POSTGRES_PASSWORD', '1234')
name = os.environ.get('POSTGRES_DB', 'postgres')
host = os.environ.get('POSTGRES_HOST', 'postgres')
port = os.environ.get('POSTGRES_PORT', 5432)


SQLALCHEMY_DATABASE_URL = f'postgresql://{user}:{password}@{host}:{port}/{name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()