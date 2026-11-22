import datetime

from sqlalchemy import Enum, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import TypeEnum
from app.ext.db import db


class DailySale(db.Model):  # type: ignore[name-defined]
    """Daily sale model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    # the Postgres type is named type_enum (see migrations), not typeenum as derived from the class name
    type: Mapped[TypeEnum] = mapped_column(Enum(TypeEnum, name="type_enum"))
    type_id: Mapped[int]
    sale_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    sale_from: Mapped[str]
    currency: Mapped[str | None]
    price: Mapped[int | None]

    __table_args__ = (UniqueConstraint("type", "type_id", "sale_at", "sale_from", name="uq_daily_sale"),)

    def __repr__(self) -> str:
        """Return a string representation of the daily sale."""
        return f"<DailySale {self.id}>"
