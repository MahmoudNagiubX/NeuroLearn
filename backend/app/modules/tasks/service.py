from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.subjects.models import Subject
from app.modules.tasks.models import Tag, Task, TaskList, TaskStatus
from app.modules.tasks.schemas import TaskCreate, TaskUpdate
from app.modules.events.service import service as event_service


class DuplicateNameError(ValueError):
    pass


class CrossEntityValidationError(ValueError):
    pass


class TaskStateError(ValueError):
    pass


def _owned_subject_exists(db: Session, *, user_id: UUID, subject_id: UUID) -> bool:
    stmt = select(Subject.id).where(Subject.id == subject_id, Subject.user_id == user_id)
    return db.scalar(stmt) is not None


def _owned_task_list_exists(db: Session, *, user_id: UUID, task_list_id: UUID) -> bool:
    stmt = select(TaskList.id).where(TaskList.id == task_list_id, TaskList.user_id == user_id)
    return db.scalar(stmt) is not None


def _owned_tags(db: Session, *, user_id: UUID, tag_ids: list[UUID]) -> list[Tag]:
    unique_tag_ids = list(dict.fromkeys(tag_ids))
    if not unique_tag_ids:
        return []

    stmt = select(Tag).where(Tag.user_id == user_id, Tag.id.in_(unique_tag_ids))
    tags = list(db.scalars(stmt).all())
    if len(tags) != len(unique_tag_ids):
        raise CrossEntityValidationError("One or more tags are missing or not owned by current user.")

    tag_by_id = {tag.id: tag for tag in tags}
    return [tag_by_id[tag_id] for tag_id in unique_tag_ids]


def _apply_task_state_rules(task: Task) -> None:
    if task.is_recurring and not task.recurrence_rule:
        raise TaskStateError("recurrence_rule is required when is_recurring is true.")
    if not task.is_recurring and task.recurrence_rule is not None:
        raise TaskStateError("recurrence_rule must be null when is_recurring is false.")

    if task.status == TaskStatus.DONE and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)

    if task.status == TaskStatus.ARCHIVED and task.archived_at is None:
        task.archived_at = datetime.now(timezone.utc)

    if task.archived_at is not None and task.status != TaskStatus.ARCHIVED:
        raise TaskStateError("archived_at can only be set when status is archived.")


def create_task_list(db: Session, *, user_id: UUID, name: str) -> TaskList:
    task_list = TaskList(user_id=user_id, name=name)
    db.add(task_list)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateNameError("Task list name already exists.") from exc
    db.refresh(task_list)
    return task_list


def list_task_lists(db: Session, *, user_id: UUID) -> list[TaskList]:
    stmt = select(TaskList).where(TaskList.user_id == user_id).order_by(TaskList.created_at.desc())
    return list(db.scalars(stmt).all())


def get_task_list(db: Session, *, user_id: UUID, task_list_id: UUID) -> TaskList | None:
    stmt = select(TaskList).where(TaskList.id == task_list_id, TaskList.user_id == user_id)
    return db.scalar(stmt)


def update_task_list(db: Session, *, user_id: UUID, task_list_id: UUID, name: str) -> TaskList | None:
    task_list = get_task_list(db, user_id=user_id, task_list_id=task_list_id)
    if task_list is None:
        return None

    task_list.name = name
    db.add(task_list)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateNameError("Task list name already exists.") from exc
    db.refresh(task_list)
    return task_list


def create_tag(db: Session, *, user_id: UUID, name: str) -> Tag:
    tag = Tag(user_id=user_id, name=name)
    db.add(tag)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateNameError("Tag name already exists.") from exc
    db.refresh(tag)
    return tag


def list_tags(db: Session, *, user_id: UUID) -> list[Tag]:
    stmt = select(Tag).where(Tag.user_id == user_id).order_by(Tag.created_at.desc())
    return list(db.scalars(stmt).all())


