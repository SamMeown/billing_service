import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RABBITMQ_DSN = {
    'host': os.environ.get('RABBITMQ_BILLING_HOST', 'localhost'),
    'port': int(os.environ.get('RABBITMQ_BILLING_PORT', 5672)),
    'user': os.environ.get('RABBITMQ_DEFAULT_USER'),
    'password': os.environ.get('RABBITMQ_DEFAULT_PASS')
}
