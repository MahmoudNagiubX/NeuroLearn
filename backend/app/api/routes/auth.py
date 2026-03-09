from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.core.security.jwt import create_access_token
from app.modules.users.models import User
from app.modules.users.schemas import AuthMeResponse, AuthResponse, LoginRequest, SignupRequest, UserPublic
from app.modules.users.service import (
    DuplicateEmailError,
    authenticate_user,
    create_user,
    get_user_by_email,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    payload: SignupRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    try:
        user = create_user(
            db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        ) from exc

    access_token = create_access_token(subject=user.id)
    return AuthResponse(
        access_token=access_token,
        user=UserPublic.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return AuthResponse(
        access_token=access_token,
        user=UserPublic.model_validate(user),
    )


@router.get("/me", response_model=AuthMeResponse)
def read_auth_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> AuthMeResponse:
    return AuthMeResponse.model_validate(current_user)
