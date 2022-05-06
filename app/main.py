import stripe
from fastapi import FastAPI
from .api.v1 import  subscription


app: FastAPI = FastAPI(
    title='Api',
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(
    subscription.router,
    prefix="/api/v1/subscriptions",
    tags=[
        "subscriptions",
    ],
)


@app.get('/')
def index():
    return dict(message="Hello world")



