from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth_dependencies import get_current_user
from app.core.database.session import get_db
from app.modules.tasks.models import Task, TaskStatus
from app.modules.tasks.schemas import (
    TagCreate,
    TagRead,
    TaskCreate,
    TaskListCreate,
    TaskListRead,
    TaskListUpdate,
    TaskRead,
    TaskUpdate,
)
from app.modules.tasks.service import (
    CrossEntityValidationError,
    DuplicateNameError,
    TaskStateError,
    complete_task,
    create_tag,
    create_task,
    create_task_list,
    get_task,
    get_task_list,
    list_tags,
    list_task_lists,
    list_tasks,
    update_task,
    update_task_list,
)
from app.modules.users.models import User


router = APIRouter(tags=["tasks"])


def _to_task_read(task: Task) -> TaskRead:
    return TaskRead(
        id=task.id,
        user_id=task.user_id,
        subject_id=task.subject_id,
        task_list_id=task.list_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        position=task.position,
        due_at=task.due_at,
        reminder_at=task.reminder_at,
        estimated_minutes=task.estimated_minutes,
        completed_at=task.completed_at,
        archived_at=task.archived_at,
        is_recurring=task.is_recurring,
        recurrence_rule=task.recurrence_rule,
        tag_ids=[tag.id for tag in task.tags],
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.post("/task-lists", response_model=TaskListRead, status_code=status.HTTP_201_CREATED)
def create_task_list_endpoint(
    payload: TaskListCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskListRead:
    try:
        task_list = create_task_list(db, user_id=current_user.id, name=payload.name)
    except DuplicateNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TaskListRead.model_validate(task_list)


@router.get("/task-lists", response_model=list[TaskListRead])
def list_task_lists_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[TaskListRead]:
    task_lists = list_task_lists(db, user_id=current_user.id)
    return [TaskListRead.model_validate(task_list) for task_list in task_lists]


@router.patch("/task-lists/{task_list_id}", response_model=TaskListRead)
def update_task_list_endpoint(
    task_list_id: UUID,
    payload: TaskListUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskListRead:
    if get_task_list(db, user_id=current_user.id, task_list_id=task_list_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task list not found.")
    try:
        task_list = update_task_list(db, user_id=current_user.id, task_list_id=task_list_id, name=payload.name)
    except DuplicateNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if task_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task list not found.")
    return TaskListRead.model_validate(task_list)


@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    try:
        task = create_task(db, user_id=current_user.id, payload=payload)
    except (CrossEntityValidationError, TaskStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_task_read(task)


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[TaskStatus | None, Query(alias="status")] = None,
    subject_id: UUID | None = None,
    task_list_id: UUID | None = None,
) -> list[TaskRead]:
    tasks = list_tasks(
        db,
        user_id=current_user.id,
        status=status_filter,
        subject_id=subject_id,
        task_list_id=task_list_id,
    )
    return [_to_task_read(task) for task in tasks]


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    task = get_task(db, user_id=current_user.id, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return _to_task_read(task)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: UUID,
    payload: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    try:
        task = update_task(db, user_id=current_user.id, task_id=task_id, payload=payload)
    except (CrossEntityValidationError, TaskStateError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return _to_task_read(task)


@router.post("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task_endpoint(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TaskRead:
    task = complete_task(db, user_id=current_user.id, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return _to_task_read(task)


@router.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag_endpoint(
    payload: TagCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TagRead:
    try:
        tag = create_tag(db, user_id=current_user.id, name=payload.name)
    except DuplicateNameError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TagRead.model_validate(tag)


@router.get("/tags", response_model=list[TagRead])
def list_tags_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[TagRead]:
    tags = list_tags(db, user_id=current_user.id)
    return [TagRead.model_validate(tag) for tag in tags]
