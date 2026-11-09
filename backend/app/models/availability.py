import uuid

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AvailabilityVote(Base):
    __tablename__ = "availability_votes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matches.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    proposed_date: Mapped[object] = mapped_column(Date, nullable=False)
    proposed_time: Mapped[object] = mapped_column(Time, nullable=False)
    availability: Mapped[str] = mapped_column(String(20), nullable=False)
