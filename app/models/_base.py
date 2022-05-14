from uuid import UUID, uuid4

from orjson import dumps, loads
from pydantic import BaseModel as PydanticBaseModel, Field


def orjson_dumps(v, *, default) -> str:
    return dumps(v, default=default).decode()


class BaseModelID(PydanticBaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Entity id",
    )

    class Config:
        title = "Basic model"
        json_loads = loads
        json_dumps = orjson_dumps
        schema_extra = {
            "example": {
                "id": uuid4(),
            },
        }