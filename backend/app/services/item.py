from xml.etree import ElementTree

from flask import current_app

from app.constants import (
    ENHANCE_MAP,
    MODULE_BONUS_RATIO_MAP,
    MODULE_ENHANCEMENT_MAP,
    RARITY_MAP,
    SHORT_ENHANCE_MAP,
    SLOT_MAP,
)
from app.enums import RecordTypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.utils.pss import has_offstat


class ItemService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._items = {}

    @property
    def items(self):
        if not self._items:
            self._items = self.get_items_from_records()

        return self._items

    def get_items_from_records(self):
        """Get items from database."""

        records = self.record_service.get_records_from_type(RecordTypeEnum.ITEM)

        items = {}
        for record in records.values():
            current_app.logger.debug(f"Loading item {record.type_id} from database")
            item_node = ElementTree.fromstring(record.data)
            item = PixelStarshipsApi.parse_item_node(item_node)

            number_of_rewards = 0
            if item["Content"] and float(item["ModuleArgument"]) != 0:
                number_of_rewards = item["ModuleArgument"]

            module_extra_enhancement = self.parse_module_extra_enhancement(item)

            slot = SLOT_MAP.get(item["ItemSubType"], item["ItemSubType"])
            item_type = item.get("ItemType")
            rarity_order = RARITY_MAP[item["Rarity"]]
            bonus = float(item.get("EnhancementValue"))
            disp_enhancement = ENHANCE_MAP.get(item["EnhancementType"], item["EnhancementType"])
            offstat = has_offstat(item_type, slot, rarity_order, bonus, disp_enhancement)

            items[record.type_id] = {
                "name": item["ItemDesignName"],
                "description": item["ItemDesignDescription"],
                "sprite": self.sprite_service.get_sprite_infos(int(item["ImageSpriteId"])),
                "logo_sprite": self.sprite_service.get_sprite_infos(int(item["LogoSpriteId"])),
                "slot": slot,
                "enhancement": item.get("EnhancementType").lower(),
                "disp_enhancement": disp_enhancement,
                "short_disp_enhancement": SHORT_ENHANCE_MAP.get(item["EnhancementType"], item["EnhancementType"]),
                "bonus": bonus,
                "module_extra_enhancement": module_extra_enhancement["enhancement"],
                "module_extra_disp_enhancement": module_extra_enhancement["disp_enhancement"],
                "module_extra_short_disp_enhancement": module_extra_enhancement["short_disp_enhancement"],
                "module_extra_enhancement_bonus": module_extra_enhancement["bonus"],
                "type": item_type,
                "rarity": item.get("Rarity").lower(),
                "rarity_order": rarity_order,
                "has_offstat": offstat,
                "ingredients": item["Ingredients"],
                "content_string": item["Content"],
                "number_of_rewards": number_of_rewards,
                "market_price": int(item["MarketPrice"]),
                "fair_price": int(item["FairPrice"]),
                "prices": self.market_service.prices.get(int(item["ItemDesignId"])),
                "training": self.training_service.trainings.get(int(item["TrainingDesignId"])),
                "id": record.type_id,
                "saleable": (int(item["Flags"]) & 1) != 0,
                "item_space": int(item["ItemSpace"]),
                "requirement": item["RequirementString"],
            }

        # Second pass required for self references
        for item in items.values():
            item["recipe"] = self.parse_item_ingredients(item["ingredients"], items)

        # Third pass required for self references
        for item in items.values():
            item["content"] = self.parse_item_content(item["content_string"], item, items)

        return items

    @staticmethod
    def create_light_item(item, items=None):
        return {
            "id": item["id"],
            "name": item["name"],
            "sprite": item["sprite"],
            "rarity": item["rarity"],
            "rarity_order": item["rarity_order"],
            "has_offstat": item["has_offstat"],
            "slot": item["slot"],
            "type": item["type"],
            "disp_enhancement": item["disp_enhancement"],
            "short_disp_enhancement": item["short_disp_enhancement"],
            "bonus": item["bonus"],
            "module_extra_disp_enhancement": item["module_extra_disp_enhancement"],
            "module_extra_short_disp_enhancement": item["module_extra_short_disp_enhancement"],
            "module_extra_enhancement_bonus": item["module_extra_enhancement_bonus"],
            "prices": item["prices"],
            "content": item["content"] if "content" in item else None,
            "recipe": item["recipe"] if not items else ItemService.parse_item_ingredients(item["ingredients"], items),
            "training": item["training"],
        }

    @staticmethod
    def parse_item_ingredients(ingredients_string, items):
        """Parse recipe infos from API."""

        recipe = []
        if ingredients_string:
            ingredients = [i.split("x") for i in ingredients_string.split("|")]
            for ingredient in ingredients:
                # replace hack, 2021 easter event come with additional 'item:' prefix
                ingredient_item_id = ingredient[0].replace("item:", "")

                item = items.get(int(ingredient_item_id))

                if item:
                    line = ItemService.create_light_item(item, items)
                    line["count"] = int(ingredient[1])

                    recipe.append(line)

        return recipe

    def parse_item_content(self, item_content_string, last_item, items):
        """Parse content infos from API."""

        content = []
        if item_content_string:
            content_items = item_content_string.split("|")
            for content_item in content_items:
                if not content_item:
                    continue

                content_item_unpacked = content_item.split(":")
                if len(content_item_unpacked) < 2:
                    continue

                content_item_type = content_item_unpacked[0]

                content_item_id_count_unpacked = content_item_unpacked[1].split("x")
                content_item_id = content_item_id_count_unpacked[0]

                content_item_count = 1

                # if content's a Character, get all infos of the crew
                if content_item_type == "character":
                    try:
                        content_item_data = self.character_service.characters[int(content_item_id)]
                        if len(content_item_id_count_unpacked) > 1:
                            content_item_count = int(content_item_id_count_unpacked[1])
                    except KeyError:
                        continue

                # if content's an Item, get all infos of the item
                elif content_item_type == "item":
                    try:
                        item = items.get(int(content_item_id))
                        if len(content_item_id_count_unpacked) > 1:
                            content_item_count = int(content_item_id_count_unpacked[1])
                    except KeyError:
                        continue

                    content_item_data = self.create_light_item(item)

                    # avoid infinite recursion when item reward can be the item itself
                    if last_item["id"] != item["id"]:
                        content_item_data["content"] = self.parse_item_content(item["content_string"], item, items)

                # if content's is Starbux
                elif content_item_type == "starbux":
                    content_item_data = None
                    content_item_id = None
                    content_item_count = int(content_item_unpacked[1])

                # if content's is Dove
                elif content_item_type == "purchasePoints" or content_item_type == "points":
                    content_item_data = None
                    content_item_id = None
                    content_item_count = int(content_item_unpacked[1])

                # if content's is Skin
                elif content_item_type == "skin":
                    try:
                        content_item_data = self.skin_service.skinsets[int(content_item_id)]
                        if len(content_item_id_count_unpacked) > 1:
                            content_item_count = int(content_item_id_count_unpacked[1])
                    except KeyError:
                        continue

                # Unknown type
                else:
                    continue

                line = {
                    "type": content_item_type,
                    "id": content_item_id,
                    "data": content_item_data,
                    "count": content_item_count,
                }

                content.append(line)

        return content

    @staticmethod
    def parse_module_extra_enhancement(item):
        """Parse module extra enhancement from a given item."""

        module_type = item["ModuleType"]

        # XP books have ModuleArgument but no ModuleType
        if item["ItemSubType"] == "InstantXP":
            module_type = "XP"

        enhancement = MODULE_ENHANCEMENT_MAP.get(module_type, None)
        disp_enhancement = ENHANCE_MAP.get(enhancement, enhancement)
        short_disp_enhancement = (SHORT_ENHANCE_MAP.get(enhancement, enhancement),)

        bonus = 0
        if float(item["ModuleArgument"]) != 0:
            bonus = float(item["ModuleArgument"]) / MODULE_BONUS_RATIO_MAP.get(module_type, 1)

        return {
            "enhancement": enhancement,
            "disp_enhancement": disp_enhancement,
            "short_disp_enhancement": short_disp_enhancement,
            "bonus": bonus,
        }

    def get_item_upgrades(self, item_id: int):
        upgrades = []

        for current_item_id in self.items.keys():
            item = self.items[current_item_id]

            if not item["recipe"]:
                continue

            for recipe_item in item["recipe"]:
                if recipe_item["id"] == item_id:
                    upgrades.append(ItemService.create_light_item(item))

        return upgrades

    def update_items(self):
        """Get items from API and save them in database."""

        items = self.pixel_starships_api.get_items()
        still_presents_ids = []

        for item in items:
            record_id = int(item["ItemDesignId"])
            self.record_service.add_record(
                RecordTypeEnum.ITEM,
                record_id,
                item["ItemDesignName"],
                int(item["ImageSpriteId"]),
                item["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["FairPrice", "MarketPrice", "BuildPrice"],
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(RecordTypeEnum.ITEM, still_presents_ids)
