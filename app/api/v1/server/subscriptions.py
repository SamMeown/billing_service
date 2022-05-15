from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from db.database import get_db
from db.db_models import ModelSubscriptions
from app.models.subscriptions import SubscriptionBase

router = APIRouter()
object = 'subscription'


@router.get('/subscriptions')
def fetch_subscriptions(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> list:
    _subscriptions = jsonable_encoder(paginate(db.query(ModelSubscriptions), params))
    if _subscriptions.get('items') is not None:
        return _subscriptions.get('items')
    return []


@router.get("/subscriptions/{id}")
def get_id(
        id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response


@router.post("/subscriptions")
def create(
        subscription: SubscriptionBase,
        db: Session = Depends(get_db)
) -> dict:
    if db.query(ModelSubscriptions).filter(ModelSubscriptions.name == subscription.name).first() is not None:
        return {"response": f'The {object} already exists'}
    else:
        to_create = ModelSubscriptions(
            name=subscription.name,
            description=subscription.description,
            period=subscription.period,
            price=subscription.price
        )
        db.add(to_create)
        db.commit()
        return {"response": to_create.id}


@router.put("/subscriptions/{id}")
async def update(
        id: Optional[str],
        subscription: SubscriptionBase,
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()

    if response is None:
        return {"response": f'The {object} not found'}
    else:
        response.name = subscription.name
        response.description = subscription.description
        response.price = subscription.price
        response.period = subscription.period

        db.add(response)
        db.commit()
        return {"response": id}
