from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.match import Match
from app.models.match_event import MatchEvent
from app.models.user import User
from app.schemas.match_event import MatchEventCreate, MatchEventOut

router = APIRouter(prefix="/matches/{match_id}/events", tags=["Match events"])


@router.post("", response_model=MatchEventOut, status_code=status.HTTP_201_CREATED)
def create_match_event(
    match_id: UUID,
    event_data: MatchEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.status != "played":
        raise HTTPException(status_code=409, detail="Solo se pueden registrar eventos en partidos jugados")

    if not db.get(User, event_data.player_id):
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    event = MatchEvent(
        match_id=match_id,
        player_id=event_data.player_id,
        event_type=event_data.event_type,
        minute=event_data.minute,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[MatchEventOut])
def list_match_events(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    return (
        db.query(MatchEvent)
        .filter(MatchEvent.match_id == match_id)
        .order_by(MatchEvent.created_at)
        .all()
    )
