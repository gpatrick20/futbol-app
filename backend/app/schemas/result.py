from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TeamMatchResultCreate(BaseModel):
    team_id: UUID
    goals_for: int = Field(ge=0)
    goals_against: int = Field(ge=0)
    result: str = Field(pattern="^(win|loss|draw)$")

    @model_validator(mode="after")
    def validate_result(self):
        if self.result == "win" and self.goals_for <= self.goals_against:
            raise ValueError("Un resultado ganado requiere más goles a favor que en contra")
        if self.result == "loss" and self.goals_for >= self.goals_against:
            raise ValueError("Un resultado perdido requiere menos goles a favor que en contra")
        if self.result == "draw" and self.goals_for != self.goals_against:
            raise ValueError("Un empate requiere la misma cantidad de goles")
        return self


class TeamMatchResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    match_id: UUID
    team_id: UUID
    goals_for: int
    goals_against: int
    result: str
