import uuid
from datetime import date, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AvailabilityVote(Base):
    __tablename__ = "availability_votes"
    __table_args__ = (
        UniqueConstraint(
            "match_id",
            "user_id",
            "proposed_date",
            "proposed_time",
            name="uq_availability_votes_match_user_slot",
        ),
        CheckConstraint(
            "availability IN ('available', 'maybe', 'unavailable')",
            name="ck_availability_votes_availability",
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
    proposed_date: Mapped[date] = mapped_column(Date, nullable=False)
    proposed_time: Mapped[time] = mapped_column(Time, nullable=False)
    availability: Mapped[str] = mapped_column(String(20), nullable=False)


Index("ix_availability_votes_user_id", AvailabilityVote.user_id)
