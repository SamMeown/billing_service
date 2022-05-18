from typing import Optional
from dataclasses import dataclass

from aiokafka import AIOKafkaProducer
from kafka import KafkaProducer


@dataclass
class KafkaProvider:
    producer_async: Optional[AIOKafkaProducer] = None
    producer_sync: Optional[KafkaProducer] = None


kafka: KafkaProvider = KafkaProvider()


async def get_kafka() -> KafkaProvider:
    return kafka
