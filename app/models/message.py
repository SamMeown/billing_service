from typing import Optional
from uuid import UUID

from pydantic import Field

from models._base import BaseModelAPI


class Message(BaseModelAPI):
    task: str = Field(..., description='Task name')
    user_id: UUID = Field(..., description='Id of the user')
    extra: Optional[dict] = Field(None, description='Additional task info')
