import hashlib
import uuid
from functools import cached_property
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

from flask import current_app
from sqlalchemy import func

from app.enums import TypeEnum
from app.ext.db import db
from app.models import Record
from app.services.base import BaseService
from app.utils.xml_helpers import sort_attributes


class RecordService(BaseService):
    """Service to manage records."""

    def __init__(self) -> None:
        super().__init__()
        self._current_records: dict[TypeEnum, dict[int, Record]] = {}

    @cached_property
    def records(self) -> dict[TypeEnum, dict[int, Record]]:
        """Get records data."""
        records: dict[TypeEnum, dict[int, Record]] = {}
        current_records: list[Record] = Record.query.filter_by(current=True).all()

        for record in current_records:
            db.session.expunge(record)
            if record.type not in records:
                records[record.type] = {}

            records[record.type][record.type_id] = record

        return records

    @staticmethod
    def get_records_from_type(record_type: TypeEnum) -> list[Record]:
        """Get records from given PSS API type (LimitedCatalogType for example)."""
        return Record.query.filter_by(current=True, type=record_type).order_by(Record.type_id).all()

    def get_record(self, record_type: TypeEnum, record_type_id: int, reload_on_error: bool = True) -> Record | None:
        """Get PixyShip record from given PSS API type (LimitedCatalogType for example)."""
        try:
            return self.records[record_type][record_type_id]
        except KeyError:
            # happens when there's new things, reload the records from the database (drop the cached_property)
            if reload_on_error:
                self.__dict__.pop("records", None)
                return self.get_record(record_type, record_type_id, False)

            current_app.logger.warning("Cannot find record of type %s with id %d", record_type, record_type_id)
            return None

    def get_record_name(self, record_type: TypeEnum, type_id: int, reload_on_error: bool = True) -> str | None:
        """Get sprite date for the given record ID."""
        record = self.get_record(record_type, type_id, reload_on_error)
        if record is None:
            return None

        return record.name

    def get_current_records_by_type_id(self, record_type: TypeEnum) -> dict[int, Record]:
        """Get current records of the given type by type_id, loaded with a single query and kept until committed."""
        if record_type not in self._current_records:
            records = Record.query.filter_by(type=record_type, current=True).all()
            self._current_records[record_type] = {record.type_id: record for record in records}

        return self._current_records[record_type]

    def add_record(
        self,
        record_type: TypeEnum,
        record_id: int,
        record_name: str,
        record_sprite_id: int,
        raw_data: Element | str,
        url: str,
        ignore_list: list[str] | None = None,
    ) -> None:
        """Add a record to the session with hash, committed by purge_old_records() at the end of the import."""
        ignore_list = ignore_list or []

        if isinstance(raw_data, Element):
            # since python 3.8, attrib order is now preserved, but we need a sorted order for legacy comparaisons
            sort_attributes(raw_data)

            # data to be stored in database
            data: str = ET.tostring(raw_data).decode()

            # ignore some fields for hashing
            for i in ignore_list:
                raw_data.attrib.pop(i, None)

            # hash
            md5_str = ET.tostring(raw_data).decode().replace("\n", " ")
        else:
            data = raw_data
            md5_str = data

        md5_hash = hashlib.md5(md5_str.encode("utf-8")).hexdigest()

        # check if this is already in the db as the current
        current_records = self.get_current_records_by_type_id(record_type)
        existing = current_records.get(record_id)

        if existing:
            # hash is stored as uuid with extra dashes, remove them when comparing hashes
            if str(existing.md5_hash).replace("-", "") == md5_hash:
                # if we ignored fields, update them, but don't make a new record.
                if ignore_list and existing.data != data:
                    existing.data = data

                # if we haven't a name, add it
                if not existing.name or existing.name != record_name:
                    existing.name = record_name

                # if we haven't a sprite id, add it
                if not existing.sprite_id or existing.sprite_id != record_sprite_id:
                    existing.sprite_id = record_sprite_id

                return

            # new hash and data, previous record is no more the current
            existing.current = False

        # create the new record
        new_record = Record(
            type=record_type,
            type_id=record_id,
            current=True,
            md5_hash=uuid.UUID(md5_hash),
            data=data,
            url=url,
            name=record_name,
            sprite_id=record_sprite_id,
        )

        db.session.add(new_record)
        current_records[record_id] = new_record

    def purge_old_records(self, record_type: TypeEnum, still_presents_ids: list[int]) -> None:
        """Disable old records not presents in API anymore, and commit all the records added for this type."""
        if not still_presents_ids:
            # most likely an API error, don't disable every record of this type
            current_app.logger.warning("No %s records retrieved from API, not purging old records", record_type)
        else:
            current_ids = set(self.get_current_records_by_type_id(record_type))
            no_more_presents_ids = current_ids - set(still_presents_ids)

            if no_more_presents_ids:
                db.session.query(Record).filter(
                    Record.type == record_type,
                    Record.current.is_(True),
                    Record.type_id.in_(no_more_presents_ids),
                ).update({Record.current: False}, synchronize_session=False)

        db.session.commit()
        self._current_records.pop(record_type, None)

    def get_record_sprite_id(self, record_type: TypeEnum, type_id: int) -> int | None:
        """Get sprite date for the given record ID."""
        record = self.get_record(record_type, type_id)
        if record is None:
            return None

        return record.sprite_id

    @staticmethod
    def get_last_prestige_record() -> Record | None:
        """Get last prestige record."""
        return db.session.query(func.max(Record.created_at)).filter_by(type=TypeEnum.PRESTIGE, current=True).first()
