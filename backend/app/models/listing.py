import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.ext.db import db


class Listing(db.Model):  # type: ignore[name-defined]
    """Listing model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_at: Mapped[datetime.datetime]
    item_name: Mapped[str]
    item_id: Mapped[int]
    amount: Mapped[int]
    currency: Mapped[str]
    price: Mapped[int]
    user_id: Mapped[int]
    user_name: Mapped[str]
    seller_id: Mapped[int]
    seller_name: Mapped[str]

    def __repr__(self) -> str:
        """Return a string representation of the listing."""
        return f"<Listing {self.id}>"
