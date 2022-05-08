import stripe
from fastapi import FastAPI

from .api.v1 import subscription, buy

app: FastAPI = FastAPI(
    title='Api',
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(
    subscription.router,
    prefix="/api/v1/subscription",
    tags=[
        "Subscription",
    ],
)

app.include_router(
    buy.router,
    prefix="/api/v1/buy",
    tags=[
        "Buy subscription",
    ],
)



@app.get('/')
def index():
    return dict(message="Hello world")



