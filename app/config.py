import os
from dataclasses import dataclass

# SQLite is used initially for development purposes.
@dataclass
class Config:
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "sqlite:///clans.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

