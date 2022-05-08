from typing import Optional
from app.models._base import BaseModel, Field
from datetime import datetime, timedelta, date


class UserSubscriptionBase(BaseModel):
    user_id: Optional[str] = Field(
        default="",
        description="Id_user in tablename users")
    sub_id: Optional[str] = Field(
        default="",
        description="Id_subscription in tablename subscriptions")
    expired_time: Optional[datetime] = Field(
        default=datetime.now(),
        description="Expired time subscription")

    class Config:
        title = "Basic buy subscription model"
        schema_extra = {
            "example": {
                **BaseModel.Config.schema_extra["example"],
                "user_id": "364101df-2c13-4a39-9394-6a03e12ee6fd",
                "sub_id": "92b21482-4048-40cf-90dc-3028b723b137",
                "expired_time": "2022-05-08T07:42:44.670721+00:00"
            },
        }
