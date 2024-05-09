from sqlalchemy.orm import Mapped, mapped_column

from app.ext.db import db


class Alliance(db.Model):  # type: ignore[name-defined]
    """Alliance model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    sprite_id: Mapped[int]

    def __repr__(self) -> str:
        """Return a string representation of the alliance."""
        return f"<Alliance {self.name}>"
