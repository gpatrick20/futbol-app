import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint(
            "format IN ('futbol5', 'futbol7', 'futbol11')",
            name="ck_matches_format",
        ),
        CheckConstraint(
            "status IN ('proposed', 'voting', 'confirmed', 'full', 'cancelled', 'played')",
            name="ck_matches_status",
        ),
        CheckConstraint(
            "total_cost IS NULL OR total_cost >= 0",
            name="ck_matches_total_cost_non_negative",
        ),
        CheckConstraint(
            "min_players >= 0",
            name="ck_matches_min_players_non_negative",
        ),
        CheckConstraint(
            "max_players >= min_players",
            name="ck_matches_player_capacity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    venue_name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    commune: Mapped[str | None] = mapped_column(String(100), nullable=True)
    match_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default="proposed", nullable=False
    )
    total_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    min_players: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    max_players: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    participants: Mapped[list["MatchParticipant"]] = relationship(
        back_populates="match",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class MatchParticipant(Base):
    __tablename__ = "match_participants"
    __table_args__ = (
        UniqueConstraint(
            "match_id", "user_id", name="uq_match_participants_match_user"
        ),
        CheckConstraint(
            "status IN ('invited', 'confirmed', 'tentative', 'absent', 'substitute')",
            name="ck_match_participants_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default="invited", nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    match: Mapped["Match"] = relationship(back_populates="participants")


Index("ix_matches_created_by", Match.created_by)
Index("ix_match_participants_user_id", MatchParticipant.user_id)
