from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


AUTH_COOKIE_NAME = "futbol_access_token"

# Orígenes permitidos para el desarrollo local.
TRUSTED_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
}

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    auto_error=False,
)


def require_trusted_origin(request: Request) -> None:
    origin = request.headers.get("origin")

    if origin not in TRUSTED_ORIGINS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origen de la solicitud no permitido",
        )


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Conservamos la compatibilidad con Authorization: Bearer.
    # Si no se envía, buscamos la credencial en la cookie.
    if token is None:
        token = request.cookies.get(AUTH_COOKIE_NAME)

        # Las operaciones que modifican datos mediante cookies
        # deben proceder de un origen permitido.
        if token and request.method not in SAFE_METHODS:
            require_trusted_origin(request)

    if not token:
        raise credentials_exception

    subject = decode_access_token(token)

    if not isinstance(subject, str):
        raise credentials_exception

    try:
        user_id = UUID(subject)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    return user