import os


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
