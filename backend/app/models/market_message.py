import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.ext.db import db


class MarketMessage(db.Model):  # type: ignore[name-defined]
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str]
    sale_id: Mapped[int] = mapped_column(unique=True)
    item_id: Mapped[int]
    user_id: Mapped[int]
    message_type: Mapped[str]
    channel_id: Mapped[str]
    activit_type: Mapped[str]
    message_date: Mapped[datetime.datetime]

    def __repr__(self) -> str:
        return f"<MarketMessage {self.id}>"
