from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelUserSubscription
from app.models.user_subscriptions import UserSubscriptionBase

router = APIRouter()
object = 'user_subscriptions'


@router.get('/user_subscriptions')
def fetch_subscriptions(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> list:
    _user_subscriptions = jsonable_encoder(paginate(db.query(ModelUserSubscription), params))
    if _user_subscriptions.get('items') is not None:
        return _user_subscriptions.get('items')
    return []


@router.get("/user_subscriptions/{id}")
def get_id(
        id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelUserSubscription).filter(ModelUserSubscription.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response
