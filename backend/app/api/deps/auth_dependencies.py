from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database.session import get_db
from app.core.security.jwt import decode_access_token
from app.modules.users.models import User
from app.modules.users.service import get_user_by_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise _credentials_exception() from exc

    user = get_user_by_id(db, payload.get("sub"))
    if user is None:
        raise _credentials_exception()
    return user
