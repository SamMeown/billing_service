from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import POSTGRES_DSN


SQLALCHEMY_DATABASE_URL = f'postgresql://{POSTGRES_DSN.get("user")}:{POSTGRES_DSN.get("password")}@{POSTGRES_DSN.get("host")}:{POSTGRES_DSN.get("port")}/{POSTGRES_DSN.get("name")}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()
