from xml.etree import ElementTree

from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class AchievementService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._achievements = {}

    @property
    def achievements(self):
        if not self._achievements:
            self._achievements = self.get_achievements_from_db()

        return self._achievements

    def get_achievements_from_db(self):
        """Load achievements from database."""

        records = self.record_service.records[TypeEnum.ACHIEVEMENT]

        achievements = {}
        all_parent_achievement_design_id = []

        for record in records.values():
            achievement = PixelStarshipsApi.parse_achievement_node(ElementTree.fromstring(record.data))

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

    def update_achievements(self):
        """Update data and save records."""

        achievements = self.pixel_starships_api.get_achievements()
        still_presents_ids = []

        for achievement in achievements:
            record_id = int(achievement["AchievementDesignId"])
            self.record_service.add_record(
                TypeEnum.ACHIEVEMENT,
                record_id,
                achievement["AchievementTitle"],
                int(achievement["SpriteId"]),
                achievement["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.ACHIEVEMENT, still_presents_ids)
