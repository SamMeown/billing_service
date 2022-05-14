from typing import Optional
from uuid import UUID, uuid4

from app.models._base import BaseModelID, Field


class UsersBase(BaseModelID):
    stripe_cus_id: UUID = Field(
        default_factory=uuid4,
        description="Entity id in stripe",
    )

    class Config:
        title = "Basic subscription model"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                "stripe_cus_id": uuid4(),

            }
        }
