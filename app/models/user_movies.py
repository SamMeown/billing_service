import enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel as PydanticBaseModel

from app.models._base import BaseModelID, Field


class UserMovieBase(PydanticBaseModel):
    user_id: UUID = Field(
        default_factory=uuid4,
        description="Foreign key in the table users")
    movie_id: UUID = Field(
        default_factory=uuid4,
        description="Foreign key in the table movies")

    class Config:
        title = "Basic payments model"
        schema_extra = {
            "example": {
                "user_id": "a943812d-fe0f-4148-9754-c2648d07647c",
                "movie_id": "b943812d-fe0f-4627-9754-c2648d096478"
            }
        }


class UserSubscriptionBaseID(UserMovieBase, BaseModelID):
    class Config:
        title = "Payments model with id"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                **UserMovieBase.Config.schema_extra["example"]
            }
        }