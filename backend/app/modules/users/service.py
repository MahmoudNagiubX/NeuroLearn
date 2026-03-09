from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security.hashing import get_password_hash, verify_password
from app.modules.users.models import User, UserSettings
from app.modules.users.schemas import UserSettingsUpdate


class DuplicateEmailError(ValueError):
    pass


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == _normalize_email(email)))


def get_user_by_id(db: Session, user_id: UUID | str) -> User | None:
    try:
        parsed_id = UUID(str(user_id))
    except (TypeError, ValueError):
        return None
    return db.get(User, parsed_id)


def create_user(db: Session, *, email: str, password: str, full_name: str | None) -> User:
    user = User(
        email=_normalize_email(email),
        password_hash=get_password_hash(password),
        full_name=full_name,
    )
    db.add(user)
    try:
        db.flush()
        db.add(UserSettings(user_id=user.id))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateEmailError("Email is already registered.") from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_or_create_user_settings(db: Session, *, user_id: UUID) -> UserSettings:
    user_settings = db.get(UserSettings, user_id)
    if user_settings is not None:
        return user_settings
    user_settings = UserSettings(user_id=user_id)
    db.add(user_settings)
    db.commit()
    db.refresh(user_settings)
    return user_settings


def update_user_settings(
    db: Session,
    *,
    user_id: UUID,
    payload: UserSettingsUpdate,
) -> UserSettings:
    user_settings = get_or_create_user_settings(db, user_id=user_id)
    updates = payload.model_dump(exclude_unset=True)
    for field_name, value in updates.items():
        setattr(user_settings, field_name, value)
    if updates:
        db.add(user_settings)
        db.commit()
        db.refresh(user_settings)
    return user_settings
