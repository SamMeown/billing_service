import stripe
from fastapi import FastAPI
from sqladmin import Admin
import uvicorn
import logging

from .api.v1 import subscription, buy
from .db.database import engine
from .admin.admin_models import SubscriptionAdmin, MovieAdmin, UsersAdmin, UserSubscriptionAdmin

app: FastAPI = FastAPI(
    title='Api',
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)

admin = Admin(app, engine=engine)

admin.register_model(SubscriptionAdmin)
admin.register_model(MovieAdmin)
admin.register_model(UsersAdmin)
admin.register_model(UserSubscriptionAdmin)


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



