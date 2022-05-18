from typing import Optional
import enum
from app.models._base import BaseModelID, Field
from pydantic import BaseModel as PydanticBaseModel
from uuid import UUID, uuid4


class STATUS(enum.Enum):
    ACTIVE = "ACTIVE"
    NEEDS_PAYMENT = "NEEDS_PAYMENT"
    EXPIRED = "EXPIRED"


class UserSubscriptionBase(PydanticBaseModel):
    sub_id: UUID = Field(
        default_factory=uuid4,
        description="Foreign key in the table subscriptions")
    recurring: Optional[bool] = Field(
        default=True,
        description="Auto-renewal payments")
    status: Optional[str] = Field(
        default=STATUS.ACTIVE,
        description="Payments status")
    grace_days: Optional[int] = Field(
        default=3,
        description="Extra days for renewal subscription")

    class Config:
        title = "Basic payments model"
        schema_extra = {
            "example": {
                "sub_id": "b943812d-fe0f-4627-9754-c2648d096478",
                "recurring":  True,  # auto-renewal payments
                "status": "ACTIVE",  # "choice(ACTIVE | NEEDS_PAYMENT | EXPIRED)",
                "grace_days": 3  # extra days for renewal subscription
            }
        }


class UserSubscriptionBaseID(UserSubscriptionBase, BaseModelID):
    class Config:
        title = "Payments model with id"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                **UserSubscriptionBase.Config.schema_extra["example"]
            }
        }