from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.match import Match
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentStatusUpdate

router = APIRouter(prefix="/matches/{match_id}/payments", tags=["Payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    match_id: UUID,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if not db.get(User, payment_data.user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    existing = (
        db.query(Payment)
        .filter(
            Payment.match_id == match_id,
            Payment.user_id == payment_data.user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe un pago para este usuario en este partido")

    payment = Payment(
        match_id=match_id,
        user_id=payment_data.user_id,
        amount=payment_data.amount,
        method=payment_data.method,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=list[PaymentOut])
def list_payments(
    match_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    return db.query(Payment).filter(Payment.match_id == match_id).all()


@router.patch("/{payment_id}", response_model=PaymentOut)
def update_payment_status(
    match_id: UUID,
    payment_id: UUID,
    status_data: PaymentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    match = db.get(Match, match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Partido no encontrado")

    if match.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Solo el creador puede actualizar pagos")

    payment = db.get(Payment, payment_id)
    if payment is None or payment.match_id != match_id:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    payment.status = status_data.status
    if status_data.status == "paid":
        from datetime import datetime, timezone

        payment.paid_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)
    return payment
