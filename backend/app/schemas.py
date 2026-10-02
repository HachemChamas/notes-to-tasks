"""API schemas: the shape of the JSON the API sends and receives.

Models (models.py) describe database tables. Schemas describe JSON.
Keeping them separate means we choose exactly which fields leave the API.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    """A user as returned by the API."""

    # Lets Pydantic read the values from a SQLAlchemy User object
    # (user.id, user.email, ...) instead of only from a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    created_at: datetime
