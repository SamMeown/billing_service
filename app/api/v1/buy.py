from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelUserSubscription, ModelUsers, ModelSubscriptions
from app.models.buy_subscription import UserSubscriptionBase
from datetime import datetime, timedelta, date

router = APIRouter()
object = 'buy'


@router.get("/")
async def get(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> dict:
    return {
        "success": True,
        "response": paginate(db.query(ModelUserSubscription), params)
    }


@router.get("/{id}")
async def get_id(
        id: Optional[str] = Query(
            default=None,
            description=f"A unique {object} id",
        ),
        db: Session = Depends(get_db),
) -> dict:
    response = db.query(ModelUserSubscription).filter(ModelUserSubscription.id == id).first()
    if response is None:
        return {
            "success": False,
            "response": f'The {object} not found'
        }
    else:
        return {
            "success": True,
            "response": response
        }


@router.post("/create")
async def create(
        user_email: Optional[str] = Query(
            default=None,
            description=f"A unique {object} name = email",
        ),
        subscription: Optional[str] = Query(
            default=None,
            description="Full description",
        ),
        expired_time: Optional[datetime] = Query(
            default=datetime.now() + timedelta(days=30),
            description=f"Full {object} price",
        ),
        details: UserSubscriptionBase = {},
        db: Session = Depends(get_db)

) -> dict:
    response = db.query(ModelUsers).filter(ModelUsers.email == user_email).first()
    if response is None:
        return {
            "success": False,
            "response": f'The user not found'
        }
    else:
        user_id = response.id
        response = db.query(ModelSubscriptions).filter(ModelSubscriptions.name == subscription).first()
        if response is None:
            return {
                "success": False,
                "response": f'The subscription not found'
            }
        else:
            sub_id = response.id
            to_create = ModelUserSubscription(
                user_id=user_id,
                sub_id=sub_id,
                expired_time=expired_time
            )
            db.add(to_create)
            db.commit()
            return {
                "success": True,
                "response": to_create.id
            }


@router.put("/update/{id}")
async def update(
        id: Optional[str] = Query(
            default=None,
            description=f"A unique {object} id",
        ),
        user_email: Optional[str] = Query(
            default=None,
            description=f"A unique {object} name = email",
        ),
        subscription: Optional[str] = Query(
            default=None,
            description="Full description",
        ),
        expired_time: Optional[datetime] = Query(
            default=datetime.now() + timedelta(days=30),
            description=f"Full {object} price",
        ),
        details: UserSubscriptionBase = {},
        db: Session = Depends(get_db)
) -> dict:
    response_data = db.query(ModelUserSubscription).filter(ModelUserSubscription.id == id).first()
    if response_data is None:
        return {
            "success": False,
            "response": f'The {object} not found'
        }
    else:
        response = db.query(ModelUsers).filter(ModelUsers.email == user_email).first()
        if response is None:
            return {
                "success": False,
                "response": f'The user not found'
            }
        else:
            user_id = response.id
            response = db.query(ModelSubscriptions).filter(ModelSubscriptions.name == subscription).first()
            if response is None:
                return {
                    "success": False,
                    "response": f'The subscription not found'
                }
            else:
                sub_id = response.id

                response_data.user_id = user_id
                response_data.sub_id = sub_id
                response_data.expired_time = expired_time
                db.add(response_data)
                db.commit()
                return {
                    "success": True,
                    "response": id
                }


@router.delete("/{id}", name='delete_buy')
def delete(
        id: Optional[str] = Query(
            default=None,
            description=f"A unique {object} id",
        ),
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelUserSubscription).filter(ModelUserSubscription.id == id).first()
    if response is None:
        return {
            "success": False,
            "response": f'The {object} not found'
        }
    else:
        db.query(ModelUserSubscription).filter(ModelUserSubscription.id == id).delete()
        db.commit()
        return {
            "success": True,
            "response": id
        }