def get_task(db: Session, *, user_id: UUID, task_id: UUID) -> Task | None:
    stmt = (
        select(Task)
        .options(selectinload(Task.tags))
        .where(Task.id == task_id, Task.user_id == user_id)
    )
    return db.scalar(stmt)


def create_task(db: Session, *, user_id: UUID, payload: TaskCreate) -> Task:
    if payload.subject_id is not None and not _owned_subject_exists(
        db,
        user_id=user_id,
        subject_id=payload.subject_id,
    ):
        raise CrossEntityValidationError("subject_id does not belong to current user.")

    if payload.task_list_id is not None and not _owned_task_list_exists(
        db,
        user_id=user_id,
        task_list_id=payload.task_list_id,
    ):
        raise CrossEntityValidationError("task_list_id does not belong to current user.")

    task = Task(
        user_id=user_id,
        subject_id=payload.subject_id,
        list_id=payload.task_list_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        position=payload.position,
        due_at=payload.due_at,
        reminder_at=payload.reminder_at,
        estimated_minutes=payload.estimated_minutes,
        is_recurring=payload.is_recurring,
        recurrence_rule=payload.recurrence_rule,
    )
    _apply_task_state_rules(task)

    if payload.tag_ids:
        task.tags = _owned_tags(db, user_id=user_id, tag_ids=payload.tag_ids)

    db.add(task)
    db.commit()
    db.refresh(task)
    
    event_service.track_task_created(db=db, user_id=user_id, task_id=task.id)
    
    result = get_task(db, user_id=user_id, task_id=task.id)
    return result if result is not None else task


def list_tasks(
    db: Session,
    *,
    user_id: UUID,
    status: TaskStatus | None = None,
    subject_id: UUID | None = None,
    task_list_id: UUID | None = None,
) -> list[Task]:
    stmt = select(Task).options(selectinload(Task.tags)).where(Task.user_id == user_id)

    if status is not None:
        stmt = stmt.where(Task.status == status)
    if subject_id is not None:
        stmt = stmt.where(Task.subject_id == subject_id)
    if task_list_id is not None:
        stmt = stmt.where(Task.list_id == task_list_id)

    stmt = stmt.order_by(Task.created_at.desc())
    return list(db.scalars(stmt).all())


def update_task(db: Session, *, user_id: UUID, task_id: UUID, payload: TaskUpdate) -> Task | None:
    task = get_task(db, user_id=user_id, task_id=task_id)
    if task is None:
        return None

    updates = payload.model_dump(exclude_unset=True)

    if "subject_id" in updates:
        subject_id = updates["subject_id"]
        if subject_id is not None and not _owned_subject_exists(db, user_id=user_id, subject_id=subject_id):
            raise CrossEntityValidationError("subject_id does not belong to current user.")

    if "task_list_id" in updates:
        task_list_id = updates["task_list_id"]
        if task_list_id is not None and not _owned_task_list_exists(db, user_id=user_id, task_list_id=task_list_id):
            raise CrossEntityValidationError("task_list_id does not belong to current user.")

    if "tag_ids" in updates:
        tag_ids = updates.pop("tag_ids")
        if tag_ids is None:
            task.tags = []
        else:
            task.tags = _owned_tags(db, user_id=user_id, tag_ids=tag_ids)

    if "task_list_id" in updates:
        task.list_id = updates.pop("task_list_id")

    for field_name, value in updates.items():
        setattr(task, field_name, value)

    _apply_task_state_rules(task)

    db.add(task)
    db.commit()
    db.refresh(task)
    return get_task(db, user_id=user_id, task_id=task.id)


def complete_task(db: Session, *, user_id: UUID, task_id: UUID) -> Task | None:
    task = get_task(db, user_id=user_id, task_id=task_id)
    if task is None:
        return None

    task.status = TaskStatus.DONE
    task.completed_at = datetime.now(timezone.utc)
    _apply_task_state_rules(task)

    db.add(task)
    db.commit()
    db.refresh(task)
    
    event_service.track_task_completed(db=db, user_id=user_id, task_id=task.id)
    
    return get_task(db, user_id=user_id, task_id=task.id)
