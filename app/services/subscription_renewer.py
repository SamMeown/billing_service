import logging
from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import Depends

from models.message import Message
from msg.message_broker import MessageBroker, get_message_broker
from msg.events_reporter import EventsReporter
from db.db_models import ModelUsers, ModelUserSubscription, STATUS
from db.database import SessionLocal


renewer_logger = logging.getLogger('SubscriptionRenewer')


class SubscriptionRenewer:
    def __init__(self,
                 msg_broker: MessageBroker,
                 events_reporter: EventsReporter):
        self.msg_broker = msg_broker
        self.events_reporter = events_reporter

    async def check_subscriptions(self):
        with SessionLocal() as db:
            subscriptions_data = db.query(
                ModelUsers,
                ModelUserSubscription
            ).filter(
                ModelUsers.user_subscription_id == ModelUserSubscription.id
            ).filter(
                ModelUserSubscription.status != STATUS.EXPIRED
            ).filter(
                ModelUserSubscription.expires < datetime.utcnow()
            ).all()
            renewer_logger.error('Subscriptions to further check: %s', subscriptions_data)
            for user, user_subscription in subscriptions_data:
                if (not user_subscription.recurring
                        or user_subscription.expires+timedelta(days=user_subscription.grace_days) < datetime.utcnow()):
                    user_subscription.status = STATUS.EXPIRED
                    db.commit()
                    await self.events_reporter.report_status_change_async(str(user.id),
                                                                          {'type': 'subscription',
                                                                           'id': str(user_subscription.sub_id)},
                                                                          user_subscription.subscription.price,
                                                                          'expired')
                elif user_subscription.status == STATUS.ACTIVE:
                    user_subscription.status = STATUS.NEEDS_PAYMENT
                    db.commit()
                    await self.msg_broker.enqueue_for_renewal(Message(task='subscription_renew',
                                                                      user_id=user.id,
                                                                      extra={'is_initial': True}))
                elif user_subscription.status == STATUS.NEEDS_PAYMENT:
                    await self.msg_broker.enqueue_for_renewal(Message(task='subscription_renew',
                                                                      user_id=user.id,
                                                                      extra={'is_initial': False}))
                elif user_subscription.status == STATUS.NEEDS_PAYMENT_AUTH:
                    # just waiting for the user to authorize payment
                    renewer_logger.error('Subscription of user %s is waiting for user auth', user)
