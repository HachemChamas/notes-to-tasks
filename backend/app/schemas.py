"""API schemas: the shape of the JSON the API sends and receives.

Models (models.py) describe database tables. Schemas describe JSON.
Keeping them separate means we choose exactly which fields leave the API,
and FastAPI rejects bad input (with a 422 error) before our code runs.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# Only these three values are allowed for a task's status.
TaskStatus = Literal["todo", "in_progress", "done"]


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)


class UserRead(BaseModel):
    """A user as returned by the API."""

    # Lets Pydantic read the values from a SQLAlchemy User object
    # (user.id, user.email, ...) instead of only from a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str | None
    name: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Extraction: notes in, suggested tasks out (nothing is saved as a task yet)
# ---------------------------------------------------------------------------
class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)
    # The day the meeting happened, so "by Friday" can become a real date.
    # Defaults to today when left out.
    meeting_date: date | None = None


class SuggestedTask(BaseModel):
    """A task the AI found. The user reviews it before it is saved."""

    title: str
    description: str | None = None
    owner_name: str | None = None
    due_date: date | None = None


class ExtractResponse(BaseModel):
    note_id: int
    tasks: list[SuggestedTask]


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    # A name, not an id: the backend finds that person or adds them.
    owner_name: str | None = Field(default=None, max_length=100)
    due_date: date | None = None


class TaskBulkCreate(BaseModel):
    """The tasks a user approved after reviewing the AI's suggestions."""

    note_id: int | None = None
    tasks: list[TaskCreate] = Field(min_length=1)


class TaskUpdate(BaseModel):
    """Every field is optional: only the fields you send are changed."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatus | None = None
    # Send "" or null to unassign the task.
    owner_name: str | None = Field(default=None, max_length=100)
    due_date: date | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_date: date | None
    owner: UserRead | None
    note_id: int | None
    created_at: datetime
