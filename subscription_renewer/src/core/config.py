import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMPTY_QUEUES_RETRY_TIMEOUT = 10

PAYMENT_EXCHANGE = os.environ.get('BILLING_PAYMENT_EXCHANGE', 'payments')


from pydantic import BaseSettings, Field


class RABBITMQsecret(BaseSettings):
    host: str = Field(..., env="RABBITMQ_BILLING_HOST")
    port: int = Field(..., env="RABBITMQ_BILLING_PORT")
    user: str = Field(..., env="RABBITMQ_DEFAULT_USER")
    password: str = Field(..., env="RABBITMQ_DEFAULT_PASS")

    class Config:
        case_sentive = False
        env_file = '.env'


RABBITMQ_DSN = RABBITMQsecret().dict()

RABBITMQ_CONNECTION_RETRIES = 4
