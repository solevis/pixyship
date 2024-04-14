import datetime
from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped

from db import db


class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    trophies: Mapped[int]
    alliance_id: Mapped[Optional[int]]
    last_login_at: Mapped[Optional[datetime.datetime]]

    def __repr__(self) -> str:
        return f"<Player {self.name}>"
