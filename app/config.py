import os
from dataclasses import dataclass

# SQLite is used initially for development purposes.
@dataclass
class Config:
    # If DATABASE_URL is not set, default to a local SQLite database.
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "sqlite:///clans.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

