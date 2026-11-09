from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.match import Match, MatchParticipant
from app.models.user import User
from app.schemas.match import (
    MatchCreate,
    MatchDateUpdate,
    MatchOut,
    MatchParticipantOut,
    MatchParticipantUpdate,
)

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
def create_match(
    match_data: MatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = Match(
        created_by=current_user.id,
        **match_data.model_dump(),
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


@router.get("", response_model=list[MatchOut])
def list_matches(db: Session = Depends(get_db)):
    return db.query(Match).order_by(Match.created_at.desc()).all()


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: UUID, db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return match


@router.patch("/{match_id}/date", response_model=MatchOut)
def set_match_date(
    match_id: UUID,
    date_data: MatchDateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede confirmar la fecha")

    match.match_date = date_data.match_date
    match.start_time = date_data.start_time
    match.status = "confirmed"
    db.commit()
    db.refresh(match)
    return match


@router.patch("/{match_id}/cancel", response_model=MatchOut)
def cancel_match(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede cancelar el partido")

    match.status = "cancelled"
    db.commit()
    db.refresh(match)
    return match


@router.post(
    "/{match_id}/participants",
    response_model=MatchParticipantOut,
    status_code=status.HTTP_201_CREATED,
)
def join_match(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.status in ["cancelled", "played"]:
        raise HTTPException(status_code=409, detail="No es posible unirse a este partido")

    existing = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == current_user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ya estás registrado en este partido")

    participant = MatchParticipant(
        match_id=match_id,
        user_id=current_user.id,
        status="confirmed",
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


@router.patch(
    "/{match_id}/participants/{user_id}",
    response_model=MatchParticipantOut,
)
def update_participant_status(
    match_id: UUID,
    user_id: UUID,
    participant_data: MatchParticipantUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede actualizar participantes")

    participant = (
        db.query(MatchParticipant)
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.user_id == user_id,
        )
        .first()
    )
    if participant is None:
        raise HTTPException(status_code=404, detail="Participante no encontrado")

    participant.status = participant_data.status
    db.commit()
    db.refresh(participant)
    return participant
