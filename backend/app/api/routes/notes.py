from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.notes.schemas import (
    NoteAttachmentCreate,
    NoteAttachmentRead,
    NoteCreate,
    NoteFolderCreate,
    NoteFolderRead,
    NoteFolderUpdate,
    NoteRead,
    NoteUpdate,
)
from app.modules.notes.service import (
    CrossEntityValidationError,
    create_note,
    create_note_attachment,
    create_note_folder,
    delete_note_attachment,
    get_note,
    list_note_attachments,
    list_note_folders,
    list_notes,
    update_note,
    update_note_folder,
)
from app.modules.users.models import User


router = APIRouter(tags=["notes"])


@router.post("/note-folders", response_model=NoteFolderRead, status_code=status.HTTP_201_CREATED)
def create_note_folder_endpoint(
    payload: NoteFolderCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteFolderRead:
    try:
        folder = create_note_folder(
            db,
            user_id=current_user.id,
            name=payload.name,
            parent_id=payload.parent_id,
        )
    except CrossEntityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return NoteFolderRead.model_validate(folder)


@router.get("/note-folders", response_model=list[NoteFolderRead])
def list_note_folders_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[NoteFolderRead]:
    folders = list_note_folders(db, user_id=current_user.id)
    return [NoteFolderRead.model_validate(folder) for folder in folders]


@router.patch("/note-folders/{folder_id}", response_model=NoteFolderRead)
def update_note_folder_endpoint(
    folder_id: UUID,
    payload: NoteFolderUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteFolderRead:
    try:
        folder = update_note_folder(
            db,
            user_id=current_user.id,
            folder_id=folder_id,
            payload=payload,
        )
    except CrossEntityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note folder not found.")
    return NoteFolderRead.model_validate(folder)


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note_endpoint(
    payload: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteRead:
    try:
        note = create_note(db, user_id=current_user.id, payload=payload)
    except CrossEntityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return NoteRead.model_validate(note)


@router.get("/notes", response_model=list[NoteRead])
def list_notes_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    subject_id: UUID | None = Query(default=None),
    folder_id: UUID | None = Query(default=None),
) -> list[NoteRead]:
    try:
        notes = list_notes(
            db,
            user_id=current_user.id,
            subject_id=subject_id,
            folder_id=folder_id,
        )
    except CrossEntityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return [NoteRead.model_validate(note) for note in notes]


@router.get("/notes/{note_id}", response_model=NoteRead)
def get_note_endpoint(
    note_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteRead:
    note = get_note(db, user_id=current_user.id, note_id=note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    return NoteRead.model_validate(note)


@router.patch("/notes/{note_id}", response_model=NoteRead)
def update_note_endpoint(
    note_id: UUID,
    payload: NoteUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteRead:
    try:
        note = update_note(
            db,
            user_id=current_user.id,
            note_id=note_id,
            payload=payload,
        )
    except CrossEntityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    return NoteRead.model_validate(note)


@router.post("/notes/{note_id}/attachments", response_model=NoteAttachmentRead, status_code=status.HTTP_201_CREATED)
def create_note_attachment_endpoint(
    note_id: UUID,
    payload: NoteAttachmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> NoteAttachmentRead:
    attachment = create_note_attachment(db, user_id=current_user.id, note_id=note_id, payload=payload)
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    return NoteAttachmentRead.model_validate(attachment)


@router.get("/notes/{note_id}/attachments", response_model=list[NoteAttachmentRead])
def list_note_attachments_endpoint(
    note_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[NoteAttachmentRead]:
    attachments = list_note_attachments(db, user_id=current_user.id, note_id=note_id)
    if attachments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    return [NoteAttachmentRead.model_validate(attachment) for attachment in attachments]


@router.delete("/notes/{note_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_attachment_endpoint(
    note_id: UUID,
    attachment_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    deleted = delete_note_attachment(
        db,
        user_id=current_user.id,
        note_id=note_id,
        attachment_id=attachment_id,
    )
    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found.")
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found.")
