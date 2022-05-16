import os
import sys
app_root = os.path.dirname(os.path.abspath(__file__))
app_root_grandparent = os.path.dirname(os.path.dirname(app_root))
sys.path.append(app_root_grandparent)
print(sys.path)
import time
import json
import logging
import enum

import backoff
import pika
import stripe
from stripe import error as stripe_error
from pika.adapters.blocking_connection import BlockingChannel
from pika import exceptions as pika_exceptions
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy.orm import Session, query

from core import config
from db.db_models import ModelUsers, STATUS
from db.database import SessionLocal


logging.basicConfig(level=logging.INFO)


stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')


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
            if not (user_subscription := user.subscription):
                # error: no subscription
                logging.error('user doesn\'t have subscription')
                return
            if user_subscription.status != STATUS.NEEDS_PAYMENT:
                logging.info('user subscription doesn\'t need renewal (status: %s)', user_subscription.status.name)
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
                session.commit()
                report_payment_result(PaymentResult.SUCCESS)
            else:
                logging.error('failed to withdraw subscription renewal price with intent status: %s', intent['status'])
        except sqlalchemy_exc.DataError as e:
            logging.error(e)
        except stripe_error.InvalidRequestError as e:
            logging.error('Stripe Request Error: %s', e.user_message)
        except stripe_error.CardError as e:
            # off-session card errors
            err = e.error
            logging.error('failed to withdraw subscription renewal price with error code: %s', err.code)
            if not is_initial:
                return
            report_payment_result(
                PaymentResult.ERROR_AUTH if err.code == 'authentication_required' else PaymentResult.ERROR_OTHER
            )


def report_payment_result(result: PaymentResult):
    if result == PaymentResult.ERROR_AUTH:
        # Bring the customer back on-session to authenticate the purchase
        # by sending an email or app notification to let them know
        # the off-session purchase failed
        # Probably we can save the PM ID and client_secret to authenticate the purchase later
        # without asking your customers to re-enter their details
        # err.payment_method.id, err.payment_intent.client_secret, err.payment_method.card
        pass
    elif result == PaymentResult.ERROR_OTHER:
        # The card was declined for other reasons (e.g. insufficient funds)
        # Bring the customer back on-session by sending him a message asking him for a new payment method
        pass
    else:
        # success
        print('success!!!')
        pass


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
                print('Queue is empty. Sleeping...')
                time.sleep(config.EMPTY_QUEUES_RETRY_TIMEOUT)
    finally:
        mq_connection.close()


if __name__ == '__main__':
    run_subscription_renew_loop()
