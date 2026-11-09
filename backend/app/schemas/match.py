from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MatchCreate(BaseModel):
    format: str = Field(pattern="^(futbol5|futbol7|futbol11)$")
    venue_name: str = Field(min_length=2, max_length=150)
    address: str | None = None
    commune: str | None = Field(default=None, max_length=100)
    match_date: date | None = None
    start_time: time | None = None
    total_cost: Decimal | None = Field(default=None, ge=0)
    min_players: int = Field(default=0, ge=0)
    max_players: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_capacity(self):
        if self.max_players < self.min_players:
            raise ValueError("max_players debe ser mayor o igual que min_players")
        return self


class MatchDateUpdate(BaseModel):
    match_date: date
    start_time: time


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_by: UUID
    format: str
    venue_name: str
    address: str | None
    commune: str | None
    match_date: date | None
    start_time: time | None
    status: str
    total_cost: Decimal | None
    min_players: int
    max_players: int
    created_at: datetime


class MatchParticipantUpdate(BaseModel):
    status: str = Field(pattern="^(invited|confirmed|tentative|absent|substitute)$")


class MatchParticipantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    user_id: UUID
    status: str
    joined_at: datetime
