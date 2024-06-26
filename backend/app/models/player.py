import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.ext.db import db


class Player(db.Model):  # type: ignore[name-defined]
    """Player model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    trophies: Mapped[int]
    alliance_id: Mapped[int | None]
    last_login_at: Mapped[datetime.datetime | None]

    def __repr__(self) -> str:
        """Return a string representation of the player."""
        return f"<Player {self.name}>"
