from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from db.database import get_db
from db.db_models import ModelUsers
from app.models.users import UsersBase

router = APIRouter()
object = 'users'


@router.get('/users')
def fetch_subscriptions(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> list:
    _users = jsonable_encoder(paginate(db.query(ModelUsers), params))
    if _users.get('items') is not None:
        return _users.get('items')
    return []


@router.get("/users/{id}")
def get_id(
        id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelUsers).filter(ModelUsers.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response


@router.post("/users")
def create(
        users: UsersBase,
        db: Session = Depends(get_db)
) -> dict:
    if db.query(ModelUsers).filter(ModelUsers.id == users.id).first() is not None:
        return {"response": f'The {object} already exists'}
    else:

        to_create = ModelUsers(
            id=users.id,
            # stripe_cus_id=users.stripe_cus_id
            # user_subscription_id=users.user_subscription_id or None
        )
        db.add(to_create)
        db.commit()
        return {"response": to_create.id}


@router.put("/users/{id}")
async def update(
        id: Optional[str],
        stripe_cus_id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelUsers).filter(ModelUsers.id == id).first()

    if response is None:
        return {"response": f'The {object} not found'}
    else:
        response.id = id
        response.stripe_cus_id = stripe_cus_id

        db.add(response)
        db.commit()
        return {"response": id}
