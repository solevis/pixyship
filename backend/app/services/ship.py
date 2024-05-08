import html
import time
from xml.etree import ElementTree

from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.utils.pss import parse_requirement


class ShipService(BaseService):
    """Service to manage ships."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._ships: dict[int, dict] = {}

    @property
    def ships(self) -> dict[int, dict]:
        """Get ships data."""
        if not self._ships:
            self._ships = self.get_ships_from_records()

        return self._ships

    def get_ships_from_records(self) -> dict[int, dict]:
        """Load ships from database."""
        records = self.record_service.get_records_from_type(TypeEnum.SHIP)

        ships = {}
        for record in records.values():
            ship = PixelStarshipsApi.parse_ship_node(ElementTree.fromstring(record.data))
            starbux_cost, mineral_cost, points_cost, items_cost = self.parse_ship_unlock_costs(
                ship["MineralCost"],
                ship["StarbuxCost"],
                ship["UnlockCost"],
            )

            ships[record.type_id] = {
                "id": record.type_id,
                "name": ship["ShipDesignName"],
                "description": ship["ShipDescription"],
                "level": int(ship["ShipLevel"]),
                "hp": int(ship["Hp"]),
                "repair_time": int(ship["RepairTime"]),
                "full_repair_time": time.strftime("%H:%M:%S", time.gmtime(int(ship["RepairTime"]) * int(ship["Hp"]))),
                "exterior_sprite": self.sprite_service.get_sprite_infos(int(ship["ExteriorSpriteId"])),
                "interior_sprite": self.sprite_service.get_sprite_infos(int(ship["InteriorSpriteId"])),
                "logo_sprite": self.sprite_service.get_sprite_infos(int(ship["LogoSpriteId"])),
                "sprite": self.sprite_service.get_sprite_infos(int(ship["MiniShipSpriteId"])),
                "frame_sprite": self.sprite_service.get_sprite_infos(int(ship["RoomFrameSpriteId"])),
                "left_door_sprite": self.sprite_service.get_sprite_infos(int(ship["DoorFrameLeftSpriteId"])),
                "right_door_sprite": self.sprite_service.get_sprite_infos(int(ship["DoorFrameRightSpriteId"])),
                "rows": int(ship["Rows"]),
                "columns": int(ship["Columns"]),
                "race_id": int(ship["RaceId"]),
                "mask": ship["Mask"],
                "mineral_cost": mineral_cost,
                "starbux_cost": starbux_cost,
                "points_cost": points_cost,
                "items_cost": items_cost,
                "mineral_capacity": ship["MineralCapacity"],
                "gas_capacity": ship["GasCapacity"],
                "equipment_capacity": ship["EquipmentCapacity"],
                "ship_type": ship["ShipType"],
                "requirements": self.parse_ship_requirement(ship["RequirementString"]),
            }

        return ships

    def parse_ship_unlock_costs(
        self, mineral_cost_string: str, starbux_cost_string: str, unlock_cost_string: str
    ) -> tuple[int, int, int, list]:
        """Parse ship unlock cost infos from API."""
        starbux_cost = 0
        mineral_cost = 0
        points_cost = 0
        items_cost = []

        if unlock_cost_string:
            costs = unlock_cost_string.split("|")
            for cost in costs:
                cost_type, cost_value = cost.split(":")

                if cost_type == "starbux":
                    starbux_cost = int(cost_value)
                    continue

                if cost_type == "mineral":
                    mineral_cost = int(cost_value)
                    continue

                if cost_type == "points":
                    points_cost = int(cost_value)
                    continue

                if cost_type == "item":
                    item = self.item_service.items.get(int(cost_value))

                    if item:
                        item_cost = self.item_service.create_light_item(item)
                        items_cost.append(item_cost)

                    continue
        else:
            # no UnlockCost, use MineralCost and StarbuxCost
            starbux_cost = int(starbux_cost_string)
            mineral_cost = int(mineral_cost_string)

        return starbux_cost, mineral_cost, points_cost, items_cost

    def parse_ship_requirement(self, requirements_string: str) -> list | None:
        """Parse several requirements assets."""
        if not requirements_string:
            return None

        requirements_string = html.unescape(requirements_string)
        unparsed_requirements = requirements_string.split("&&")

        return [self.parse_requirement(unparsed_requirement.strip()) for unparsed_requirement in unparsed_requirements]

    def update_ships(self) -> None:
        """Get ships from API and save them in database."""
        ships = self.pixel_starships_api.get_ships()
        still_presents_ids = []

        for ship in ships:
            record_id = int(ship["ShipDesignId"])
            self.record_service.add_record(
                TypeEnum.SHIP,
                record_id,
                ship["ShipDesignName"],
                int(ship["MiniShipSpriteId"]),
                ship["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SHIP, still_presents_ids)

    def parse_requirement(self, requirement_string: str) -> dict | None:
        """Parse requirement asset."""
        requirement = parse_requirement(requirement_string)

        if requirement:
            if requirement["type"] == TypeEnum.ROOM:
                requirement["object"] = self.room_service.rooms[requirement["id"]]
            else:
                record = self.record_service.get_record(requirement["type"], requirement["id"])
                if record:
                    requirement["object"] = {
                        "id": record.type_id,
                        "name": record.name,
                    }

        return requirement
