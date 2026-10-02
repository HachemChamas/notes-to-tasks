"""Alembic runs this file every time you run an `alembic` command.

Its job: connect to the database and run the migrations in versions/.
"""

from logging.config import fileConfig

from alembic import context

from app.database import engine
from app.models import Base

# Set up terminal logging using the [logger_*] sections of alembic.ini.
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

# Our table definitions. Alembic compares these with the real database
# when you run `alembic revision --autogenerate -m "..."`.
target_metadata = Base.metadata


def run_migrations() -> None:
    """Connect using the app's own engine (so DATABASE_URL comes from .env)."""
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
