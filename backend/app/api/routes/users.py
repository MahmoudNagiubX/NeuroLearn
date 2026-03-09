from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.users.models import User
from app.modules.users.schemas import UserPublic, UserSettingsRead, UserSettingsUpdate
from app.modules.users.service import get_or_create_user_settings, update_user_settings


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserPublic)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.get("/settings", response_model=UserSettingsRead)
def read_user_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserSettingsRead:
    user_settings = get_or_create_user_settings(db, user_id=current_user.id)
    return UserSettingsRead.model_validate(user_settings)


@router.patch("/settings", response_model=UserSettingsRead)
def patch_user_settings(
    payload: UserSettingsUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> UserSettingsRead:
    user_settings = update_user_settings(
        db,
        user_id=current_user.id,
        payload=payload,
    )
    return UserSettingsRead.model_validate(user_settings)
