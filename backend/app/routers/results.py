from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.match import Match
from app.models.result import TeamMatchResult
from app.models.team import Team
from app.models.user import User
from app.schemas.result import TeamMatchResultCreate, TeamMatchResultOut

router = APIRouter(prefix="/matches/{match_id}/results", tags=["Results"])


@router.post("", response_model=TeamMatchResultOut, status_code=status.HTTP_201_CREATED)
def create_match_result(
    match_id: UUID,
    result_data: TeamMatchResultCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede registrar resultados")

    if match.status != "played":
        raise HTTPException(status_code=409, detail="Solo se pueden registrar resultados en partidos jugados")

    team = db.get(Team, result_data.team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    existing = (
        db.query(TeamMatchResult)
        .filter(
            TeamMatchResult.match_id == match_id,
            TeamMatchResult.team_id == result_data.team_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Este equipo ya tiene un resultado registrado")

    result = TeamMatchResult(
        match_id=match_id,
        team_id=result_data.team_id,
        goals_for=result_data.goals_for,
        goals_against=result_data.goals_against,
        result=result_data.result,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


@router.get("", response_model=list[TeamMatchResultOut])
def list_match_results(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    return db.query(TeamMatchResult).filter(TeamMatchResult.match_id == match_id).all()
