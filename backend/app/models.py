"""Database models: Python classes that describe our tables.

Each class is one table, each attribute is one column. Models tell Python
what the tables look like; the migrations in alembic/versions/ are what
actually create them in Postgres. When you change a model, add a migration.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# The three columns of the task board. Stored as plain text in the database;
# the API (schemas.py) rejects anything that isn't one of these.
TASK_STATUSES = ("todo", "in_progress", "done")


class Base(DeclarativeBase):
    """Parent class for all models. Alembic uses it to find every table."""


class User(Base):
    """Someone who can own tasks on the board."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Optional: people found in meeting notes usually only have a name.
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    # server_default=func.now() lets Postgres fill in the time on insert.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Note(Base):
    """Meeting notes or chat messages that someone pasted in."""

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Task(Base):
    """One card on the task board."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="todo")
    due_date: Mapped[date | None] = mapped_column(Date)
    # If the owner is deleted, keep the task but make it unassigned.
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    # Which pasted note this task came from (empty for tasks added by hand).
    note_id: Mapped[int | None] = mapped_column(
        ForeignKey("notes.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Lets us write task.owner to get the User object (SQLAlchemy runs the
    # query for us). lazy="joined" loads the owner in the same query.
    owner: Mapped[User | None] = relationship(lazy="joined")
