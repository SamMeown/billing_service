import os
import sys
app_root = os.path.dirname(os.path.abspath(__file__))
app_root_grandparent = os.path.dirname(os.path.dirname(app_root))
sys.path.append(app_root_grandparent)
import time
import json
import logging
import enum
from datetime import timedelta

import backoff
import pika
import stripe
from stripe import error as stripe_error
from pika.adapters.blocking_connection import BlockingChannel
from pika import exceptions as pika_exceptions
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session, query
from kafka import KafkaProducer

from core import config
from db.db_models import ModelUsers, ModelSubscriptions, STATUS
from db.database import SessionLocal


logging.basicConfig(level=logging.INFO)

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')


kafka_producer = KafkaProducer(bootstrap_servers=['localhost:9092'])


def process_msg(ch: BlockingChannel, method: pika.spec.Basic.GetOk, message_body: bytes):
    msg = json.loads(message_body.decode('utf-8'))
    renew_subscription(msg['user_id'], True)
    ch.basic_ack(delivery_tag=method.delivery_tag)


class PaymentResult(enum.Enum):
    SUCCESS = 0,
    ERROR_AUTH = 1,
    ERROR_OTHER = 2


def renew_subscription(user_id, is_initial=True):
    with SessionLocal() as session:
        try:
            user = session.query(ModelUsers).filter_by(id=user_id).first()
            if not user:
                # error: user not found
                logging.error('user not found')
                return
            user_subscription = user.subscription
            if not user_subscription:
                # error: no subscription
                logging.error('user doesn\'t have subscription')
                return
            if not user_subscription.recurring or user_subscription.status != STATUS.NEEDS_PAYMENT:
                logging.info('user subscription doesn\'t need renewal (status: %s, recurring: %s)',
                             user_subscription.status.name, user_subscription.recurring)
                return
            if not user.stripe_cus_id:
                # error: no stripe customer id
                logging.error('no stripe customer id')
                return

            payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_cus_id,
                type='card'
            )

            order_amount = user_subscription.subscription.price * 100
            intent = stripe.PaymentIntent.create(
                amount=order_amount,
                currency='usd',
                payment_method=payment_methods['data'][0]['id'],
                customer=user.stripe_cus_id,
                confirm=True,
                off_session=True
            )
            if intent['status'] == 'succeeded':
                user_subscription.status = STATUS.ACTIVE
                user_subscription.expires += timedelta(days=user_subscription.subscription.period)
                session.commit()
                report_payment_result(PaymentResult.SUCCESS, user_id, user_subscription.subscription)
            else:
                logging.error('failed to withdraw subscription renewal price with intent status: %s', intent['status'])
        except sqlalchemy_exc.DataError as e:
            logging.error(e)
        except stripe_error.InvalidRequestError as e:
            logging.error('Stripe Request Error: %s', e.user_message)
        except stripe_error.CardError as e:
            # off-session card errors
            # err = e.error
            logging.error('failed to withdraw subscription renewal price with error code: %s', e.code)
            if not is_initial:
                return
            if e.code == 'authentication_required':
                user_subscription.status = STATUS.NEEDS_PAYMENT_AUTH
                session.commit()
                report_payment_result(PaymentResult.ERROR_AUTH, user_id, user_subscription.subscription)
            else:
                report_payment_result(PaymentResult.ERROR_OTHER, user_id, user_subscription.subscription)


def report_payment_result(result: PaymentResult, user_id, subscription: ModelSubscriptions):
    report_topic = 'user.v1.purchase_status_changed'
    report = {
        'user_id': user_id,
        'item': {
            'type': 'subscription',
            'id': str(subscription.id)
        },
        'amount': subscription.price,
    }
    if result == PaymentResult.ERROR_AUTH:
        # Bring the customer back on-session to authenticate the purchase
        # by sending an email or app notification to let them know
        # the off-session purchase failed
        # Probably we can save the PM ID and client_secret to authenticate the purchase later
        # without asking your customers to re-enter their details
        # err.payment_method.id, err.payment_intent.client_secret, err.payment_method.card
        report['status'] = 'awaits_renewal'
        report['sub_status'] = 'awaits_auth'
    elif result == PaymentResult.ERROR_OTHER:
        # The card was declined for other reasons (e.g. insufficient funds)
        # Bring the customer back on-session by sending him a message asking him for a new payment method
        report['status'] = 'awaits_renewal'
        report['sub_status'] = 'awaits_card'
    else:
        report['status'] = 'renewed'
        logging.debug('success!!!')

    kafka_producer.send(report_topic,
                        value=json.dumps(report).encode('utf-8'),
                        key=user_id.encode('utf-8'))


def init_message_queue(mq_dsn: dict, exchange: str) -> (pika.BlockingConnection, BlockingChannel, list[str]):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=mq_dsn['host'],
            port=mq_dsn['port'],
            credentials=pika.PlainCredentials(mq_dsn['user'], mq_dsn['password']),
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='direct')

    channel.basic_qos(prefetch_count=1)

    queue_topic = 'subscription_renewal'
    queue = '{exchange}.{topic}'.format(exchange=exchange, topic=queue_topic)

    channel.queue_declare(queue=queue, durable=True)
    channel.queue_bind(exchange=exchange, queue=queue, routing_key=queue_topic)

    return connection, channel, queue


@backoff.on_exception(backoff.expo, pika_exceptions.AMQPConnectionError,
                      max_tries=config.RABBITMQ_CONNECTION_RETRIES, jitter=backoff.random_jitter)
def run_subscription_renew_loop():
    mq_connection, mq_channel, mq_queue = init_message_queue(config.RABBITMQ_DSN, config.PAYMENT_EXCHANGE)
    try:
        while True:
            m_frame, _, msg_body = mq_channel.basic_get(mq_queue)
            if m_frame:
                process_msg(mq_channel, m_frame, msg_body)
            else:
                # Queue is empty. Sleeping...
                logging.debug('Queue is empty. Sleeping...')
                time.sleep(config.EMPTY_QUEUES_RETRY_TIMEOUT)
    finally:
        mq_connection.close()


if __name__ == '__main__':
    run_subscription_renew_loop()
