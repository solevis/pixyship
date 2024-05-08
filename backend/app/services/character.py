from xml.etree import ElementTree

from app.constants import (
    ABILITY_NAME_MAP,
    ABILITY_SPRITE_MAP,
    EQUIPMENT_SLOTS,
    RARITY_MAP,
)
from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.utils.math import float_range, int_range


class CharacterService(BaseService):
    """Service to manage characters."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._characters: dict[int, dict] = {}

    @property
    def characters(self) -> dict[int, dict]:
        """Get characters data."""
        if not self._characters:
            self._characters = self.get_characters_from_records()
            self.update_character_with_collection_data()

        return self._characters

    def get_characters_from_records(self) -> dict[int, dict]:
        """Load crews from database."""
        records = self.record_service.records[TypeEnum.CHARACTER]

        characters = {}
        for record in records.values():
            character_node = ElementTree.fromstring(record.data)
            character = PixelStarshipsApi.parse_character_node(character_node)

            characters[record.type_id] = {
                "name": character["CharacterDesignName"],
                "id": record.type_id,
                "sprite": self.sprite_service.get_sprite_infos(int(character["ProfileSpriteId"])),
                "head_sprite": self.sprite_service.get_sprite_infos(
                    int(character["CharacterParts"]["Head"]["StandardSpriteId"]),
                ),
                "body_sprite": self.sprite_service.get_sprite_infos(
                    int(character["CharacterParts"]["Body"]["StandardSpriteId"]),
                ),
                "leg_sprite": self.sprite_service.get_sprite_infos(
                    int(character["CharacterParts"]["Leg"]["StandardSpriteId"]),
                ),
                "rarity": character["Rarity"].lower(),  # Sprites for gems are 1593. 1594
                "rarity_order": RARITY_MAP[character["Rarity"]],
                "hp": int_range(character, "Hp", "FinalHp"),
                "pilot": float_range(character, "Pilot", "FinalPilot"),
                "attack": float_range(character, "Attack", "FinalAttack"),
                "repair": float_range(character, "Repair", "FinalRepair"),
                "weapon": float_range(character, "Weapon", "FinalWeapon"),
                "engine": float_range(character, "Engine", "FinalEngine"),
                "research": float_range(character, "Research", "FinalResearch"),
                "science": float_range(character, "Science", "FinalScience"),
                "ability": float_range(character, "SpecialAbilityArgument", "SpecialAbilityFinalArgument"),
                "special_ability": ABILITY_NAME_MAP.get(character["SpecialAbilityType"], ""),
                "ability_sprite": self.sprite_service.get_sprite_infos(
                    ABILITY_SPRITE_MAP.get(character["SpecialAbilityType"], 110),
                ),
                "fire_resist": int(character["FireResistance"]),
                "resurrect": 0,
                "walk": int(character["WalkingSpeed"]),
                "run": int(character["RunSpeed"]),
                "training_limit": int(character["TrainingCapacity"]),
                "progression_type": character["ProgressionType"],
                "equipment": self.parse_equipment_slots(character),
                "collection": int(character["CollectionDesignId"]),
                "collection_sprite": None,
                "collection_name": "",
                "description": character["CharacterDesignDescription"],
            }

            # computed properties
            characters[record.type_id]["width"] = max(
                characters[record.type_id]["head_sprite"]["width"],
                characters[record.type_id]["body_sprite"]["width"],
                characters[record.type_id]["leg_sprite"]["width"],
            )

        return characters

    @staticmethod
    def parse_equipment_slots(character: dict) -> list[str]:
        """Determine equipments slots with character equipment mask."""
        equipment_mask = int(character["EquipmentMask"])
        output = [int(x) for x in f"{equipment_mask:06b}"]

        return [EQUIPMENT_SLOTS[5 - i] for i, b in enumerate(output) if b]

    def update_character_with_collection_data(self) -> None:
        """Updata character data with collection."""
        # update crew with collection data
        for character in self.characters.values():
            if character["collection"]:
                character["collection_sprite"] = self.collection_service.collections[character["collection"]][
                    "icon_sprite"
                ]
                character["collection_name"] = self.collection_service.collections[character["collection"]]["name"]

    def update_characters(self) -> None:
        """Get crews from API and save them in database."""
        characters = self.pixel_starships_api.get_characters()
        still_presents_ids = []

        for character in characters:
            record_id = int(character["CharacterDesignId"])
            self.record_service.add_record(
                TypeEnum.CHARACTER,
                record_id,
                character["CharacterDesignName"],
                int(character["ProfileSpriteId"]),
                character["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.CHARACTER, still_presents_ids)
