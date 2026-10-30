"""Endpoints for the task board.

GET    /tasks          list tasks (optionally filtered)
POST   /tasks          add one task by hand
POST   /tasks/bulk     save the tasks a user approved after extraction
PATCH  /tasks/{id}     change some fields (e.g. move to "done")
DELETE /tasks/{id}     remove a task
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Note, Task
from app.routers.users import find_or_create_user
from app.schemas import TaskBulkCreate, TaskCreate, TaskRead, TaskStatus, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _new_task(db: Session, data: TaskCreate, note_id: int | None = None) -> Task:
    """Build a Task from API input. The caller adds and commits it."""
    owner = find_or_create_user(db, data.owner_name) if data.owner_name else None
    return Task(
        title=data.title.strip(),
        description=data.description,
        due_date=data.due_date,
        owner=owner,
        note_id=note_id,
        status="todo",
    )


def _get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(
    status: TaskStatus | None = None,
    owner_id: int | None = None,
    db: Session = Depends(get_db),
):
    """All tasks, soonest due date first (tasks with no date go last).

    Example: GET /tasks?status=todo&owner_id=3
    """
    query = select(Task).order_by(Task.due_date.asc().nulls_last(), Task.id)
    if status:
        query = query.where(Task.status == status)
    if owner_id:
        query = query.where(Task.owner_id == owner_id)
    return db.scalars(query).all()


@router.post("", response_model=TaskRead, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = _new_task(db, data)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/bulk", response_model=list[TaskRead], status_code=201)
def create_tasks_bulk(data: TaskBulkCreate, db: Session = Depends(get_db)):
    """Save every approved task in one go. Either all are saved or none."""
    if data.note_id is not None and db.get(Note, data.note_id) is None:
        raise HTTPException(status_code=404, detail=f"Note {data.note_id} not found.")

    tasks = [_new_task(db, item, note_id=data.note_id) for item in data.tasks]
    db.add_all(tasks)
    db.commit()  # one transaction: if anything failed above, nothing is saved
    for task in tasks:
        db.refresh(task)
    return tasks


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)

    # exclude_unset=True keeps only the fields the client actually sent,
    # so {"status": "done"} changes the status and nothing else.
    changes = data.model_dump(exclude_unset=True)

    if "owner_name" in changes:
        name = (changes.pop("owner_name") or "").strip()
        task.owner = find_or_create_user(db, name) if name else None
    if changes.get("title") is None:
        changes.pop("title", None)  # a title can't be removed, only changed
    if changes.get("status") is None:
        changes.pop("status", None)

    for field, value in changes.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = _get_task_or_404(db, task_id)
    db.delete(task)
    db.commit()
    return Response(status_code=204)
