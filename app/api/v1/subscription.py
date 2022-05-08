from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelSubscriptions
from app.models.subscriptions import SubscriptionBase

router = APIRouter()
object = 'subscription'


@router.get("/")
async def get(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> dict:
    return {
        "success": True,
        "response": paginate(db.query(ModelSubscriptions), params)
    }


@router.get("/{id}")
async def get_id(
        id: Optional[str] = Query(
            default=None,
            description=f"A unique {object} id",
        ),
        db: Session = Depends(get_db),
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
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
        name: Optional[str] = Query(
            default=None,
            description=f"A unique {object} name",
        ),
        description: Optional[str] = Query(
            default=None,
            description="Full description",
        ),
        price: Optional[int] = Query(
            default=0,
            description=f"Full {object} price",
        ),
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
            price=price
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
        name: Optional[str] = Query(
            default=None,
            description=f"A unique {object} name",
        ),
        description: Optional[str] = Query(
            default=None,
            description="Full description",
        ),
        price: Optional[int] = Query(
            default=0,
            description=f"Full {object} price",
        ),
        details: SubscriptionBase = {},
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {
            "success": False,
            "response": f'The {object} not found'
        }
    else:
        response.name = name
        response.description = description
        response.price = price
        db.add(response)
        db.commit()
        return {
            "success": True,
            "response": id
        }


@router.delete("/{id}")
def delete(
        id: Optional[str] = Query(
            default=None,
            description=f"A unique {object} id",
        ),
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
    if response is None:
        return {
            "success": False,
            "response": f'The {object} not found'
        }
    else:
        db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).delete()
        db.commit()
        return {
            "success": True,
            "response": id
        }
