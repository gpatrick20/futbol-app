from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.availability import AvailabilityVote
from app.models.match import Match
from app.models.user import User
from app.schemas.availability import (
    AvailabilityVoteCreate,
    AvailabilityVoteOut,
)

router = APIRouter(
    prefix="/matches/{match_id}/availability",
    tags=["Availability"],
)


@router.post(
    "",
    response_model=AvailabilityVoteOut,
    status_code=status.HTTP_201_CREATED,
)
def create_availability_vote(
    match_id: UUID,
    vote_data: AvailabilityVoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Partido no encontrado",
        )

    if match.status not in ("proposed", "voting"):
        raise HTTPException(
            status_code=409,
            detail="Este partido ya no acepta votos de disponibilidad",
        )

    vote_values = {
        "match_id": match_id,
        "user_id": current_user.id,
        "proposed_date": vote_data.proposed_date,
        "proposed_time": vote_data.proposed_time,
    }

    existing_vote = (
        db.query(AvailabilityVote)
        .filter_by(**vote_values)
        .first()
    )

    if existing_vote is not None:
        raise HTTPException(
            status_code=409,
            detail="Ya registraste disponibilidad para esta fecha y hora",
        )

    vote = AvailabilityVote(
        **vote_values,
        availability=vote_data.availability,
    )
    db.add(vote)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()

        duplicate_vote = (
            db.query(AvailabilityVote)
            .filter_by(**vote_values)
            .first()
        )

        if duplicate_vote is not None:
            raise HTTPException(
                status_code=409,
                detail="Ya registraste disponibilidad para esta fecha y hora",
            ) from exc

        raise

    db.refresh(vote)
    return vote


@router.get("", response_model=list[AvailabilityVoteOut])
def list_availability_votes(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)

    if match is None:
        raise HTTPException(
            status_code=404,
            detail="Partido no encontrado",
        )

    return (
        db.query(AvailabilityVote)
        .filter(AvailabilityVote.match_id == match_id)
        .order_by(
            AvailabilityVote.proposed_date,
            AvailabilityVote.proposed_time,
        )
        .all()
    )
