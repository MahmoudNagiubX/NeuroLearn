from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteFolderCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    parent_id: UUID | None = None


class NoteFolderUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1)
    parent_id: UUID | None = None


class NoteFolderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime


class NoteCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    folder_id: UUID | None = None
    title: str = Field(min_length=1)
    content_md: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: UUID | None = None
    folder_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1)
    content_md: str | None = Field(default=None, min_length=1)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    subject_id: UUID | None
    folder_id: UUID | None
    title: str
    content_md: str
    created_at: datetime
    updated_at: datetime


class NoteAttachmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    original_filename: str = Field(min_length=1)
    storage_key: str = Field(min_length=1)
    file_extension: str | None = None
    mime_type: str | None = None
    file_size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = None
    storage_provider: str = "s3"
    upload_status: str = "uploaded"


class NoteAttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    note_id: UUID
    user_id: UUID
    original_filename: str
    file_extension: str | None
    mime_type: str | None
    file_size_bytes: int | None
    checksum: str | None
    storage_provider: str
    storage_key: str
    upload_status: str
    created_at: datetime
