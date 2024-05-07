from __future__ import annotations

import datetime

from app.services.base import BaseService
from app.services.item import ItemService
from app.utils.math import format_delta_time


class PixyShipService(BaseService):
    def __init__(self):
        super().__init__()

    def parse_assets_from_string(self, assets_string: str):
        """Parse RewardString from API."""

        assets = []
        if assets_string:
            assets_items = assets_string.split("|")
            for asset_item in assets_items:
                if not asset_item:
                    continue

                asset_item_unpacked = asset_item.split(":")
                asset_item_type = asset_item_unpacked[0]
                asset_item_type_id = None

                asset_item_id_count_unpacked = asset_item_unpacked[1].split("x")
                asset_item_data = asset_item_id_count_unpacked[0]

                line = {}

                # if change's a Character, get all infos of the crew
                if asset_item_type == "character":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        data = self.character_service.characters[asset_item_type_id]
                    except KeyError:
                        continue

                # if change's an Item, get all infos of the item
                elif asset_item_type == "item":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        item = self.item_service.items[asset_item_type_id]
                        data = ItemService.create_light_item(item)
                    except KeyError:
                        continue

                # if change's an Item, get all infos of the item
                elif asset_item_type == "room":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        data = self.room_service.rooms[asset_item_type_id]
                    except KeyError:
                        continue

                # if change's is Starbux, Dove, Gas or Mineral
                elif (
                    asset_item_type == "starbux"
                    or asset_item_type == "purchasePoints"
                    or asset_item_type == "points"
                    or asset_item_type == "gas"
                    or asset_item_type == "mineral"
                ):
                    data = int(asset_item_data)

                # if change's a Skin, get all infos of the crew
                elif asset_item_type == "skin":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        data = self.skin_service.skinsets[asset_item_type_id]
                    except KeyError:
                        continue

                # Unknown type
                else:
                    continue

                asset_item_count = 1
                if len(asset_item_id_count_unpacked) > 1:
                    # TODO @solevis: handle count based in IAP value, for now ignore it
                    # https://github.com/solevis/pixyship/issues/114
                    asset_item_count = None if "[USD/" in assets_string else int(asset_item_id_count_unpacked[1])

                line.update(
                    {
                        "count": asset_item_count,
                        "data": data,
                        "id": asset_item_type_id,
                        "type": asset_item_type,
                    },
                )

                assets.append(line)

        return assets

    @staticmethod
    def get_tournament_infos():
        utc_now = datetime.datetime.now(tz=datetime.UTC)
        first_day_next_month = (utc_now.date().replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        tournament_start = first_day_next_month - datetime.timedelta(days=7)
        tournament_start_time = datetime.datetime(
            tournament_start.year,
            tournament_start.month,
            tournament_start.day,
            tzinfo=datetime.UTC,
        )
        tournament_left_delta = tournament_start_time - utc_now
        tournament_left_formatted = format_delta_time(tournament_left_delta)

        return {
            "start": tournament_start,
            "end": first_day_next_month,
            "left": tournament_left_formatted.strip(),
            "started": tournament_left_delta.total_seconds() < 0,
        }
