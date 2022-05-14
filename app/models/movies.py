from typing import Optional

from app.models._base import BaseModelID, Field
from pydantic import BaseModel as PydanticBaseModel


class MovieBase(PydanticBaseModel):
    name: Optional[str] = Field(
        default="",
        description="Movie name")
    description: Optional[str] = Field(
        default="",
        description="Movie description")
    price: Optional[int] = Field(
        default=0,
        description="Movie price")

    class Config:
        title = "Basic movie model"
        schema_extra = {
            "example": {
                "name": "Around the World in 80 Days",
                "description": "Gentleman adventurer Phileas Fogg sets out on a quest to travel around the world and back home in a period of 80 days",
                "price": 0  # $
            }
        }


class SubscriptionBaseID(MovieBase, BaseModelID):
    class Config:
        title = "subscription model with id"
        schema_extra = {
            "example": {
                **BaseModelID.Config.schema_extra["example"],
                **MovieBase.Config.schema_extra["example"]
            }
        }
