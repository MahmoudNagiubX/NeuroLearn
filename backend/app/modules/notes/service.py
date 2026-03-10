from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.notes.models import Note, NoteAttachment, NoteFolder
from app.modules.notes.schemas import NoteAttachmentCreate, NoteCreate, NoteFolderUpdate, NoteUpdate
from app.modules.subjects.models import Subject


class CrossEntityValidationError(ValueError):
    pass


def _owned_subject_exists(db: Session, *, user_id: UUID, subject_id: UUID) -> bool:
    stmt = select(Subject.id).where(Subject.id == subject_id, Subject.user_id == user_id)
    return db.scalar(stmt) is not None


def _owned_folder_exists(db: Session, *, user_id: UUID, folder_id: UUID) -> bool:
    stmt = select(NoteFolder.id).where(NoteFolder.id == folder_id, NoteFolder.user_id == user_id)
    return db.scalar(stmt) is not None


def create_note_folder(
    db: Session,
    *,
    user_id: UUID,
    name: str,
    parent_id: UUID | None,
) -> NoteFolder:
    if parent_id is not None and not _owned_folder_exists(db, user_id=user_id, folder_id=parent_id):
        raise CrossEntityValidationError("parent_id does not belong to current user.")

    folder = NoteFolder(user_id=user_id, name=name, parent_id=parent_id)
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def list_note_folders(db: Session, *, user_id: UUID) -> list[NoteFolder]:
    stmt = select(NoteFolder).where(NoteFolder.user_id == user_id).order_by(NoteFolder.created_at.desc())
    return list(db.scalars(stmt).all())


def get_note_folder(db: Session, *, user_id: UUID, folder_id: UUID) -> NoteFolder | None:
    stmt = select(NoteFolder).where(NoteFolder.id == folder_id, NoteFolder.user_id == user_id)
    return db.scalar(stmt)


def update_note_folder(
    db: Session,
    *,
    user_id: UUID,
    folder_id: UUID,
    payload: NoteFolderUpdate,
) -> NoteFolder | None:
    folder = get_note_folder(db, user_id=user_id, folder_id=folder_id)
    if folder is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    if "parent_id" in updates:
        parent_id = updates["parent_id"]
        if parent_id == folder_id:
            raise CrossEntityValidationError("A folder cannot be its own parent.")
        if parent_id is not None and not _owned_folder_exists(db, user_id=user_id, folder_id=parent_id):
            raise CrossEntityValidationError("parent_id does not belong to current user.")

    for field_name, value in updates.items():
        setattr(folder, field_name, value)

    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


def create_note(db: Session, *, user_id: UUID, payload: NoteCreate) -> Note:
    if payload.subject_id is not None and not _owned_subject_exists(db, user_id=user_id, subject_id=payload.subject_id):
        raise CrossEntityValidationError("subject_id does not belong to current user.")
    if payload.folder_id is not None and not _owned_folder_exists(db, user_id=user_id, folder_id=payload.folder_id):
        raise CrossEntityValidationError("folder_id does not belong to current user.")

    note = Note(
        user_id=user_id,
        subject_id=payload.subject_id,
        folder_id=payload.folder_id,
        title=payload.title,
        content_md=payload.content_md,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def list_notes(
    db: Session,
    *,
    user_id: UUID,
    subject_id: UUID | None = None,
    folder_id: UUID | None = None,
) -> list[Note]:
    if subject_id is not None and not _owned_subject_exists(db, user_id=user_id, subject_id=subject_id):
        raise CrossEntityValidationError("subject_id does not belong to current user.")
    if folder_id is not None and not _owned_folder_exists(db, user_id=user_id, folder_id=folder_id):
        raise CrossEntityValidationError("folder_id does not belong to current user.")

    stmt = select(Note).where(Note.user_id == user_id)
    if subject_id is not None:
        stmt = stmt.where(Note.subject_id == subject_id)
    if folder_id is not None:
        stmt = stmt.where(Note.folder_id == folder_id)

    stmt = stmt.order_by(Note.updated_at.desc())
    return list(db.scalars(stmt).all())


def get_note(db: Session, *, user_id: UUID, note_id: UUID) -> Note | None:
    stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    return db.scalar(stmt)


def update_note(
    db: Session,
    *,
    user_id: UUID,
    note_id: UUID,
    payload: NoteUpdate,
) -> Note | None:
    note = get_note(db, user_id=user_id, note_id=note_id)
    if note is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    if "subject_id" in updates:
        subject_id = updates["subject_id"]
        if subject_id is not None and not _owned_subject_exists(db, user_id=user_id, subject_id=subject_id):
            raise CrossEntityValidationError("subject_id does not belong to current user.")
    if "folder_id" in updates:
        folder_id = updates["folder_id"]
        if folder_id is not None and not _owned_folder_exists(db, user_id=user_id, folder_id=folder_id):
            raise CrossEntityValidationError("folder_id does not belong to current user.")

    for field_name, value in updates.items():
        setattr(note, field_name, value)

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def create_note_attachment(
    db: Session,
    *,
    user_id: UUID,
    note_id: UUID,
    payload: NoteAttachmentCreate,
) -> NoteAttachment | None:
    note = get_note(db, user_id=user_id, note_id=note_id)
    if note is None:
        return None

    attachment = NoteAttachment(
        note_id=note.id,
        user_id=user_id,
        original_filename=payload.original_filename,
        file_extension=payload.file_extension,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
        checksum=payload.checksum,
        storage_provider=payload.storage_provider,
        storage_key=payload.storage_key,
        upload_status=payload.upload_status,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def list_note_attachments(db: Session, *, user_id: UUID, note_id: UUID) -> list[NoteAttachment] | None:
    note = get_note(db, user_id=user_id, note_id=note_id)
    if note is None:
        return None

    stmt = select(NoteAttachment).where(
        NoteAttachment.user_id == user_id,
        NoteAttachment.note_id == note_id,
    ).order_by(NoteAttachment.created_at.desc())
    return list(db.scalars(stmt).all())


def delete_note_attachment(
    db: Session,
    *,
    user_id: UUID,
    note_id: UUID,
    attachment_id: UUID,
) -> bool | None:
    note = get_note(db, user_id=user_id, note_id=note_id)
    if note is None:
        return None

    stmt = select(NoteAttachment).where(
        NoteAttachment.id == attachment_id,
        NoteAttachment.note_id == note_id,
        NoteAttachment.user_id == user_id,
    )
    attachment = db.scalar(stmt)
    if attachment is None:
        return False

    db.delete(attachment)
    db.commit()
    return True
