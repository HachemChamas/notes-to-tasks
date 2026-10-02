"""Database connection.

- `engine` holds the connection to Postgres (a pool of reusable connections).
- `get_db()` gives each request its own session and closes it afterwards.
- `check_database()` answers "can we reach Postgres right now?".
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

# Creating the engine does NOT connect yet. The first connection is opened
# the first time we run a query. connect_timeout stops a request from
# hanging for a long time if Postgres is unreachable.
engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})

# A "session" is how we run queries with SQLAlchemy models.
# SessionLocal() creates a new one.
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """FastAPI dependency that gives an endpoint a database session.

    Use it like this:
        def my_endpoint(db: Session = Depends(get_db)): ...

    The code after `yield` runs once the request is finished, so the
    session is always closed, even if the endpoint raised an error.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database() -> bool:
    """Return True if Postgres answers a trivial query, False otherwise."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as error:
        logger.warning("Database check failed: %s", error)
        return False
