from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
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


def _count_confirmed_participants(db: Session, match_id: UUID) -> int:
    return (
        db.query(func.count(MatchParticipant.id))
        .filter(
            MatchParticipant.match_id == match_id,
            MatchParticipant.status == "confirmed",
        )
        .scalar()
        or 0
    )


def _sync_match_capacity_status(
    match: Match,
    confirmed_count: int,
) -> None:
    if match.status in ("cancelled", "played"):
        return

    if match.max_players > 0 and confirmed_count >= match.max_players:
        match.status = "full"
    elif match.status == "full":
        match.status = "confirmed"



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
    db.flush()

    organizer_participant = MatchParticipant(
        match_id=match.id,
        user_id=current_user.id,
        status="confirmed",
        team="A",
    )
    db.add(organizer_participant)

    _sync_match_capacity_status(match, confirmed_count=1)
    db.commit()
    db.refresh(organizer_participant)
    db.refresh(match)
    return match



@router.get("", response_model=list[MatchOut])
def list_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Match)
        .order_by(Match.created_at.desc())
        .all()
    )



@router.get("/organized", response_model=list[MatchOut])
def list_organized_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Match)
        .filter(Match.created_by == current_user.id)
        .order_by(Match.created_at.desc())
        .all()
    )



@router.get("/participating", response_model=list[MatchOut])
def list_participating_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Match)
        .join(
            MatchParticipant,
            MatchParticipant.match_id == Match.id,
        )
        .filter(MatchParticipant.user_id == current_user.id)
        .order_by(Match.created_at.desc())
        .all()
    )


@router.get("/available", response_model=list[MatchOut])
def list_available_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    participant_match_ids = select(MatchParticipant.match_id).where(
        MatchParticipant.user_id == current_user.id
    )
    confirmed_counts = (
        db.query(
            MatchParticipant.match_id.label("match_id"),
            func.count(MatchParticipant.id).label("confirmed_count"),
        )
        .filter(MatchParticipant.status == "confirmed")
        .group_by(MatchParticipant.match_id)
        .subquery()
    )

    return (
        db.query(Match)
        .outerjoin(
            confirmed_counts,
            confirmed_counts.c.match_id == Match.id,
        )
        .filter(
            Match.created_by != current_user.id,
            ~Match.id.in_(participant_match_ids),
            ~Match.status.in_(("cancelled", "played", "full")),
            Match.max_players > 0,
            func.coalesce(confirmed_counts.c.confirmed_count, 0) < Match.max_players,
        )
        .order_by(Match.created_at.desc())
        .all()
    )



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
        raise HTTPException(
            status_code=404,
            detail="Partido no encontrado",
        )


    if match.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador puede confirmar la fecha",
        )


    if match.status in ("cancelled", "played"):
        raise HTTPException(
            status_code=409,
            detail="No se puede cambiar la fecha de un partido cancelado o jugado",
        )


    match.match_date = date_data.match_date
    match.start_time = date_data.start_time
    match.status = "confirmed"
    confirmed_count = _count_confirmed_participants(db, match_id)
    _sync_match_capacity_status(match, confirmed_count)


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
        raise HTTPException(
            status_code=404,
            detail="Partido no encontrado",
        )


    if match.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador puede cancelar el partido",
        )


    if match.status == "played":
        raise HTTPException(
            status_code=409,
            detail="No se puede cancelar un partido jugado",
        )


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
    try:
        match = (
            db.query(Match)
            .filter(Match.id == match_id)
            .with_for_update()
            .first()
        )
        if match is None:
            raise HTTPException(
                status_code=404,
                detail="Partido no encontrado",
            )

        if match.status in ("cancelled", "played"):
            raise HTTPException(
                status_code=409,
                detail="No es posible unirse a este partido",
            )

        if match.max_players <= 0:
            raise HTTPException(
                status_code=409,
                detail="Este partido no tiene cupos habilitados",
            )

        existing = (
            db.query(MatchParticipant)
            .filter(
                MatchParticipant.match_id == match_id,
                MatchParticipant.user_id == current_user.id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Ya estás registrado en este partido",
            )

        confirmed_count = _count_confirmed_participants(
            db, match_id
        )
        if confirmed_count >= match.max_players:
            _sync_match_capacity_status(
                match,
                confirmed_count,
            )
            raise HTTPException(
                status_code=409,
                detail="No hay cupos disponibles en este partido",
            )

        participant = MatchParticipant(
            match_id=match_id,
            user_id=current_user.id,
            status="confirmed",
            team="A",
        )
        db.add(participant)

        _sync_match_capacity_status(
            match,
            confirmed_count + 1,
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya estás registrado en este partido",
        )

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
    match = (
        db.query(Match)
        .filter(Match.id == match_id)
        .with_for_update()
        .first()
    )
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
    db.flush()
    confirmed_count_after = _count_confirmed_participants(db, match_id)
    if (
        match.max_players > 0
        and confirmed_count_after > match.max_players
    ):
        raise HTTPException(
            status_code=409,
            detail="No hay cupos disponibles en este partido",
        )

    _sync_match_capacity_status(match, confirmed_count_after)
    db.commit()
    db.refresh(participant)
    return participant


@router.patch("/{match_id}/finish", response_model=MatchOut)
def finish_match(
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


    if match.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Solo el creador puede finalizar el partido",
        )


    # Repetir la solicitud no modifica un partido ya finalizado.
    if match.status == "played":
        return match


    if match.status not in ("confirmed", "full"):
        raise HTTPException(
            status_code=409,
            detail="Solo se pueden finalizar partidos confirmados o completos",
        )


    match.status = "played"
    db.commit()
    db.refresh(match)
    return match