import stripe
from fastapi import FastAPI
from .api.v1 import test


app: FastAPI = FastAPI(
    title='Api',
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

app.include_router(
    test.test,
    prefix="/api/v1",
    tags=[
        "Kafka",
    ],
)

@app.get('/')
def index():
    return dict(message="Hello world")
