import uvicorn
import logging
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin
from .api.v1.server import server, subscriptions, payments, users, user_subscriptions, movies, user_movies
from .models.admin_models import SubscriptionAdmin, MovieAdmin, UsersAdmin, UserSubscriptionAdmin
from .db.database import engine

app = FastAPI(
    title="Billing MVP",
    description='Billing API MVP using Stripe',
    docs_url='/api/openapi',
    openapi_url='/mvp/openapi.json',
)

admin = Admin(app, engine=engine)

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

app.include_router(
    users.router,
    prefix="",
    tags=[
        "Users",
    ],
)

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

#app.mount('/static', StaticFiles(directory='static'), name='static')

#static_dir = "app/api/v1/client/"
static_dir = "/app/app/api/v1/client/"
app.mount('/', StaticFiles(directory=static_dir, html=True), name='static')

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, log_level=logging.DEBUG, debug=True)
