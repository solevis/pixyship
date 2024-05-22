from functools import cached_property
from xml.etree import ElementTree

from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class MissileService(BaseService):
    """Service to manage missiles."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()

    @cached_property
    @cache.cached(key_prefix="missiles")
    def missiles(self) -> dict[int, dict]:
        """Get missiles data."""
        return self.get_missiles_from_records()

    def get_missiles_from_records(self) -> dict[int, dict]:
        """Load missiles from database."""
        records = self.record_service.records[TypeEnum.MISSILE]

        missiles = {}
        for record in records.values():
            missile = PixelStarshipsApi.parse_missile_node(ElementTree.fromstring(record.data))
            missile_design = missile["MissileDesign"]

            missiles[record.type_id] = {
                "id": record.type_id,
                "name": missile["ItemDesignName"],
                "build_time": int(missile["BuildTime"]),
                "reload_modifier": int(missile["ReloadModifier"]) if "ReloadModifier" in missile else None,
                "manufacture_cost": self.pixyship_service.parse_assets_from_string(missile["ManufactureCost"]),
                "sprite": self.sprite_service.get_sprite_infos(int(missile["ImageSpriteId"])),
                "system_damage": float(missile_design["SystemDamage"]) if missile_design else 0,
                "hull_damage": float(missile_design["HullDamage"]) if missile_design else 0,
                "character_damage": float(missile_design["CharacterDamage"]) if missile_design else 0,
                "shield_damage": float(missile_design["ShieldDamage"]) if missile_design else 0,
                "direct_system_damage": float(missile_design["DirectSystemDamage"]) if missile_design else 0,
                "volley": float(missile_design["Volley"]) if missile_design else 0,
                "volley_delay": float(missile_design["VolleyDelay"]) if missile_design else 0,
                "speed": float(missile_design["Speed"]) if missile_design else 0,
                "fire_length": float(missile_design["FireLength"]) if missile_design else 0,
                "emp_length": float(missile_design["EMPLength"]) if missile_design else 0,
                "stun_length": float(missile_design["StunLength"]) if missile_design else 0,
                "hull_percentage_damage": float(missile_design["HullPercentageDamage"]) if missile_design else 0,
            }

        return missiles

    def update_missiles(self) -> None:
        """Get missiles from API and save them in database."""
        missiles = self.pixel_starships_api.get_missiles()
        still_presents_ids = []

        for missile in missiles:
            record_id = int(missile["ItemDesignId"])
            self.record_service.add_record(
                TypeEnum.MISSILE,
                record_id,
                missile["ItemDesignName"],
                int(missile["ImageSpriteId"]),
                missile["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["ReloadModifier"],
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.MISSILE, still_presents_ids)
