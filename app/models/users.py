from typing import Optional
from uuid import UUID, uuid4

from app.models._base import BaseModelID, Field


class UsersBase(BaseModelID):
    stripe_cus_id: Optional[str] = Field(
        default=None,
        description="Stripe cus id")
    user_subscription_id: UUID = Field(
        default_factory=None,
        description="Entity id in stripe",
    )

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                "stripe_cus_id": "cus_LhkJS9IXtgcc7A",
                "user_subscription_id": uuid4(),

            }
        }
