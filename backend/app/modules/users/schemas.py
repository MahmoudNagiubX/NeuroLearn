from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SignupRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: str = Field(min_length=3)
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    is_email_verified: bool
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AuthMeResponse(UserPublic):
    pass


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    user: UserPublic


class UserSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    timezone: str
    daily_study_goal_minutes: int
    pomodoro_focus_minutes: int
    pomodoro_break_minutes: int
    pomodoro_long_break_minutes: int
    pomodoro_sessions_before_long_break: int
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    timezone: str | None = None
    daily_study_goal_minutes: int | None = Field(default=None, gt=0)
    pomodoro_focus_minutes: int | None = Field(default=None, gt=0)
    pomodoro_break_minutes: int | None = Field(default=None, ge=0)
    pomodoro_long_break_minutes: int | None = Field(default=None, ge=0)
    pomodoro_sessions_before_long_break: int | None = Field(default=None, gt=0)
