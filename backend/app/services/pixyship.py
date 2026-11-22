from __future__ import annotations

import datetime

from app.services.base import BaseService
from app.services.item import ItemService
from app.utils.calculation import format_delta_time
from app.utils.pss import parse_assets_string

CURRENCY_ASSET_TYPES = ("starbux", "purchasePoints", "points", "gas", "mineral")


class PixyShipService(BaseService):
    """Service to manage PixyShip specific features."""

    def __init__(self) -> None:
        super().__init__()

    def parse_assets_from_string(self, assets_string: str) -> list[dict]:
        """Parse RewardString from API, with the data of each asset."""
        assets = []
        for asset in parse_assets_string(assets_string):
            asset_type = asset["type"]
            asset_type_id: int | None = asset["id"]

            try:
                if asset_type == "character":
                    data: dict | int | None = self.character_service.characters[asset["id"]]
                elif asset_type == "item":
                    data = ItemService.create_light_item(self.item_service.items[asset["id"]])
                elif asset_type == "room":
                    data = self.room_service.rooms[asset["id"]]
                elif asset_type == "skin":
                    data = self.skin_service.skinsets[asset["id"]]
                elif asset_type in CURRENCY_ASSET_TYPES:
                    # the "id" is the amount
                    data = asset["id"]
                    asset_type_id = None
                else:
                    # unknown type
                    continue
            except KeyError:
                continue

            # TODO @solevis: handle count based in IAP value, for now ignore it
            # https://github.com/solevis/pixyship/issues/114
            asset_count = asset["count"]
            if asset_count is None:
                asset_count = None if "[USD/" in assets_string else 1

            assets.append(
                {
                    "count": asset_count,
                    "data": data,
                    "id": asset_type_id,
                    "type": asset_type,
                },
            )

        return assets

    @staticmethod
    def get_tournament_infos() -> dict:
        """Get infos about the next tournament."""
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
