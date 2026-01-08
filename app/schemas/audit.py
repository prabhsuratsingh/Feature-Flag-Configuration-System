from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: UUID
    actor: str
    entity_type: str
    entity_id: UUID
    action: str
    before: dict | None
    after: dict | None
    created_at: datetime

    class Config:
        orm_mode = True
