"""Database models: Python classes that describe our tables.

Each class is one table, each attribute is one column. Models tell Python
what the tables look like; the migrations in alembic/versions/ are what
actually create them in Postgres. When you change a model, add a migration.
"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Parent class for all models. Alembic uses it to find every table."""


class User(Base):
    """Someone who can own tasks on the board."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    # server_default=func.now() lets Postgres fill in the time on insert.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
