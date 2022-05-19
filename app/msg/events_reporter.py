import logging
import json
from typing import Optional

from fastapi import Depends

from msg.kafka import get_kafka, KafkaProvider
from core import config


reporter_logger = logging.getLogger('EventsReporter')


class EventsReporter:
    def __init__(self, kafka_provider: KafkaProvider):
        self.kafka = kafka_provider

    def report_status_change(
            self, user_id: str, item: dict, amount: int, status: str, sub_status: Optional[str] = None):
        topic, key, value = self._prepare_report(user_id, item, amount, status, sub_status)
        self.kafka.producer_sync.send(topic,
                                      value=json.dumps(value).encode('utf-8'),
                                      key=key.encode('utf-8'))

    async def report_status_change_async(
            self, user_id: str, item: dict, amount: int, status: str, sub_status: Optional[str] = None):
        topic, key, value = self._prepare_report(user_id, item, amount, status, sub_status)
        await self.kafka.producer_async.send_and_wait(topic=topic,
                                                      value=json.dumps(value).encode('utf-8'),
                                                      key=key.encode('utf-8'))

    @staticmethod
    def _prepare_report(
            user_id: str, item: dict, amount: int, status: str, sub_status: Optional[str]) -> (str, str, dict):
        topic = config.KAFKA_BILLING_REPORT_TOPIC
        key = user_id
        value = {
            'user_id': user_id,
            'item': item,
            'amount': amount,
            'status': status
        }
        if sub_status:
            value['sub_status'] = sub_status

        return topic, key, value


events_reporter_instance: Optional[EventsReporter] = None


async def get_events_reporter(kafka: KafkaProvider = Depends(get_kafka)) -> EventsReporter:
    global events_reporter_instance
    if not events_reporter_instance:
        events_reporter_instance = EventsReporter(kafka)

    return events_reporter_instance
