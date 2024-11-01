from functools import cached_property
from xml.etree import ElementTree as ET

from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class CraftService(BaseService):
    """Service to manage crafts."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def crafts(self) -> dict[int, dict]:
        """Get crafts data."""
        crafts = cache.get("crafts")
        if crafts is None:
            crafts = self.get_crafts_from_records()
            cache.set("crafts", crafts)

        return crafts

    def update_cache(self) -> None:
        """Load crafts in cache."""
        cache.set("crafts", self.get_crafts_from_records())

    def get_crafts_from_records(self) -> dict[int, dict]:
        """Load crafts from database."""
        records = self.record_service.get_records_from_type(TypeEnum.CRAFT)

        crafts = {}
        for record in records:
            craft = PixelStarshipsApi.parse_craft_node(ET.fromstring(record.data))
            missile_design = craft["MissileDesign"]

            crafts[record.type_id] = {
                "id": record.type_id,
                "name": craft["CraftName"],
                "flight_speed": int(craft["FlightSpeed"]),
                "reload": int(craft["Reload"]),
                "reload_modifier": int(craft["ReloadModifier"]) - 100 if "ReloadModifier" in craft else None,
                "craft_volley": int(craft["Volley"]),
                "craft_volley_delay": int(craft["VolleyDelay"]),
                "attack_distance": int(craft["AttackDistance"]),
                "attack_range": int(craft["AttackRange"]),
                "hp": int(craft["Hp"]),
                "craft_attack_type": craft["CraftAttackType"],
                "craft_target_type": craft["CraftTargetType"],
                "sprite": self.sprite_service.get_sprite_infos(int(craft["SpriteId"])),
                "volley": float(missile_design["Volley"]) if missile_design else 0,
                "volley_delay": float(missile_design["VolleyDelay"]) if missile_design else 0,
                "system_damage": float(missile_design["SystemDamage"]) if missile_design else 0,
                "hull_damage": float(missile_design["HullDamage"]) if missile_design else 0,
                "character_damage": float(missile_design["CharacterDamage"]) if missile_design else 0,
                "shield_damage": float(missile_design["ShieldDamage"]) if missile_design else 0,
                "direct_system_damage": float(missile_design["DirectSystemDamage"]) if missile_design else 0,
                "speed": float(missile_design["Speed"]) if missile_design else 0,
                "fire_length": float(missile_design["FireLength"]) if missile_design else 0,
                "emp_length": float(missile_design["EMPLength"]) if missile_design else 0,
                "stun_length": float(missile_design["StunLength"]) if missile_design else 0,
                "hull_percentage_damage": float(missile_design["HullPercentageDamage"]) if missile_design else 0,
                "aoe": float(missile_design["ExplosionRadius"]) / 100 if missile_design else None,
            }

        return crafts

    def update_crafts(self) -> None:
        """Get crafts from API and save them in database."""
        pixel_starships_api = PixelStarshipsApi()
        crafts = pixel_starships_api.get_crafts()
        still_presents_ids = []

        for craft in crafts:
            record_id = int(craft["CraftDesignId"])
            self.record_service.add_record(
                TypeEnum.CRAFT,
                record_id,
                craft["CraftName"],
                int(craft["SpriteId"]),
                craft["pixyship_xml_element"],
                pixel_starships_api.server,
                ["ReloadModifier"],
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.CRAFT, still_presents_ids)
