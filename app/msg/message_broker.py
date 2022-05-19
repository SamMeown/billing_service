import logging
from typing import Optional

from fastapi import Depends
from aio_pika import Connection, ExchangeType, Message as RabbitMessage, DeliveryMode

from models.message import Message
from msg.rabbit import get_rabbit


broker_logger = logging.getLogger('MessageBroker')


class MessageBroker:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.msg_payments_exchange = None

    async def init_exchanges(self):
        channel = await self.connection.channel()
        self.msg_payments_exchange = await channel.declare_exchange('payments', ExchangeType.DIRECT)

    async def enqueue_for_renewal(self, message: Message):
        rabbit_msg = self._rabbit_msg(message)
        await self.msg_payments_exchange.publish(rabbit_msg, routing_key='subscription_renewal')

    @staticmethod
    def _rabbit_msg(message: Message) -> RabbitMessage:
        message_dump = message.json().encode()
        return RabbitMessage(message_dump,
                             delivery_mode=DeliveryMode.PERSISTENT)


msg_broker_instance: Optional[MessageBroker] = None


async def get_message_broker(connection: Connection = Depends(get_rabbit)) -> MessageBroker:
    global msg_broker_instance
    if not msg_broker_instance:
        msg_broker_instance = MessageBroker(connection)
        await msg_broker_instance.init_exchanges()

    return msg_broker_instance
