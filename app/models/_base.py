from uuid import UUID, uuid4

from orjson import dumps, loads
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


def orjson_dumps(v, *, default) -> str:
    return dumps(v, default=default).decode()


class BaseModelAPI(PydanticBaseModel):
    class Config:
        json_loads = loads
        json_dumps = orjson_dumps


class BaseModelID(BaseModelAPI):
    id: UUID = Field(
        default_factory=uuid4,
        description="Entity id",
    )

    class Config:
        title = "Basic model"
        schema_extra = {
            "example": {
                "id": uuid4(),
            },
        }
