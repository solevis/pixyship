from xml.etree import ElementTree

from flask import current_app

from app.constants import COLLECTION_ABILITY_MAP, COLLECTION_ABILITY_TRIGGER_MAP
from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class CollectionService(BaseService):
    """Service to manage collections."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._collections: dict[int, dict] = {}

    @property
    def collections(self) -> dict[int, dict]:
        """Get collections data."""
        if not self._collections:
            self._collections = self.get_collections_from_records()

        return self._collections

    def get_collections_from_records(self) -> dict[int, dict]:
        """Load collections from database."""
        records = self.record_service.records[TypeEnum.COLLECTION]

        collections = {}
        for record in records.values():
            collection_node = ElementTree.fromstring(record.data)
            collection = PixelStarshipsApi.parse_collection_node(collection_node)

            collections[record.type_id] = {
                "id": int(collection["CollectionDesignId"]),
                "name": collection["CollectionName"],
                "min": int(collection["MinCombo"]),
                "max": int(collection["MaxCombo"]),
                "base_enhancement": int(collection["BaseEnhancementValue"]),
                "sprite": self.sprite_service.get_sprite_infos(int(collection["SpriteId"])),
                "step_enhancement": float(collection["StepEnhancementValue"]),
                "icon_sprite": self.sprite_service.get_sprite_infos(int(collection["IconSpriteId"])),
                "chars": [],
                "ability_name": self.get_collection_ability_name(collection["EnhancementType"]),
                "trigger": self.get_collection_trigger_name(collection["TriggerType"]),
                "base_chance": int(collection["BaseChance"]),
                "step_chance": int(collection["StepChance"]),
                "max_use": int(collection["MaxUse"]),
                "description": collection["CollectionDescription"],
            }

        return collections

    @staticmethod
    def get_collection_trigger_name(trigger_type: str) -> str:
        """Get collection trigger name."""
        trigger_name = COLLECTION_ABILITY_TRIGGER_MAP.get(trigger_type)
        if trigger_name is None:
            current_app.logger.warning("Unknown collection trigger type: %s", trigger_type)
            return trigger_type

        return trigger_name

    @staticmethod
    def get_collection_ability_name(enhancement: str) -> str:
        """Get collection ability name."""
        ability_map_get = COLLECTION_ABILITY_MAP.get(enhancement)
        if ability_map_get is None:
            current_app.logger.warning("Unknown collection ability enhancement: %s", enhancement)
            return enhancement

        return ability_map_get

    def update_collections(self) -> None:
        """Get collections from API and save them in database."""
        collections = self.pixel_starships_api.get_collections()
        still_presents_ids = []

        for collection in collections:
            record_id = int(collection["CollectionDesignId"])
            self.record_service.add_record(
                TypeEnum.COLLECTION,
                record_id,
                collection["CollectionName"],
                int(collection["SpriteId"]),
                collection["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.COLLECTION, still_presents_ids)
