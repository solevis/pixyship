from sqlalchemy.orm import mapped_column, Mapped

from db import db


class Alliance(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    sprite_id: Mapped[int]

    def __repr__(self) -> str:
        return f"<Alliance {self.name}>"
