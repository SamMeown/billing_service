from typing import Optional

from app.models._base import BaseModelID, Field
from pydantic import BaseModel as PydanticBaseModel


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
    type: Optional[str] = Field(
        default="subscription",
        description="Subscription type")

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                "name": "1-Month Subscription",
                "description": "Subscription for 4 people",
                "price": 0,  # $
                "period": 30,  #days
                "type": "subscription"
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
