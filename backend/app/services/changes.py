from datetime import datetime

from flask import current_app
from sqlalchemy import text

from app.enums import TypeEnum
from app.ext import cache, db
from app.services.base import BaseService
from app.services.item import ItemService
from app.services.record import RecordService
from app.utils.pss import get_type_enum_from_string


class ChangesService(BaseService):
    def __init__(self):
        super().__init__()
        self._changes: list[dict[str, any]] = []
        self._last_prestiges_changes = None

    @property
    @cache.cached(key_prefix="changes")
    def changes(self) -> list[dict[str, any]]:
        if not self._changes:
            self._changes = self.get_changes_from_db()

        return self._changes

    @property
    @cache.cached(key_prefix="last_prestiges_changes")
    def last_prestiges_changes(self):
        if self._last_prestiges_changes is None:
            self._last_prestiges_changes = self.get_last_prestiges_changes_from_db()

        return self._last_prestiges_changes

    def get_changes_from_db(self) -> list[dict[str, any]]:
        """Get changes from database."""

        min_changes_dates_sql = f"""
            SELECT type, MIN(created_at) + INTERVAL '1 day' AS min
            FROM record
            WHERE type IN (
                           '{TypeEnum.ITEM}',
                           '{TypeEnum.SHIP}',
                           '{TypeEnum.CHARACTER}',
                           '{TypeEnum.ROOM}',
                           '{TypeEnum.SPRITE}',
                           '{TypeEnum.CRAFT}',
                           '{TypeEnum.SKINSET}'
                )
            GROUP BY type
        """

        min_changes_dates_result = db.session.execute(text(min_changes_dates_sql)).fetchall()

        min_changes_dates_conditions = [
            f"(c.type = '{record[0]}' AND o.data IS NULL AND (o.id IS NOT NULL OR c.created_at > '{record[1]}'))"
            if record[0] == "sprite"
            else f"(c.type = '{record[0]}' AND (o.id IS NOT NULL OR c.created_at > '{record[1]}'))"
            for record in min_changes_dates_result
        ]

        sql = """
            SELECT sub.name, sub.sprite_id, sub.type, sub.type_id, sub.data, sub.created_at, sub.old_data
            FROM (SELECT DISTINCT ON (c.id) c.id,
                                            c.name,
                                            c.sprite_id,
                                            c.type,
                                            c.type_id,
                                            c.data,
                                            c.created_at,
                                            o.data as old_data
                  FROM record c
                           LEFT JOIN record o ON o.type = c.type AND o.type_id = c.type_id AND o.current = FALSE
                  WHERE c.current = TRUE
                    AND ({})
                  ORDER BY c.id, o.created_at DESC) AS sub
            ORDER BY created_at DESC
            LIMIT {}
        """.format(" OR ".join(min_changes_dates_conditions), current_app.config.get("CHANGES_MAX_ASSETS", 5000))

        result = db.session.execute(text(sql)).fetchall()

        changes = [self.create_change_record(record) for record in result]

        return changes

    def create_change_record(self, record) -> dict[str, any]:
        record_name = record[0]
        record_sprite_id = record[1]
        record_type = get_type_enum_from_string(record[2])
        record_type_id = record[3]
        change_data = record[4]
        change_created_at = record[5]
        change_old_data = record[6]

        record_sprite = self.sprite_service.get_sprite_infos(record_sprite_id)

        change = {
            "type": record_type.lower(),
            "id": record_type_id,
            "name": record_name,
            "changed_at": change_created_at,
            "data": change_data,
            "old_data": change_old_data,
            "change_type": "Changed" if change_old_data else "New",
            "sprite": record_sprite,
        }

        if record_type == TypeEnum.CHARACTER:
            change["char"] = self.character_service.characters[record_type_id]
        elif record_type == TypeEnum.ITEM:
            change["item"] = ItemService.create_light_item(self.item_service.items[record_type_id])

        return change

    @staticmethod
    def get_last_prestiges_changes_from_db() -> datetime | None:
        """Get last prestiges changes date."""

        record = RecordService.get_last_prestige_record()

        if record:
            return record[0]

        return None