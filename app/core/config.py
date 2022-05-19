import os

from pydantic import BaseSettings, Field, SecretStr


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

RABBITMQ_DSN = {
    'host': os.environ.get('RABBITMQ_BILLING_HOST', 'localhost'),
    'port': int(os.environ.get('RABBITMQ_BILLING_PORT', 5672)),
    'user': os.environ.get('RABBITMQ_DEFAULT_USER'),
    'password': os.environ.get('RABBITMQ_DEFAULT_PASS')
}

KAFKA_DSN = {
    'host': os.getenv('UGC_KAFKA_HOST', '127.0.0.1'),
    'port': int(os.getenv('UGC_KAFKA_PORT', 9092)),
}
KAFKA_CLIENT_METADATA_TTL = 30
KAFKA_BILLING_REPORT_TOPIC = 'user.v1.purchase_status_changed'

SUBSCRIPTIONS_CHECK_INTERVAL = 3600
