from typing import Optional

from aio_pika import Connection


rabbit: Optional[Connection] = None


async def get_rabbit() -> Connection:
    return rabbit
