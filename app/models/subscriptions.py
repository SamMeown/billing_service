from typing import Optional

from pydantic import BaseModel as PydanticBaseModel

from app.models._base import BaseModelID, Field


class SubscriptionBase(PydanticBaseModel):
    name: Optional[str] = Field(
        default="",
        description="Subscription name")
    description: Optional[str] = Field(
        default="",
        description="Subscription description")
    period: Optional[int] = Field(
        default=30,
        description="Subscription validity period (days)")
    price: Optional[int] = Field(
        default=0,
        description="Subscription price")

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                "name": "1-Month Subscription",
                "description": "Subscription for 4 people",
                "price": 0,  # $
                "period": 30  #days
            }
        }


class SubscriptionBaseID(SubscriptionBase, BaseModelID):
    class Config:
        title = "subscription model with id"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                **SubscriptionBase.Config.schema_extra["example"]
            }
        }
