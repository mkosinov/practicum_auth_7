from uuid import UUID

from pydantic import BaseModel


class DeviceCreateSchema(BaseModel):
    user_id: UUID
    user_agent: str
