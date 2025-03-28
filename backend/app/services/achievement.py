from functools import cached_property
from xml.etree import ElementTree as ET

from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class AchievementService(BaseService):
    """Service to manage achievements."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def achievements(self) -> dict[int, dict]:
        """Get achievements data."""
        achievements = cache.get("achievements")
        if achievements is None:
            achievements = self.get_achievements_from_db()
            cache.set("achievements", achievements)

        return achievements

    def update_cache(self) -> None:
        """Load achievements in cache."""
        cache.set("achievements", self.get_achievements_from_db())

    def get_achievements_from_db(self) -> dict[int, dict]:
        """Load achievements from database."""
        records = self.record_service.get_records_from_type(TypeEnum.ACHIEVEMENT)

        achievements = {}
        all_parent_achievement_design_id = []

        for record in records:
            achievement = PixelStarshipsApi.parse_achievement_node(ET.fromstring(record.data))

            starbux_reward = 0
            mineral_reward = 0
            gas_reward = 0

            all_parent_achievement_design_id.append(int(achievement["ParentAchievementDesignId"]))

            reward_content = achievement["RewardString"]
            if reward_content:
                reward_type, reward_value = reward_content.split(":")
                if reward_type == "starbux":
                    starbux_reward = int(reward_value)
                elif reward_type == "mineral":
                    mineral_reward = int(reward_value)
                elif reward_type == "gas":
                    gas_reward = int(reward_value)

            achievements[record.type_id] = {
                "id": int(achievement["AchievementDesignId"]),
                "sprite": self.sprite_service.get_sprite_infos(int(achievement["SpriteId"])),
                "name": achievement["AchievementTitle"],
                "description": achievement["AchievementDescription"],
                "starbux_reward": starbux_reward,
                "mineral_reward": mineral_reward,
                "gas_reward": gas_reward,
                "max_reward": max([starbux_reward, mineral_reward, gas_reward]),
                "pin_reward": False,  # default value, defined after
            }

        # second loop to define pin's reward
        for achievement in achievements.values():
            if achievement["id"] not in all_parent_achievement_design_id:
                achievement["pin_reward"] = True

        return achievements

    def update_achievements(self) -> None:
        """Update data and save records."""
        pixel_starships_api = PixelStarshipsApi()
        achievements = pixel_starships_api.get_achievements()
        still_presents_ids = []

        for achievement in achievements:
            record_id = int(achievement["AchievementDesignId"])
            self.record_service.add_record(
                TypeEnum.ACHIEVEMENT,
                record_id,
                achievement["AchievementTitle"],
                int(achievement["SpriteId"]),
                achievement["pixyship_xml_element"],
                pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.ACHIEVEMENT, still_presents_ids)
