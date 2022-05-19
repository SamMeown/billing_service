import asyncio
import os
import sys

app_root = os.path.dirname(os.path.abspath(__file__))
app_root_parent = os.path.dirname(app_root)
sys.path.append(app_root_parent)
import logging

import uvicorn
from aiokafka import AIOKafkaProducer
from kafka import KafkaProducer
from aio_pika import connect
from api.v1.server import (movies, payments, server, subscriptions,
                           user_movies, user_subscriptions, users)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models.admin_models import (MovieAdmin, SubscriptionAdmin, UsersAdmin,
                                 UserSubscriptionAdmin)
from sqladmin import Admin

from core import config
from db.database import engine
from msg import rabbit, kafka
from msg.message_broker import get_message_broker
from msg.events_reporter import get_events_reporter
from services.subscription_renewer import SubscriptionRenewer


app = FastAPI(
    title="Billing MVP",
    description='Billing API MVP using Stripe',
    docs_url='/api/openapi',
    openapi_url='/mvp/openapi.json',
)

admin = Admin(app, engine=engine)


async def check(subscriptions_renewer: SubscriptionRenewer, interval: int):
    while True:
        await subscriptions_renewer.check_subscriptions()
        await asyncio.sleep(interval)


@app.on_event('startup')
async def startup():
    rabbit.rabbit = await connect('ampq://{user}:{password}@{host}:{port}'.format(**config.RABBITMQ_DSN))
    kafka.kafka.producer_sync = KafkaProducer(bootstrap_servers=['{host}:{port}'.format(**config.KAFKA_DSN)])
    kafka.kafka.producer_async = AIOKafkaProducer(bootstrap_servers='{host}:{port}'.format(**config.KAFKA_DSN),
                                                  metadata_max_age_ms=config.KAFKA_CLIENT_METADATA_TTL * 1000)
    await kafka.kafka.producer_async.start()

    msg_broker = await get_message_broker(await rabbit.get_rabbit())
    events_reporter = await get_events_reporter(await kafka.get_kafka())
    subscription_renewer = SubscriptionRenewer(msg_broker, events_reporter)
    asyncio.create_task(check(subscription_renewer, config.SUBSCRIPTIONS_CHECK_INTERVAL))


@app.on_event('shutdown')
async def shutdown():
    await rabbit.rabbit.close()
    await kafka.kafka.producer_async.stop()


admin.register_model(SubscriptionAdmin)
admin.register_model(MovieAdmin)
admin.register_model(UsersAdmin)
admin.register_model(UserSubscriptionAdmin)


app.include_router(
    server.router,
    prefix="",
    tags=[
        "Server",
    ],
)

app.include_router(
    subscriptions.router,
    prefix="",
    tags=[
        "Subscriptions",
    ],
)

app.include_router(
    payments.router,
    prefix="",
    tags=[
        "Payments",
    ],
)

# app.include_router(
#     users.router,
#     prefix="",
#     tags=[
#         "Users",
#     ],
# )

app.include_router(
    user_subscriptions.router,
    prefix="",
    tags=[
        "User_subscriptions",
    ],
)
app.include_router(
    movies.router,
    prefix="",
    tags=[
        "Movies",
    ],
)

app.include_router(
    user_movies.router,
    prefix="",
    tags=[
        "User_movies",
    ],
)


admin_static_dir = os.path.join(app_root_parent, 'static')
app.mount('/static', StaticFiles(directory=admin_static_dir), name='static')

static_dir = os.path.join(app_root, 'api/v1/client/')
app.mount('/', StaticFiles(directory=static_dir, html=True), name='static')


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, log_level=logging.DEBUG, debug=True)
