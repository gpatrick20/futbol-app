import uuid

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TeamMatchResult(Base):
    __tablename__ = "team_match_results"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "team_id", name="uq_team_match_results_match_team"
        ),
        CheckConstraint(
            "goals_for >= 0", name="ck_team_match_results_goals_for"
        ),
        CheckConstraint(
            "goals_against >= 0", name="ck_team_match_results_goals_against"
        ),
        CheckConstraint(
            "result IN ('win', 'loss', 'draw')",
            name="ck_team_match_results_result",
        ),
        CheckConstraint(
            "(result = 'win' AND goals_for > goals_against) OR "
            "(result = 'loss' AND goals_for < goals_against) OR "
            "(result = 'draw' AND goals_for = goals_against)",
            name="ck_team_match_results_result_consistency",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False
    )
    goals_for: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    goals_against: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    result: Mapped[str] = mapped_column(String(10), nullable=False)


Index("ix_team_match_results_team_id", TeamMatchResult.team_id)
