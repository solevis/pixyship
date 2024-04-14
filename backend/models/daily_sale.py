import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped

from db import db


class DailySale(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    type_id: Mapped[int]
    sale_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    sale_from: Mapped[str]
    currency: Mapped[Optional[str]]
    price: Mapped[Optional[int]]

    __table_args__ = (UniqueConstraint("type", "type_id", "sale_at", "sale_from", name="uq_daily_sale"),)

    def __repr__(self) -> str:
        return f"<DailySale {self.id}>"
