from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MatchEventCreate(BaseModel):
    player_id: UUID
    event_type: str = Field(pattern="^(goal|assist|mvp)$")
    minute: int | None = Field(default=None, ge=0)


class MatchEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    player_id: UUID
    event_type: str
    minute: int | None
    created_at: datetime
