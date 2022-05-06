from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.subscription import ModelSubscriptions
from app.models.subscriptions import SubscriptionBase
from app.models._base import BaseModel
from typing import Optional
from fastapi.param_functions import Query

router = APIRouter()


@router.post("/create")
async def create(
        name: Optional[str] = Query(
            default=None,
            description="A unique subscription name",
        ),
        description: Optional[str] = Query(
            default=None,
            description="Full description",
        ),
        details: SubscriptionBase = {},
        db: Session = Depends(get_db)
) -> dict:
    if db.query(ModelSubscriptions).filter(ModelSubscriptions.name == name).first() is not None:
        return {
            "success": False,
            "created_id": 'The subscription already exists'
        }
    else:
        to_create = ModelSubscriptions(
            name=name,
            description=description
        )
        db.add(to_create)
        db.commit()
        return {
            "success": True,
            "created_id": to_create.id
        }


@router.get(
    path="/{id}"
)
async def subscription_details(
    id: str,
    db: Session = Depends(get_db),
    details: BaseModel = {},
) -> dict:

    return db.query(ModelSubscriptions).filter(ModelSubscriptions.id == id).first()
