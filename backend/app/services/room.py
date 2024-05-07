from __future__ import annotations

import math
from typing import TYPE_CHECKING
from xml.etree import ElementTree

from app.constants import (
    CAPACITY_RATIO_MAP,
    LABEL_CAPACITY_MAP,
    MANUFACTURE_CAPACITY_MAP,
    MANUFACTURE_CAPACITY_RATIO_MAP,
    MANUFACTURE_RATE_MAP,
    MANUFACTURE_RATE_PER_HOUR_MAP,
    ROOM_SHOP_TYPE_MASK,
    ROOM_TYPE_MAP,
)
from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.utils.pss import parse_price_from_pricestring, parse_requirement

if TYPE_CHECKING:
    pass


class RoomService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._rooms: dict[int, dict] = {}
        self._rooms_by_name: dict[int, dict] = {}
        self._upgrades: dict[int, dict] = {}

    @property
    def rooms(self):
        if not self._rooms:
            self._rooms, self._upgrades, self._rooms_by_name = self.get_rooms_from_records()

        return self._rooms

    @property
    def rooms_by_name(self):
        if not self._rooms_by_name:
            self._rooms, self._upgrades, self._rooms_by_name = self.get_rooms_from_records()

        return self._rooms_by_name

    @property
    def upgrades(self):
        if not self._upgrades:
            self._rooms, self._upgrades, self._rooms_by_name = self.get_rooms_from_records()

        return self._upgrades

    def get_rooms_from_records(self) -> (dict[int, dict], dict[int, dict], dict[int, dict]):
        """Load rooms from database."""

        records = self.record_service.records[TypeEnum.ROOM]

        rooms = {}
        for record in records.values():
            room = PixelStarshipsApi.parse_room_node(ElementTree.fromstring(record.data))
            missile_design = room["MissileDesign"]

            room_price, room_price_currency = parse_price_from_pricestring(room["PriceString"])
            room_type = ROOM_TYPE_MAP.get(room["RoomType"], room["RoomType"])

            # ask Savy why...
            not_powered = (
                int(room["MaxSystemPower"]) != 0
                and int(room["ReloadTime"]) == 0
                and int(room["ManufactureCapacity"]) == 0
            )

            requirement = parse_requirement(room["RequirementString"])
            if requirement:
                if requirement["type"] == TypeEnum.ITEM:
                    requirement["object"] = self.item_service.items[requirement["id"]]
                elif requirement["type"] == TypeEnum.RESEARCH:
                    requirement["object"] = self.research_service.researches[requirement["id"]]
                else:
                    requirement["object"] = self.record_service.get_record(requirement["type"], requirement["id"])

            rooms[record.type_id] = {
                "id": record.type_id,
                "name": room["RoomName"],
                "short_name": room["RoomShortName"],
                "type": room_type,
                "level": int(room["Level"]),
                "capacity": int(room["Capacity"]) / CAPACITY_RATIO_MAP.get(room["RoomType"], 1),
                "capacity_label": LABEL_CAPACITY_MAP.get(room["RoomType"], "Capacity"),
                "range": int(room["Range"]),
                "min_range": int(room["MinRange"]),
                "height": int(room["Rows"]),
                "width": int(room["Columns"]),
                "sprite": self.sprite_service.get_sprite_infos(int(room["ImageSpriteId"])),
                "construction_sprite": self.sprite_service.get_sprite_infos(int(room["ConstructionSpriteId"])),
                "power_use": int(room["MaxSystemPower"]),
                "power_gen": int(room["MaxPowerGenerated"]),
                "power_diff": int(room["MaxSystemPower"])
                if not_powered
                else int(room["MaxPowerGenerated"]) - int(room["MaxSystemPower"]),
                "min_ship_level": int(room["MinShipLevel"]),
                "upgrade_from_id": int(room["UpgradeFromRoomDesignId"]),
                "defense": int(room["DefaultDefenceBonus"]),
                "activation_delay": int(room["ActivationDelay"]),
                "reload": int(room["ReloadTime"]),
                "refill_cost": int(room["RefillUnitCost"]),
                "show_frame": room_type not in ("Lift", "Armor", "Corridor"),
                "upgrade_cost": room_price,
                "upgrade_currency": room_price_currency,
                "upgrade_seconds": int(room["ConstructionTime"]),
                "description": room["RoomDescription"],
                "enhancement_type": room["EnhancementType"],
                "manufacture_type": room["ManufactureType"],
                "manufacture_rate": float(room["ManufactureRate"]),
                "manufacture_rate_label": MANUFACTURE_RATE_MAP.get(room["RoomType"], "Manufacture Rate"),
                "manufacture_rate_per_hour": math.ceil(float(room["ManufactureRate"]) * 3600)
                if MANUFACTURE_RATE_PER_HOUR_MAP.get(room["RoomType"], False)
                else None,
                "manufacture_capacity": int(room["ManufactureCapacity"])
                / MANUFACTURE_CAPACITY_RATIO_MAP.get(room["RoomType"], 1),
                "manufacture_capacity_label": MANUFACTURE_CAPACITY_MAP.get(room["RoomType"], None),
                "cooldown_time": int(room["CooldownTime"]),
                "requirement": requirement,
                "extension_grids": int(room.get("SupportedGridTypes", "0")) & 2 != 0,
                "has_weapon_stats": bool(missile_design),
                "purchasable": "AvailabilityMask" in room,
                "shop_type": ROOM_SHOP_TYPE_MASK.get(room["AvailabilityMask"], room["AvailabilityMask"])
                if "AvailabilityMask" in room
                else ROOM_SHOP_TYPE_MASK[None],
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
                "skin": False,
                "base_room_id": None,
                "base_room_name": None,
                "not_powered": not_powered,
            }

        upgrades = {room["upgrade_from_id"]: room_id for room_id, room in rooms.items()}

        rooms_by_name = {room["name"]: room for room_id, room in rooms.items()}

        return rooms, upgrades, rooms_by_name

    def update_rooms(self):
        """Get rooms from API and save them in database."""

        rooms = self.pixel_starships_api.get_rooms()
        still_presents_ids = []

        for room in rooms:
            record_id = int(room["RoomDesignId"])
            self.record_service.add_record(
                TypeEnum.ROOM,
                record_id,
                room["RoomName"],
                int(room["ImageSpriteId"]),
                room["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["AvailabilityMask"],
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.ROOM, still_presents_ids)
