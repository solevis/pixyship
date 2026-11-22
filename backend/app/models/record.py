import datetime
import uuid

from sqlalchemy import Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import TypeEnum
from app.ext.db import db


class Record(db.Model):  # type: ignore[name-defined]
    """Record model."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    sprite_id: Mapped[int] = mapped_column(nullable=True)
    # the Postgres type is named type_enum (see migrations), not typeenum as derived from the class name
    type: Mapped[TypeEnum] = mapped_column(Enum(TypeEnum, name="type_enum"))
    type_id: Mapped[int]
    current: Mapped[bool]
    md5_hash: Mapped[uuid.UUID]
    data: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    url: Mapped[str]

    def __repr__(self) -> str:
        """Return a string representation of the record."""
        return f"<Record {self.type} {self.type_id}>"
