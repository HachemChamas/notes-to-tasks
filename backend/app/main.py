"""The FastAPI application: this is where the API endpoints live.

Run it locally (from the backend/ folder) with:
    uvicorn app.main:app --reload
Then open http://localhost:8000/docs to try the endpoints in your browser.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import FRONTEND_ORIGIN
from app.database import check_database, get_db
from app.schemas import UserRead

app = FastAPI(title="notes-to-tasks API")

# CORS: the frontend (localhost:5173) and backend (localhost:8000) count as
# different "origins", so the browser blocks the frontend's requests unless
# the backend says that origin is allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health(database_ok: bool = Depends(check_database)):
    """Tell the caller the API is running and whether Postgres is reachable.

    `Depends(check_database)` means FastAPI calls check_database() for us
    and passes in the result. Tests can swap that function for a fake one,
    so they don't need a real database (see tests/test_health.py).
    """
    return {
        "status": "ok",
        "database": "ok" if database_ok else "unavailable",
    }


@app.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    """Return every user in the database, oldest first."""
    # ------------------------------------------------------------------
    # TODO (backend): implement this endpoint.
    #
    # What it should do:
    #   Query the `users` table and return all users, ordered by id
    #   (oldest first). If there are no users, return an empty list.
    #
    # What you already have:
    #   - `db` is an open SQLAlchemy session (from get_db in database.py).
    #   - The `User` model is in app/models.py (you will need to import it).
    #   - `response_model=list[UserRead]` makes FastAPI turn your User
    #     objects into JSON using the UserRead schema in app/schemas.py.
    #     So you can return the User objects directly.
    #
    # Hints:
    #   - Look up "SQLAlchemy 2.0 select" and `db.scalars(...)`.
    #   - Your solution can be 1-2 lines. Delete the `raise` below.
    #
    # How to check it works:
    #   Run the migration, add a user with psql (see README), start the
    #   server and open http://localhost:8000/users.
    # ------------------------------------------------------------------
    raise HTTPException(status_code=501, detail="Not implemented yet (see TODO)")
