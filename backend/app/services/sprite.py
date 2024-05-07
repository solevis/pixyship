from xml.etree import ElementTree

from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class SpriteService(BaseService):
    """Service to manage sprites."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._sprites = {}

    @property
    def sprites(self) -> dict:
        """Get sprites data."""
        if not self._sprites:
            self._sprites = self.get_sprites_from_records()

        return self._sprites

    def get_sprite_infos(self, sprite_id: int) -> dict | None:
        """Get sprite infos from given id."""
        if not sprite_id:
            return None

        if isinstance(sprite_id, str):
            sprite_id = int(sprite_id)

        if not isinstance(sprite_id, int):
            return None

        sprite = self.sprites.get(sprite_id)
        if not sprite:
            return None

        return {
            "id": sprite_id,
            "source": sprite["image_file"],
            "x": sprite["x"],
            "y": sprite["y"],
            "width": sprite["width"],
            "height": sprite["height"],
        }

    def get_sprites_from_records(self) -> dict:
        """Load sprites from database."""
        records = self.record_service.records[TypeEnum.SPRITE]

        sprites = {}
        for record in records.values():
            sprite = PixelStarshipsApi.parse_sprite_node(ElementTree.fromstring(record.data))

            sprites[record.type_id] = {
                "image_file": int(sprite["ImageFileId"]),
                "x": int(sprite["X"]),
                "y": int(sprite["Y"]),
                "width": int(sprite["Width"]),
                "height": int(sprite["Height"]),
                "sprite_key": sprite["SpriteKey"],
            }

        return sprites

    def update_sprites(self) -> None:
        """Update data and save records."""
        sprites = self.pixel_starships_api.get_sprites()
        still_presents_ids = []

        for sprite in sprites:
            record_id = int(sprite["SpriteId"])
            self.record_service.add_record(
                TypeEnum.SPRITE,
                record_id,
                sprite["ImageFileId"],
                int(sprite["SpriteId"]),
                sprite["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SPRITE, still_presents_ids)
