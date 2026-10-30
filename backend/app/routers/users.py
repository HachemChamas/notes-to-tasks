"""Endpoints for people on the board: GET /users and POST /users."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


def find_or_create_user(db: Session, name: str) -> User:
    """Find a user by name (ignoring upper/lower case), or add a new one.

    Used when saving tasks: the AI gives us names like "ada", and we want
    every task for Ada to point at the same user. The caller commits.
    """
    clean_name = name.strip()
    user = db.scalars(
        select(User).where(func.lower(User.name) == clean_name.lower())
    ).first()
    if user is None:
        user = User(name=clean_name)
        db.add(user)
        db.flush()  # sends the INSERT now so user.id is filled in
    return user


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    """Return every user, oldest first."""
    return db.scalars(select(User).order_by(User.id)).all()


@router.post("", response_model=UserRead, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Add a person to the board."""
    if data.email:
        taken = db.scalars(select(User).where(User.email == data.email)).first()
        if taken:
            raise HTTPException(status_code=409, detail="That email is already used.")
    user = User(name=data.name.strip(), email=data.email or None)
    db.add(user)
    db.commit()
    db.refresh(user)  # reload to get id and created_at from the database
    return user
