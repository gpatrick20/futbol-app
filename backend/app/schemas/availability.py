from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AvailabilityVoteCreate(BaseModel):
    proposed_date: date
    proposed_time: time
    availability: str = Field(pattern="^(available|maybe|unavailable)$")


class AvailabilityVoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    user_id: UUID
    proposed_date: date
    proposed_time: time
    availability: str
