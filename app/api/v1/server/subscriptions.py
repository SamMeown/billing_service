from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelSubscriptions
from app.models.subscriptions import SubscriptionBase

router = APIRouter()
object = 'subscription'
import enum


class STATUS(enum.Enum):
    ACTIVE = "ACTIVE"
    NEEDS_PAYMENT = "NEEDS_PAYMENT"
    EXPIRED = "EXPIRED"


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
        id: Optional[str] = Query(default=None, description=f"A unique {object} id"),
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response


@router.post("/subscriptions/create")
def create(
        name: Optional[str] = Query(default=None, description=f"A unique {object} name"),
        description: Optional[str] = Query(default=None, description="Full description"),
        period: Optional[int] = Query(default=30, description=f"{object} days"),
        price: Optional[int] = Query(default=12, description=f"Full {object} price"),
        details: SubscriptionBase = {},
        db: Session = Depends(get_db)
) -> dict:
    if db.query(ModelSubscriptions).filter(ModelSubscriptions.name == name).first() is not None:
        return {
            "success": False,
            "response": f'The {object} already exists'
        }
    else:
        to_create = ModelSubscriptions(
            name=name,
            description=description,
            period=period,
            price=price
        )
        db.add(to_create)
        db.commit()
        return {
            "success": True,
            "response": to_create.id
        }


@router.put("/subscriptions/{id}/update")
async def update(
        id: Optional[str] = Query(default=None, description=f"A unique {object} id"),
        name: Optional[str] = Query(default=None, description=f"A unique {object} name"),
        description: Optional[str] = Query(default=None, description="Full description"),
        period: Optional[int] = Query(default=30, description=f"{object} days"),
        recurring: Optional[bool] = Query(default=True, description=f"Auto-renewal {object}"),
        status: str = Query("ACTIVE", enum=['ACTIVE', 'NEEDS_PAYMENT', 'EXPIRED']),
        grace_days: Optional[int] = Query(default=3, description=f"{object} price"),
        price: Optional[int] = Query(default=12, description=f"Full {object} price"),
        details: SubscriptionBase = {},
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        response.name = name
        response.description = description
        response.price = price
        response.period = period
        response.recurring = recurring
        response.status = status
        response.grace_days = grace_days
        db.add(response)
        db.commit()
        return {"response": id}


@router.delete("/subscriptions/{id}/delete", name='delete_buy')
def delete(
        id: Optional[str] = Query(default=None, description=f"A unique {object} id"),
        chargeback: Optional[bool] = Query(default=False, description=f"Chargeback of {object}"),
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        if chargeback is True:
            response.status = "EXPIRED"
        else:
            response.recurring = False
        db.add(response)
        db.commit()
        return {"response": response.id}
