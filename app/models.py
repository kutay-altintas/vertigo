import uuid
from datetime import datetime, timezone
from . import db

class Clan(db.Model):
    __tablename__ = 'clans'

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(2), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    