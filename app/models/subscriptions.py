from typing import Optional

from app.models._base import BaseModel, Field


class SubscriptionBase(BaseModel):
    name: Optional[str] = Field(
        default="",
        description="Subscription name")
    description: Optional[str] = Field(
        default="",
        description="Subscription description")
    period: Optional[int] = Field(
        default=30,
        description="Subscription days")
    recurring: Optional[bool] = Field(
        default=True,
        description="Auto-renewal subscription")
    status: Optional[str] = Field(
        default="active",
        description="Subscription status")
    grace_days: Optional[int] = Field(
        default=3,
        description="Subscription price")
    price: Optional[int] = Field(
        default=12,
        description="Extra days for renewal subscription")

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                **BaseModel.Config.schema_extra["example"],
                "name": "1-Month Subscription",
                "description": "Subscription for 4 people",
                "period": 30,  #days
                "recurring":  True,  #auto-renewal subscription
                "status": "choice(active | needs_payment | expired)",
                "grace_days": 3,  #extra days for renewal subscription
                "price": 12  #$
            }
        }
