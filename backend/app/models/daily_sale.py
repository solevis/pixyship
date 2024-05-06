import datetime

from sqlalchemy import UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import TypeEnum
from app.ext.db import db


class DailySale(db.Model):  # type: ignore[name-defined]
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[TypeEnum]
    type_id: Mapped[int]
    sale_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    sale_from: Mapped[str]
    currency: Mapped[str | None]
    price: Mapped[int | None]

    __table_args__ = (UniqueConstraint("type", "type_id", "sale_at", "sale_from", name="uq_daily_sale"),)

    def __repr__(self) -> str:
        return f"<DailySale {self.id}>"
