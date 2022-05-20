import os

from pydantic import BaseSettings, Field


class DBsecret(BaseSettings):
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    name: str = Field(..., env="POSTGRES_DB")
    host: str = Field(..., env="POSTGRES_HOST")
    port: str = Field(..., env="POSTGRES_PORT")

    class Config:
        case_sentive = False
        env_file = '.env'


POSTGRES_DSN = DBsecret().dict()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RABBITMQsecret(BaseSettings):
    host: str = Field(..., env="RABBITMQ_BILLING_HOST")
    port: int = Field(..., env="RABBITMQ_BILLING_PORT")
    user: str = Field(..., env="RABBITMQ_DEFAULT_USER")
    password: str = Field(..., env="RABBITMQ_DEFAULT_PASS")

    class Config:
        case_sentive = False
        env_file = '.env'


RABBITMQ_DSN = RABBITMQsecret().dict()


class KAFKAsecret(BaseSettings):
    host: str = Field(..., env="UGC_KAFKA_HOST")
    port: int = Field(..., env="UGC_KAFKA_PORT")

    class Config:
        case_sentive = False
        env_file = '.env'


KAFKA_DSN = KAFKAsecret().dict()

KAFKA_CLIENT_METADATA_TTL = 30
KAFKA_BILLING_REPORT_TOPIC = 'user.v1.purchase_status_changed'

SUBSCRIPTIONS_CHECK_INTERVAL = 3600
