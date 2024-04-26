import datetime
import hashlib
import uuid
from typing import Any
from xml.etree import ElementTree

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import RecordTypeEnum
from app.ext.db import db
from app.utils import sort_attributes


class Record(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[RecordTypeEnum]
    type_id: Mapped[int]
    current: Mapped[bool]
    md5_hash: Mapped[uuid.UUID]
    data: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    url: Mapped[str]

    def __repr__(self) -> str:
        return f"<Record {self.type} {self.type_id}>"

    @classmethod
    def update_data(
        cls,
        record_type: RecordTypeEnum,
        record_id: int,
        raw_data: Any,
        url: str,
        ignore_list: list[str] = None,
        data_as_xml: bool = True,
    ):
        """Save a record to the DB with hash."""
        ignore_list = ignore_list or []

        if data_as_xml:
            # since python 3.8, attrib order is now preserved, but we need a sorted order for legacy comparaisons
            sort_attributes(raw_data)

            # data to be stored in database
            data = ElementTree.tostring(raw_data).decode()

            # ignore some fields for hashing
            for i in ignore_list:
                raw_data.attrib.pop(i, None)

            # hash
            md5_str = ElementTree.tostring(raw_data).decode().replace("\n", " ")
        else:
            data = raw_data
            md5_str = data

        md5_hash = hashlib.md5(md5_str.encode("utf-8")).hexdigest()

        # check if this is already in the db as the current
        existing = Record.query.filter_by(type=record_type, type_id=record_id, current=True).first()

        if existing:
            # hash is stored as uuid with extra dashes, remove them when comparing hashes
            if str(existing.md5_hash).replace("-", "") == md5_hash:
                # if we ignored fields, update them, but don't make a new record.
                if ignore_list:
                    if existing.data != data:
                        existing.data = data
                        db.session.commit()

                return
            else:
                # new hash and data, previous record is no more the current
                existing.current = False

        # create the new record and save it in database
        new_record = cls(
            type=record_type,
            type_id=record_id,
            current=True,
            md5_hash=md5_hash,
            data=data,
            url=url,
        )

        db.session.add(new_record)
        db.session.commit()

    @classmethod
    def set_not_current(cls, type_str, type_id):
        """Set record's current state to False in the DB."""

        existing = Record.query.filter_by(type=type_str, type_id=type_id, current=True).first()
        existing.current = False
        db.session.commit()

    @classmethod
    def purge_old_records(cls, record_type: RecordTypeEnum, still_presents_ids: list[int]):
        """Disable old records not presents in API."""

        current_ids = Record.query.filter_by(type=record_type, current=True).with_entities(Record.type_id).all()
        current_ids = [current_id[0] for current_id in current_ids]
        no_more_presents_ids = list(set(current_ids) - set(still_presents_ids))

        for no_more_presents_id in no_more_presents_ids:
            Record.set_not_current(record_type, no_more_presents_id)
