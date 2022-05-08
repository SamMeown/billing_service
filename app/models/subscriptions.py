from typing import Optional
from app.models._base import BaseModel, Field


class SubscriptionBase(BaseModel):
    name: Optional[str] = Field(
        default="",
        description="Subscription name")
    description: Optional[str] = Field(
        default="",
        description="Subscription description")
    price: Optional[int] = Field(
        default=0,
        description="Subscription price")

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                **BaseModel.Config.schema_extra["example"],
                "name": "Yandex +",
                "description": "Subscription for 4 people",
                "price": 299
            },
        }
