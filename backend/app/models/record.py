import datetime
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import RecordTypeEnum
from app.ext.db import db


class Record(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[RecordTypeEnum]
    type_id: Mapped[int]
    current: Mapped[bool]
    md5_hash: Mapped[uuid.UUID]
    data: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    url: Mapped[str]

    def __repr__(self) -> str:
        return f"<Record {self.type} {self.type_id}>"
