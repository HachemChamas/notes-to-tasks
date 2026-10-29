"""The FastAPI application: creates the app and plugs in every endpoint.

Run it locally (from the backend/ folder) with:
    uvicorn app.main:app --reload
Then open http://localhost:8000/docs to try the endpoints in your browser.
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.database import check_database
from app.routers import extract, tasks, users

app = FastAPI(
    title="notes-to-tasks API",
    description="Turn meeting notes into tasks on a shared board.",
)

# CORS: the frontend (localhost:5173) and backend (localhost:8000) count as
# different "origins", so the browser blocks the frontend's requests unless
# the backend says that origin is allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

# The endpoints live in app/routers/, grouped by topic.
app.include_router(extract.router)
app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/health", tags=["health"])
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
