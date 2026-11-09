from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    commune: str | None = Field(default=None, max_length=100)
    description: str | None = None


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    leader_id: UUID
    commune: str | None
    description: str | None
    created_at: datetime


class TeamMemberCreate(BaseModel):
    user_id: UUID
    role: str = Field(default="player", pattern="^(leader|player)$")


class TeamMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    team_id: UUID
    user_id: UUID
    role: str
    joined_at: datetime
