import datetime
import html
import json
import math
import re
import time
from collections import Counter, defaultdict
from xml.etree import ElementTree

from flask import current_app
from sqlalchemy import desc, func, text

from app.constants import (
    ABILITY_MAP,
    BLUE_CARGO_SPRITE_ID,
    CAPACITY_RATIO_MAP,
    COLLECTION_ABILITY_MAP,
    COLLECTION_ABILITY_TRIGGER_MAP,
    DAILY_REWARDS_SPRITE_ID,
    DAILY_SALE_SPRITE_ID,
    DEFAULT_EXPIRATION_DURATION,
    ENHANCE_MAP,
    EQUIPMENT_SLOTS,
    GREEN_CARGO_SPRITE_ID,
    IAP_NAMES,
    LABEL_CAPACITY_MAP,
    MANUFACTURE_CAPACITY_MAP,
    MANUFACTURE_CAPACITY_RATIO_MAP,
    MANUFACTURE_RATE_MAP,
    MANUFACTURE_RATE_PER_HOUR_MAP,
    MODULE_BONUS_RATIO_MAP,
    MODULE_ENHANCEMENT_MAP,
    RACE_SPECIFIC_SPRITE_MAP,
    RACES,
    RARITY_MAP,
    RESEARCH_TYPE_MAP,
    ROOM_SHOP_TYPE_MASK,
    ROOM_TYPE_MAP,
    SALE_FROM_MAP,
    SHOP_SPRITE_ID,
    SHORT_ENHANCE_MAP,
    SLOT_MAP,
)
from app.enums import RecordTypeEnum
from app.ext.db import db
from app.models import Alliance, DailySale, Listing, Player, Record
from app.pixelstarshipsapi import PixelStarshipsApi
from app.utils import (
    Singleton,
    compute_pvp_ratio,
    float_range,
    format_delta_time,
    get_type_enum_from_string,
    has_offstat,
    int_range,
)


class PixyShip(metaclass=Singleton):
    """
    PixyShip class to handle all data from Pixel Starships.
    TODO: refactor this class to split the code into smaller classes.
    """

    def __init__(self):
        self.__records: list[Record] = []
        self._changes = None
        self._last_prestiges_changes = None
        self._characters = None
        self._collections = None
        self._dailies = None
        self._star_system_merchant_markers = None
        self._situations = None
        self._promotions = None
        self._items = None
        self._prestiges = None
        self._researches = None
        self._prices = None
        self._trainings = None
        self._achievements = None
        self._rooms = None
        self._skins = None
        self._skinsets = None
        self._crafts = None
        self._missiles = None
        self._ships = None
        self._sprites = None
        self._upgrades = None
        self._rooms_by_name = None
        self._pixel_starships_api = None
        self._data_expiration = {}

    @property
    def records(self) -> list[Record]:
        if not self.__records or self.expired("record"):
            self.__records = Record.query.filter_by(current=True).all()
            self.expire_at("record", DEFAULT_EXPIRATION_DURATION)

        return self.__records

    @property
    def pixel_starships_api(self):
        if self._pixel_starships_api is None or self.expired("api"):
            self._pixel_starships_api = PixelStarshipsApi()
            self.expire_at("api", 60 * 60 * 12)  # 12h

        return self._pixel_starships_api

    @property
    def sprites(self):
        if self._sprites is None or self.expired("sprite"):
            self._sprites = self._get_sprites_from_db()
            self.expire_at("sprite", DEFAULT_EXPIRATION_DURATION)

        return self._sprites

    @property
    def skins(self):
        if self._skins is None or self.expired("skin"):
            self._skins = self._get_skins_from_db()
            self.expire_at("skin", DEFAULT_EXPIRATION_DURATION)

        return self._skins

    @property
    def skinsets(self):
        if self._skinsets is None or self.expired("skinset"):
            self._skinsets = self._get_skinsets_from_db()
            self.expire_at("skinset", DEFAULT_EXPIRATION_DURATION)

        return self._skinsets

    @property
    def prices(self):
        if self._prices is None or self.expired("prices"):
            self._prices = self._get_prices_from_db()
            self.expire_at("prices", DEFAULT_EXPIRATION_DURATION)

        return self._prices

    @property
    def trainings(self):
        if self._trainings is None or self.expired("trainings"):
            self._trainings = self._get_trainings_from_db()
            self.expire_at("trainings", DEFAULT_EXPIRATION_DURATION)

        return self._trainings

    @property
    def achievements(self):
        if self._achievements is None or self.expired("achievements"):
            self._achievements = self._get_achievements_from_db()
            self.expire_at("achievements", DEFAULT_EXPIRATION_DURATION)

        return self._achievements

    @property
    def ships(self):
        if self._ships is None or self.expired("ship"):
            self._ships = self._get_ships_from_db()
            self.expire_at("ship", DEFAULT_EXPIRATION_DURATION)

        return self._ships

    @property
    def rooms(self):
        if self._rooms is None or self.expired("room"):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at("room", DEFAULT_EXPIRATION_DURATION)

        return self._rooms

    @property
    def rooms_by_name(self):
        if self._rooms_by_name is None or self.expired("room"):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at("room", DEFAULT_EXPIRATION_DURATION)

        return self._rooms_by_name

    @property
    def crafts(self):
        if self._crafts is None or self.expired("craft"):
            self._crafts = self._get_crafts_from_db()
            self.expire_at("craft", DEFAULT_EXPIRATION_DURATION)

        return self._crafts

    @property
    def missiles(self):
        if self._missiles is None or self.expired("missile"):
            self._missiles = self._get_missiles_from_db()
            self.expire_at("craft", DEFAULT_EXPIRATION_DURATION)

        return self._missiles

    @property
    def researches(self):
        if self._researches is None or self.expired("room"):
            self._researches = self._get_researches_from_db()
            self.expire_at("research", DEFAULT_EXPIRATION_DURATION)

        return self._researches

    @property
    def upgrades(self):
        if self._upgrades is None or self.expired("room"):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at("room", DEFAULT_EXPIRATION_DURATION)

        return self._upgrades

    @property
    def characters(self):
        if self._characters is None or self.expired("char"):
            self._characters = self._get_characters_from_db()

            if self._characters:
                self.expire_at("char", DEFAULT_EXPIRATION_DURATION)
                self.update_character_with_collection_data()

        return self._characters

    @property
    def collections(self):
        if self._collections is None or self.expired("collection"):
            self._collections = self._get_collections_from_db()

            if self._collections:
                self.expire_at("collection", DEFAULT_EXPIRATION_DURATION)
                self.update_character_with_collection_data()

        return self._collections

    @property
    def items(self):
        if self._items is None or self.expired("item"):
            self._items = self._get_items_from_db()
            self.expire_at("item", DEFAULT_EXPIRATION_DURATION)

        return self._items

    @property
    def dailies(self):
        if self._dailies is None or self.expired("daily"):
            self._dailies = self._get_dailies_from_api()
            self.expire_at("daily", DEFAULT_EXPIRATION_DURATION)

        return self._dailies

    @property
    def star_system_merchant_markers(self):
        if self._star_system_merchant_markers is None or self.expired("star_system_merchant_marker"):
            self._star_system_merchant_markers = self._get_star_system_merchant_markers_from_api()
            self.expire_at("star_system_merchant_marker", DEFAULT_EXPIRATION_DURATION)

        return self._star_system_merchant_markers

    @property
    def changes(self):
        if self._changes is None or self.expired("change"):
            self._changes = self.get_changes_from_db()
            self.expire_at("change", DEFAULT_EXPIRATION_DURATION)

        return self._changes

    @property
    def last_prestiges_changes(self):
        if self._last_prestiges_changes is None or self.expired("last_prestiges_changes"):
            self._last_prestiges_changes = self.get_last_prestiges_changes_from_db()
            self.expire_at("last_prestiges_changes", DEFAULT_EXPIRATION_DURATION)

        return self._last_prestiges_changes

    @property
    def situations(self):
        if self._situations is None or self.expired("situation"):
            self._situations = self._get_situations_from_api()
            self.expire_at("situation", DEFAULT_EXPIRATION_DURATION)

        return self._situations

    @property
    def promotions(self):
        if self._promotions is None or self.expired("promotion"):
            self._promotions = self._get_promotions_from_api()
            self.expire_at("promotion", DEFAULT_EXPIRATION_DURATION)

        return self._promotions

    def expired(self, key):
        """Check if cached data has expired."""

        if key not in self._data_expiration:
            return True

        data_expiration = self._data_expiration[key]
        if not data_expiration:
            return True

        return datetime.datetime.utcnow().timestamp() - data_expiration > 0

    def expire_at(self, key, secs):
        """Set expiration duration date."""

        now = datetime.datetime.utcnow().timestamp()
        self._data_expiration[key] = now + secs

    def get_record(self, record_type: RecordTypeEnum | str, record_id: int, reload_on_error: bool = True):
        """Get PixyShip record from given PSS API type (LimitedCatalogType for example)."""

        try:
            if record_type == RecordTypeEnum.ITEM:
                return self.items[record_id]
            elif record_type == RecordTypeEnum.CHARACTER:
                return self.characters[record_id]
            elif record_type == RecordTypeEnum.ROOM:
                return self.rooms[record_id]
            elif record_type == RecordTypeEnum.SHIP:
                return self.ships[record_id]
            elif record_type == RecordTypeEnum.RESEARCH:
                return self.researches[record_id]
            elif record_type == RecordTypeEnum.CRAFT:
                return self.crafts[record_id]
            elif record_type == RecordTypeEnum.SKINSET:
                return self.skinsets[record_id]
            elif record_type == RecordTypeEnum.SKIN:
                return self.skins[record_id]
            else:
                return None
        except KeyError:
            # happens when there's new things, reload
            if reload_on_error:
                self._items = None
                self._characters = None
                self._items = None
                self._ships = None
                self._researches = None
                self._crafts = None
                self._skinsets = None
                self._skins = None
                return self.get_record(record_type, record_id, False)
            else:
                current_app.logger.error("Cannot find record of type %s with id %d", record_type, record_id)
                return None

    def update_character_with_collection_data(self):
        """Updata character data with collection."""

        if self.characters and self.collections:
            # update crew with collection data
            for character in self._characters.values():
                if character["collection"]:
                    character["collection_sprite"] = self.collections[character["collection"]]["icon_sprite"]
                    character["collection_name"] = self.collections[character["collection"]]["name"]

            # collection with characters
            for collection_id, collection in self._collections.items():
                collection["chars"] = [
                    character for character in self.characters.values() if character["collection"] == collection_id
                ]

    def get_sprite_infos(self, sprite_id):
        """Get sprite infos from given id."""

        if not sprite_id:
            return None

        if isinstance(sprite_id, str):
            sprite_id = int(sprite_id)

        if not isinstance(sprite_id, int):
            return None

        sprite = self.sprites.get(sprite_id)
        if not sprite:
            return None

        return {
            "source": sprite["image_file"],
            "x": sprite["x"],
            "y": sprite["y"],
            "width": sprite["width"],
            "height": sprite["height"],
        }

    def convert_room_sprite_to_race_sprite(self, room_id, ship_id):
        """Convert rooms to the correct interior depending on ship race."""

        room = self.get_record(RecordTypeEnum.ROOM, room_id)

        if room["type"] in ("Armor", "Lift"):
            ship = self.get_record(RecordTypeEnum.SHIP, ship_id)

            if room["sprite"]["source"] in RACE_SPECIFIC_SPRITE_MAP:
                # make a new sprite in a new room to keep from overwriting original data
                room = room.copy()
                sprite = room["sprite"].copy()

                sprite["source"] = RACE_SPECIFIC_SPRITE_MAP[room["sprite"]["source"]][ship["race_id"]]
                room["sprite"] = sprite

        return room

    def get_exterior_sprite(self, room_id, ship_id):
        """Retrieve exterior sprite if existing"""

        ship = self.get_record(RecordTypeEnum.SHIP, ship_id)
        exterior_sprite = None

        for _, skin in self.skins.items():
            if (
                skin["root_id"] == room_id
                and skin["race_id"] == ship["race_id"]
                and skin["skin_type"] == "RoomSkin"
                and skin["sprite_type"] == "Exterior"
            ):
                exterior_sprite = skin["sprite"]

        return exterior_sprite

    @staticmethod
    def find_user_id(search_name):
        """Given a name return the user_id from database. This should only be an exact match."""

        result = Player.query.filter(Player.name.ilike(search_name)).limit(1).first()
        if result:
            return result.id

        return None

    def _get_sprites_from_db(self):
        """Load sprites from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.SPRITE]

        sprites = {}
        for record in records:
            sprite = self.pixel_starships_api.parse_sprite_node(ElementTree.fromstring(record.data))

            sprites[record.type_id] = {
                "image_file": int(sprite["ImageFileId"]),
                "x": int(sprite["X"]),
                "y": int(sprite["Y"]),
                "width": int(sprite["Width"]),
                "height": int(sprite["Height"]),
                "sprite_key": sprite["SpriteKey"],
            }

        return sprites

    def update_sprites(self):
        """Update data and save records."""

        sprites = self.pixel_starships_api.get_sprites()
        still_presents_ids = []

        for sprite in sprites:
            record_id = int(sprite["SpriteId"])
            Record.update_data(
                RecordTypeEnum.SPRITE,
                record_id,
                sprite["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.SPRITE, still_presents_ids)

    def _get_skins_from_db(self):
        """Load skins from database."""

        skin_records = [record for record in self.records if record.type == RecordTypeEnum.SKIN]
        skins = {}

        # for each skin, find the skinset and add name and description
        for skin_record in skin_records:
            skin = self.pixel_starships_api.parse_skin_node(ElementTree.fromstring(skin_record.data))
            skinset_id = int(skin["SkinSetId"])

            # if skinset is not in the skinsets, skip
            if skinset_id not in self.skinsets:
                continue

            skinset = self.skinsets[skinset_id]
            skin_id = int(skin["SkinId"])
            skins[skin_id] = {
                "id": skin_id,
                "skinset_id": skinset_id,
                "name": skinset["name"],
                "description": skinset["description"],
                "sprite": self.get_sprite_infos(int(skin["SpriteId"])),
                "root_id": int(skin["RootId"]),
                "skin_type": skin["SkinType"],
                "sprite_type": skin["SpriteType"],
                "race_id": int(skin["RaceId"]),
                "race": RACES.get(int(skin["RaceId"]), RACES.get(0)),
            }

        return skins

    def _get_skinsets_from_db(self):
        """Load skinsets from database."""

        skinset_records = [record for record in self.records if record.type == RecordTypeEnum.SKINSET]

        skinsets = {}

        # retrieve all skinsets
        for skinset_record in skinset_records:
            skinset = self.pixel_starships_api.parse_skinset_node(ElementTree.fromstring(skinset_record.data))

            skinsets[skinset_record.type_id] = {
                "id": int(skinset["SkinSetId"]),
                "name": skinset["SkinSetName"],
                "description": skinset["SkinSetDescription"],
                "sprite": self.get_sprite_infos(int(skinset["SpriteId"])),
            }

        return skinsets

    def update_skins(self):
        """Update data and save records."""

        skinsets, skins = self.pixel_starships_api.get_skins()
        still_presents_ids = []

        for skinset in skinsets:
            record_id = int(skinset["SkinSetId"])
            Record.update_data(
                RecordTypeEnum.SKINSET,
                record_id,
                skinset["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.SKINSET, still_presents_ids)

        still_presents_ids = []

        for skin in skins:
            record_id = int(skin["SkinId"])
            Record.update_data(
                RecordTypeEnum.SKIN,
                record_id,
                skin["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.SKIN, still_presents_ids)

    def _get_trainings_from_db(self):
        """Load trainings from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.TRAINING]

        trainings = {}
        for record in records:
            training = self.pixel_starships_api.parse_training_node(ElementTree.fromstring(record.data))

            trainings[record.type_id] = {
                "id": int(training["TrainingDesignId"]),
                "sprite": self.get_sprite_infos(int(training["TrainingSpriteId"])),
                "hp": int(training["HpChance"]),
                "attack": int(training["AttackChance"]),
                "pilot": int(training["PilotChance"]),
                "repair": int(training["RepairChance"]),
                "weapon": int(training["WeaponChance"]),
                "science": int(training["ScienceChance"]),
                "engine": int(training["EngineChance"]),
                "stamina": int(training["StaminaChance"]),
                "ability": int(training["AbilityChance"]),
                "xp": int(training["XpChance"]),
                "fatigue": int(training["Fatigue"]),
                "minimum_guarantee": int(training["MinimumGuarantee"]),
            }

        return trainings

    def update_trainings(self):
        """Update data and save records."""

        trainings = self.pixel_starships_api.get_trainings()
        still_presents_ids = []

        for training in trainings:
            record_id = int(training["TrainingDesignId"])
            Record.update_data(
                RecordTypeEnum.TRAINING,
                record_id,
                training["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.TRAINING, still_presents_ids)

    def _get_achievements_from_db(self):
        """Load achievements from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.ACHIEVEMENT]

        achievements = {}
        all_parent_achievement_design_id = []

        for record in records:
            achievement = self.pixel_starships_api.parse_achievement_node(ElementTree.fromstring(record.data))

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
                "sprite": self.get_sprite_infos(int(achievement["SpriteId"])),
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
            Record.update_data(
                RecordTypeEnum.ACHIEVEMENT,
                record_id,
                achievement["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.ACHIEVEMENT, still_presents_ids)

    @staticmethod
    def _get_prices_from_db():
        """Get all history market summary from database."""

        sql = """
            SELECT l.item_id
                 , l.currency
                 , SUM(l.amount)                                                    AS count
                 , percentile_disc(.25) WITHIN GROUP (ORDER BY l.price / l.amount)  AS p25
                 , percentile_disc(.5) WITHIN GROUP (ORDER BY l.price / l.amount)   AS p50
                 , percentile_disc(.75) WITHIN GROUP (ORDER BY l.price /l. amount)  AS p75
            FROM listing l
            WHERE l.amount > 0
              AND l.sale_at > (now() - INTERVAL '48 HOURS')
            GROUP BY l.item_id, l.currency
        """

        result = db.session.execute(text(sql)).fetchall()
        prices = defaultdict(dict)
        for row in result:
            item_id = row[0]
            currency = row[1]
            prices[item_id][currency] = {
                "count": row[2],
                "p25": row[3],
                "p50": row[4],
                "p75": row[5],
            }

        return prices

    @staticmethod
    def get_item_prices_from_db(item_id):
        """Get item history market from database."""

        sql = """
            SELECT item_id
                 , item_name
                 , currency
                 , sale_at::DATE                                               AS sale_date
                 , SUM(amount)                                                 AS count
                 , percentile_disc(.25) WITHIN GROUP (ORDER BY price / amount) AS p25
                 , percentile_disc(.5) WITHIN GROUP (ORDER BY price / amount)  AS p50
                 , percentile_disc(.75) WITHIN GROUP (ORDER BY price / amount) AS p75
            FROM listing
            WHERE item_id = :item_id
              AND amount > 0
              AND sale_at::DATE >= now() - '6 months'::INTERVAL
            GROUP BY item_id, item_name, currency, sale_at::DATE
            ORDER BY item_id, item_name, currency, sale_at::DATE
        """

        result = db.session.execute(text(sql), {"item_id": item_id}).fetchall()
        prices = defaultdict(lambda: defaultdict(dict))

        for row in result:
            currency = row[2]
            sale_date = str(row[3])
            prices[currency][sale_date] = {
                "count": row[4],
                "p25": row[5],
                "p50": row[6],
                "p75": row[7],
            }

        data = {
            "id": item_id,
            "prices": prices,
        }

        return data

    @staticmethod
    def get_item_last_players_sales_from_db(item_id, limit):
        """Get item last players sales from database."""

        sql = """
            SELECT l.sale_at,
                   l.amount,
                   l.currency,
                   l.price,
                   l.user_name AS buyer_name,
                   l.seller_name,
                   l.id,
                   mm.message
            FROM listing l
                     LEFT JOIN market_message mm ON mm.sale_id = l.id
            WHERE l.item_id = :item_id
              AND l.amount > 0
              AND l.user_name IS NOT NULL
              AND l.seller_name IS NOT NULL
            ORDER BY l.sale_at DESC
            LIMIT :limit
        """

        result = db.session.execute(text(sql), {"item_id": item_id, "limit": limit}).fetchall()
        last_sales = []

        for row in result:
            # offstat
            offstat = None
            if row[7]:
                search_result = re.search(r"\(\+(.*?)\s(.*?)\)", row[7])
                result_value = search_result.group(1)
                if result_value:
                    result_bonus = search_result.group(2)
                    offstat = {
                        "value": result_value,
                        "bonus": result_bonus,
                        "short_bonus": SHORT_ENHANCE_MAP.get(result_bonus, result_bonus),
                    }

            last_sales.append(
                {
                    "id": int(row[6]),
                    "date": str(row[0]),
                    "quantity": row[1],
                    "currency": row[2],
                    "price": row[3],
                    "buyer": row[4],
                    "seller": row[5],
                    "offstat": offstat,
                }
            )

        return last_sales

    @staticmethod
    def get_last_sales_from_db(sale_type, sale_type_id, limit):
        """Get last sales from database."""

        sql = """
            SELECT ds.id,
                   ds.sale_at,
                   ds.sale_from,
                   ds.currency,
                   ds.price
            FROM daily_sale ds
            WHERE ds.type_id = :type_id
              AND ds.type = :type
            ORDER BY ds.sale_at DESC
            LIMIT :limit
        """

        result = db.session.execute(text(sql), {"type": sale_type, "type_id": sale_type_id, "limit": limit}).fetchall()
        last_sales = []

        for row in result:
            last_sales.append(
                {
                    "id": int(row[0]),
                    "date": str(row[1]),
                    "sale_from": SALE_FROM_MAP.get(row[2]),
                    "currency": row[3],
                    "price": row[4],
                }
            )

        return last_sales

    def get_last_sales_by_sale_from_from_db(self, sale_from, limit):
        """Get last sales for given type from database."""

        if sale_from == "blue_cargo":
            sale_from_values = ["blue_cargo_mineral", "blue_cargo_starbux"]
        else:
            sale_from_values = [sale_from]

        results: list[DailySale] = (
            DailySale.query.filter(DailySale.sale_from.in_(sale_from_values))
            .order_by(DailySale.sale_at.desc())
            .limit(limit)
            .all()
        )

        last_sales = []
        for row in results:
            record_type = get_type_enum_from_string(row.type)
            sprite = self.get_record_sprite(record_type, row.type_id)
            name = self.get_record_name(record_type, row.type_id)

            last_sale = {
                "type": row.type,
                "id": row.type_id,
                "name": name,
                "sprite": sprite,
                "currency": row.currency,
                "price": row.price,
                "date": str(row.sale_at),
            }

            # if it's a Character, get all infos of the crew
            if record_type == RecordTypeEnum.CHARACTER:
                last_sale["char"] = self.characters[row.type_id]

            # if it's an Item, get all infos of the item
            if record_type == RecordTypeEnum.ITEM:
                item = self.items[row.type_id]
                last_sale["item"] = PixyShip._create_light_item(item)

            last_sales.append(last_sale)

        return last_sales

    def update_ships(self):
        """Get ships from API and save them in database."""

        ships = self.pixel_starships_api.get_ships()
        still_presents_ids = []

        for ship in ships:
            record_id = int(ship["ShipDesignId"])
            Record.update_data(
                RecordTypeEnum.SHIP,
                record_id,
                ship["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.SHIP, still_presents_ids)

    def _get_ships_from_db(self):
        """Load ships from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.SHIP]

        ships = {}
        for record in records:
            ship = self.pixel_starships_api.parse_ship_node(ElementTree.fromstring(record.data))
            starbux_cost, mineral_cost, points_cost, items_cost = self._parse_ship_unlock_costs(
                ship["MineralCost"], ship["StarbuxCost"], ship["UnlockCost"]
            )

            ships[record.type_id] = {
                "id": record.type_id,
                "name": ship["ShipDesignName"],
                "description": ship["ShipDescription"],
                "level": int(ship["ShipLevel"]),
                "hp": int(ship["Hp"]),
                "repair_time": int(ship["RepairTime"]),
                "full_repair_time": time.strftime("%H:%M:%S", time.gmtime(int(ship["RepairTime"]) * int(ship["Hp"]))),
                "exterior_sprite": self.get_sprite_infos(int(ship["ExteriorSpriteId"])),
                "interior_sprite": self.get_sprite_infos(int(ship["InteriorSpriteId"])),
                "logo_sprite": self.get_sprite_infos(int(ship["LogoSpriteId"])),
                "mini_ship_sprite": self.get_sprite_infos(int(ship["MiniShipSpriteId"])),
                "frame_sprite": self.get_sprite_infos(int(ship["RoomFrameSpriteId"])),
                "left_door_sprite": self.get_sprite_infos(int(ship["DoorFrameLeftSpriteId"])),
                "right_door_sprite": self.get_sprite_infos(int(ship["DoorFrameRightSpriteId"])),
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
                "requirements": self._parse_requirements(ship["RequirementString"]),
            }

        return ships

    def update_researches(self):
        """Update data and save records."""

        researches = self.pixel_starships_api.get_researches()
        still_presents_ids = []

        for research in researches:
            record_id = int(research["ResearchDesignId"])
            Record.update_data(
                RecordTypeEnum.RESEARCH,
                record_id,
                research["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.RESEARCH, still_presents_ids)

    def _get_researches_from_db(self):
        """Load researches from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.RESEARCH]

        researches = {}
        for record in records:
            research = self.pixel_starships_api.parse_research_node(ElementTree.fromstring(record.data))
            researches[record.type_id] = {
                **research,
                "id": record.type_id,
                "name": research["ResearchName"],
                "description": research["ResearchDescription"],
                "gas_cost": int(research["GasCost"]),
                "starbux_cost": int(research["StarbuxCost"]),
                "lab_level": int(research["RequiredLabLevel"]),
                "research_seconds": int(research["ResearchTime"]),
                "logo_sprite": self.get_sprite_infos(research["LogoSpriteId"]),
                "sprite": self.get_sprite_infos(research["ImageSpriteId"]),
                "required_research_id": int(research["RequiredResearchDesignId"]),
                "research_type": RESEARCH_TYPE_MAP.get(research["ResearchDesignType"], research["ResearchDesignType"]),
            }

        for research in researches.values():
            research["required_research_name"] = (
                researches[research["required_research_id"]]["name"] if research["required_research_id"] else ""
            )

        return researches

    @staticmethod
    def _parse_price_from_pricestring(pricestring):
        """Split amount and currency."""

        if not pricestring:
            return 0, None

        parts = pricestring.split(":")
        return int(parts[1]), parts[0]

    def update_rooms(self):
        """Get rooms from API and save them in database."""

        rooms = self.pixel_starships_api.get_rooms()
        still_presents_ids = []

        for room in rooms:
            record_id = int(room["RoomDesignId"])
            Record.update_data(
                RecordTypeEnum.ROOM,
                record_id,
                room["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["AvailabilityMask"],
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.ROOM, still_presents_ids)

    def _get_rooms_from_db(self):
        """Load rooms from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.ROOM]

        rooms = {}
        for record in records:
            room = self.pixel_starships_api.parse_room_node(ElementTree.fromstring(record.data))
            missile_design = room["MissileDesign"]

            room_price, room_price_currency = self._parse_price_from_pricestring(room["PriceString"])
            room_type = ROOM_TYPE_MAP.get(room["RoomType"], room["RoomType"])

            # ask Savy why...
            not_powered = (
                int(room["MaxSystemPower"]) != 0
                and int(room["ReloadTime"]) == 0
                and int(room["ManufactureCapacity"]) == 0
            )

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
                "sprite": self.get_sprite_infos(int(room["ImageSpriteId"])),
                "construction_sprite": self.get_sprite_infos(int(room["ConstructionSpriteId"])),
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
                "requirement": self._parse_requirement(room["RequirementString"]),
                "extension_grids": int(room.get("SupportedGridTypes", "0")) & 2 != 0,
                "has_weapon_stats": True if missile_design else False,
                "purchasable": True if "AvailabilityMask" in room else False,
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

    def update_crafts(self):
        """Get crafts from API and save them in database."""

        crafts = self.pixel_starships_api.get_crafts()
        still_presents_ids = []

        for craft in crafts:
            record_id = int(craft["CraftDesignId"])
            Record.update_data(
                RecordTypeEnum.CRAFT,
                record_id,
                craft["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["ReloadModifier"],
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.CRAFT, still_presents_ids)

    def _get_crafts_from_db(self):
        """Load crafts from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.CRAFT]

        crafts = {}
        for record in records:
            craft = self.pixel_starships_api.parse_craft_node(ElementTree.fromstring(record.data))
            missile_design = craft["MissileDesign"]

            crafts[record.type_id] = {
                "id": record.type_id,
                "name": craft["CraftName"],
                "flight_speed": int(craft["FlightSpeed"]),
                "reload": int(craft["Reload"]),
                "reload_modifier": int(craft["ReloadModifier"]) if "ReloadModifier" in craft else None,
                "craft_volley": int(craft["Volley"]),
                "craft_volley_delay": int(craft["VolleyDelay"]),
                "attack_distance": int(craft["AttackDistance"]),
                "attack_range": int(craft["AttackRange"]),
                "hp": int(craft["Hp"]),
                "craft_attack_type": craft["CraftAttackType"],
                "craft_target_type": craft["CraftTargetType"],
                "sprite": self.get_sprite_infos(int(craft["SpriteId"])),
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
            }

        return crafts

    def update_missiles(self):
        """Get missiles from API and save them in database."""

        missiles = self.pixel_starships_api.get_missiles()
        still_presents_ids = []

        for missile in missiles:
            record_id = int(missile["ItemDesignId"])
            Record.update_data(
                RecordTypeEnum.MISSILE,
                record_id,
                missile["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["ReloadModifier"],
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.MISSILE, still_presents_ids)

    def _get_missiles_from_db(self):
        """Load missiles from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.MISSILE]

        missiles = {}
        for record in records:
            missile = self.pixel_starships_api.parse_missile_node(ElementTree.fromstring(record.data))
            missile_design = missile["MissileDesign"]

            missiles[record.type_id] = {
                "id": record.type_id,
                "name": missile["ItemDesignName"],
                "build_time": int(missile["BuildTime"]),
                "reload_modifier": int(missile["ReloadModifier"]) if "ReloadModifier" in missile else None,
                "manufacture_cost": self._parse_assets_from_string(missile["ManufactureCost"]),
                "sprite": self.get_sprite_infos(int(missile["ImageSpriteId"])),
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

    @staticmethod
    def _parse_equipment_slots(character):
        """Determine equipments slots with character equipment mask."""

        equipment_mask = int(character["EquipmentMask"])
        output = [int(x) for x in "{:06b}".format(equipment_mask)]
        slots = [EQUIPMENT_SLOTS[5 - i] for i, b in enumerate(output) if b]

        return slots

    def update_characters(self):
        """Get crews from API and save them in database."""

        characters = self.pixel_starships_api.get_characters()
        still_presents_ids = []

        for character in characters:
            record_id = int(character["CharacterDesignId"])
            Record.update_data(
                RecordTypeEnum.CHARACTER,
                record_id,
                character["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.CHARACTER, still_presents_ids)

    def _get_characters_from_db(self):
        """Load crews from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.CHARACTER]

        characters = {}
        for record in records:
            character_node = ElementTree.fromstring(record.data)
            character = self.pixel_starships_api.parse_character_node(character_node)

            characters[record.type_id] = {
                "name": character["CharacterDesignName"],
                "id": record.type_id,
                "sprite": self.get_sprite_infos(int(character["ProfileSpriteId"])),
                "head_sprite": self.get_sprite_infos(int(character["CharacterParts"]["Head"]["StandardSpriteId"])),
                "body_sprite": self.get_sprite_infos(int(character["CharacterParts"]["Body"]["StandardSpriteId"])),
                "leg_sprite": self.get_sprite_infos(int(character["CharacterParts"]["Leg"]["StandardSpriteId"])),
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
                "special_ability": ABILITY_MAP.get(character["SpecialAbilityType"], {"name": ""})["name"],
                "ability_sprite": self.get_sprite_infos(
                    ABILITY_MAP.get(character["SpecialAbilityType"], {"sprite": 110})["sprite"]
                ),
                "fire_resist": int(character["FireResistance"]),
                "resurrect": 0,
                "walk": int(character["WalkingSpeed"]),
                "run": int(character["RunSpeed"]),
                "training_limit": int(character["TrainingCapacity"]),
                "progression_type": character["ProgressionType"],
                "equipment": self._parse_equipment_slots(character),
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

    def update_prestiges(self):
        """Get prestiges from API and save them in database."""

        still_presents_ids = []

        for character in self.characters.values():
            prestiges = self.get_prestiges_from_api(character["id"])

            # no prestiges, probably special crew or API bug
            if not prestiges["to"] and not prestiges["from"]:
                continue

            json_content = json.dumps(
                {
                    "to": prestiges["to"],
                    "from": prestiges["from"],
                },
                sort_keys=True,
            )

            record_id = int(character["id"])
            Record.update_data(
                RecordTypeEnum.PRESTIGE,
                record_id,
                json_content,
                self.pixel_starships_api.server,
                data_as_xml=False,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.PRESTIGE, still_presents_ids)

    def update_collections(self):
        """Get collections from API and save them in database."""

        collections = self.pixel_starships_api.get_collections()
        still_presents_ids = []

        for collection in collections:
            record_id = int(collection["CollectionDesignId"])
            Record.update_data(
                RecordTypeEnum.COLLECTION,
                record_id,
                collection["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.COLLECTION, still_presents_ids)

    def _get_collections_from_db(self):
        """Load collections from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.COLLECTION]

        collections = {}
        for record in records:
            collection_node = ElementTree.fromstring(record.data)
            collection = self.pixel_starships_api.parse_collection_node(collection_node)

            collections[record.type_id] = {
                "id": int(collection["CollectionDesignId"]),
                "name": collection["CollectionName"],
                "min": int(collection["MinCombo"]),
                "max": int(collection["MaxCombo"]),
                "base_enhancement": int(collection["BaseEnhancementValue"]),
                "sprite": self.get_sprite_infos(int(collection["SpriteId"])),
                "step_enhancement": int(collection["StepEnhancementValue"]),
                "icon_sprite": self.get_sprite_infos(int(collection["IconSpriteId"])),
                "chars": [],
                "ability_name": COLLECTION_ABILITY_MAP[collection["EnhancementType"]],
                "trigger": COLLECTION_ABILITY_TRIGGER_MAP[collection["TriggerType"]],
                "base_chance": int(collection["BaseChance"]),
                "step_chance": int(collection["StepChance"]),
                "max_use": int(collection["MaxUse"]),
                "description": collection["CollectionDescription"],
            }

        return collections

    @staticmethod
    def _parse_item_ingredients(ingredients_string, items):
        """Parse recipe infos from API."""

        recipe = []
        if ingredients_string:
            ingredients = [i.split("x") for i in ingredients_string.split("|")]
            for ingredient in ingredients:
                # replace hack, 2021 easter event come with additional 'item:' prefix
                ingredient_item_id = ingredient[0].replace("item:", "")

                item = items.get(int(ingredient_item_id))

                if item:
                    line = PixyShip._create_light_item(item, items)
                    line["count"] = int(ingredient[1])

                    recipe.append(line)

        return recipe

    @staticmethod
    def _create_light_item(item, items=None):
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
            "recipe": item["recipe"] if not items else PixyShip._parse_item_ingredients(item["ingredients"], items),
            "training": item["training"],
        }

    def _parse_item_content(self, item_content_string, last_item, items):
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
                        content_item_data = self.characters[int(content_item_id)]
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

                    content_item_data = PixyShip._create_light_item(item)

                    # avoid infinite recursion when item reward can be the item itself
                    if last_item["id"] != item["id"]:
                        content_item_data["content"] = self._parse_item_content(item["content_string"], item, items)

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
                        content_item_data = self.skinsets[int(content_item_id)]
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

    def _parse_ship_unlock_costs(self, mineral_cost_string, starbux_cost_string, unlock_cost_string):
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
                    item = self.items.get(int(cost_value))

                    if item:
                        item_cost = PixyShip._create_light_item(item)
                        items_cost.append(item_cost)

                    continue
        else:
            # no UnlockCost, use MineralCost and StarbuxCost
            starbux_cost = int(starbux_cost_string)
            mineral_cost = int(mineral_cost_string)

        return starbux_cost, mineral_cost, points_cost, items_cost

    def update_items(self):
        """Get items from API and save them in database."""

        items = self.pixel_starships_api.get_items()
        still_presents_ids = []

        for item in items:
            record_id = int(item["ItemDesignId"])
            Record.update_data(
                RecordTypeEnum.ITEM,
                record_id,
                item["pixyship_xml_element"],
                self.pixel_starships_api.server,
                ["FairPrice", "MarketPrice", "BuildPrice"],
            )
            still_presents_ids.append(int(record_id))

        Record.purge_old_records(RecordTypeEnum.ITEM, still_presents_ids)

    def _get_items_from_db(self):
        """Get items from database."""

        records = [record for record in self.records if record.type == RecordTypeEnum.ITEM]

        items = {}
        for record in records:
            item_node = ElementTree.fromstring(record.data)
            item = self.pixel_starships_api.parse_item_node(item_node)

            number_of_rewards = 0
            if item["Content"] and float(item["ModuleArgument"]) != 0:
                number_of_rewards = item["ModuleArgument"]

            module_extra_enhancement = self._parse_module_extra_enhancement(item)

            slot = SLOT_MAP.get(item["ItemSubType"], item["ItemSubType"])
            item_type = item.get("ItemType")
            rarity_order = RARITY_MAP[item["Rarity"]]
            bonus = float(item.get("EnhancementValue"))
            disp_enhancement = ENHANCE_MAP.get(item["EnhancementType"], item["EnhancementType"])
            offstat = has_offstat(item_type, slot, rarity_order, bonus, disp_enhancement)

            items[record.type_id] = {
                "name": item["ItemDesignName"],
                "description": item["ItemDesignDescription"],
                "sprite": self.get_sprite_infos(int(item["ImageSpriteId"])),
                "logo_sprite": self.get_sprite_infos(int(item["LogoSpriteId"])),
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
                "prices": self.prices.get(int(item["ItemDesignId"])),
                "training": self.trainings.get(int(item["TrainingDesignId"])),
                "id": record.type_id,
                "saleable": (int(item["Flags"]) & 1) != 0,
                "item_space": int(item["ItemSpace"]),
                "requirement": item["RequirementString"],
            }

        # Second pass required for self references
        for item in items.values():
            item["recipe"] = self._parse_item_ingredients(item["ingredients"], items)

        # Third pass required for self references
        for item in items.values():
            item["content"] = self._parse_item_content(item["content_string"], item, items)

        return items

    def get_top100_alliances_from_api(self):
        """Get the top 100 alliances."""

        alliances = self.pixel_starships_api.get_alliances()

        return {
            int(alliance["AllianceId"]): {
                "name": alliance["AllianceName"],
            }
            for alliance in alliances
        }

    def get_sales_from_api(self, item_id):
        """Get market history of item."""

        # get max sale_id to retrieve only new sales
        max_sale_id_result = (
            Listing.query.filter(Listing.item_id == item_id).order_by(desc(Listing.id)).limit(1).first()
        )

        if max_sale_id_result is not None:
            max_sale_id = max_sale_id_result.id if max_sale_id_result.id is not None else 0
        else:
            max_sale_id = 0

        sales = self.pixel_starships_api.get_sales(item_id, max_sale_id)
        return sales

    def get_market_messages_from_api(self, item_id):
        """Get market messages of item."""

        sales = self.pixel_starships_api.get_market_messages(item_id)
        return sales

    def get_alliance_users_from_api(self, alliance_id):
        """Get the top 100 alliances."""

        users = self.pixel_starships_api.get_alliance_users(alliance_id)
        return self._parse_users(users)

    def get_top100_users_from_api(self):
        """Get the top 100 players."""

        users = self.pixel_starships_api.get_users(1, 100)
        return self._parse_users(users)

    @staticmethod
    def _parse_users(users):
        """Create users dict from XML PSS API response."""

        # force users to be a list
        if not isinstance(users, list):
            users = [users]

        return {
            int(user["Id"]): {
                "name": user["Name"],
                "trophies": int(user["Trophy"]),
                "alliance_id": int(user["AllianceId"]),
                "last_login_at": user["LastLoginDate"],
                "alliance_name": user.get("AllianceName"),
                "alliance_sprite_id": int(user["AllianceSpriteId"]),
            }
            for user in users
            if user["UserType"] != "UserTypeDisabled"
        }

    def _get_prestige_to_from_api(self, character_id):
        """Get prestige paires and groups which create given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_to(character_id)

        # if only one unique prestige, add it in list
        if not isinstance(prestiges, list):
            prestiges = list((prestiges,))

        prestiges_to = list(
            set(
                tuple(
                    sorted(
                        [
                            int(prestige["CharacterDesignId1"]),
                            int(prestige["CharacterDesignId2"]),
                        ]
                    )
                )
                for prestige in prestiges
            )
        )

        # determine which crews to group
        temp_to = prestiges_to
        grouped_to = defaultdict(list)
        while len(temp_to):
            counter = Counter([x for y in temp_to for x in y])
            [(most_id, _)] = counter.most_common(1)

            # find all the pairs with the id
            new_to = []
            for pair in temp_to:
                if most_id == pair[0]:
                    grouped_to[most_id].append(pair[1])
                elif most_id == pair[1]:
                    grouped_to[most_id].append(pair[0])
                else:
                    new_to.append(pair)

            temp_to = new_to

        return prestiges_to, grouped_to

    def _get_prestige_from_from_api(self, character_id):
        """Get prestige paires and groups created with given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_from(character_id)
        prestiges_from = [
            [int(prestige["CharacterDesignId2"]), int(prestige["ToCharacterDesignId"])] for prestige in prestiges
        ]

        grouped_from = defaultdict(list)
        for response in prestiges_from:
            grouped_from[response[1]].append(response[0])

        return prestiges_from, grouped_from

    def get_prestiges_from_api(self, char_id):
        """Get all prestige combinaisons."""

        prestiges_to, grouped_to = self._get_prestige_to_from_api(char_id)
        prestiges_from, grouped_from = self._get_prestige_from_from_api(char_id)

        all_ids = list(
            set(
                [i for prestige in prestiges_to for i in prestige]
                + [i for prestige in prestiges_from for i in prestige]
                + [char_id]
            )
        )
        all_characters = [self.characters[i] for i in all_ids]

        return {
            "to": grouped_to,
            "from": grouped_from,
            "chars": all_characters,
            "expires_at": datetime.datetime.now() + datetime.timedelta(minutes=1),
        }

    def get_changes_from_db(self):
        """Get changes from database."""

        min_changes_dates_sql = f"""
            SELECT type, MIN(created_at) + INTERVAL '1 day' AS min
            FROM record
            WHERE type IN (
                '{RecordTypeEnum.ITEM}',
                '{RecordTypeEnum.SHIP}',
                '{RecordTypeEnum.CHARACTER}',
                '{RecordTypeEnum.ROOM}',
                '{RecordTypeEnum.SPRITE}',
                '{RecordTypeEnum.CRAFT}',
                '{RecordTypeEnum.SKINSET}'
            )
            GROUP BY type
        """

        min_changes_dates_result = db.session.execute(text(min_changes_dates_sql)).fetchall()

        min_changes_dates_conditions = [
            f"(c.type = '{record[0]}' AND o.data IS NULL AND (o.id IS NOT NULL OR c.created_at > '{record[1]}'))"
            if record[0] == "sprite"
            else f"(c.type = '{record[0]}' AND (o.id IS NOT NULL OR c.created_at > '{record[1]}'))"
            for record in min_changes_dates_result
        ]

        sql = """
            SELECT *
            FROM (SELECT DISTINCT ON (c.id) c.id, c.type, c.type_id, c.data, c.created_at, o.data as old_data
                  FROM record c
                  LEFT JOIN record o ON o.type = c.type AND o.type_id = c.type_id AND o.current = FALSE
                  WHERE c.current = TRUE
                    AND ({})
                  ORDER BY c.id, o.created_at DESC) AS sub
            ORDER BY created_at DESC
            LIMIT {}
        """.format(" OR ".join(min_changes_dates_conditions), current_app.config.get("CHANGES_MAX_ASSETS", 5000))

        result = db.session.execute(text(sql)).fetchall()

        changes = [self.create_change_record(record) for record in result]

        return changes

    def create_change_record(self, record):
        record_type_enum = get_type_enum_from_string(record[1])
        sprite = self.get_record_sprite(record_type_enum, int(record[2]))
        name = self.get_record_name(record_type_enum, record[2])

        change = {
            "type": record[1].lower(),
            "id": record[2],
            "name": name,
            "changed_at": record[4],
            "data": record[3],
            "old_data": record[5],
            "change_type": "Changed" if record[5] else "New",
            "sprite": sprite,
        }

        if record[1] == RecordTypeEnum.CHARACTER.value:
            change["char"] = self.characters[record[2]]
        elif record[1] == RecordTypeEnum.ITEM.value:
            change["item"] = self._create_light_item(self.items[record[2]])

        return change

    @staticmethod
    def get_last_prestiges_changes_from_db():
        """Get last prestiges changes date."""

        result = (
            db.session.query(func.max(Record.created_at)).filter_by(type=RecordTypeEnum.PRESTIGE, current=True).first()
        )

        if result:
            return result[0]

        return None

    @staticmethod
    def _format_daily_object(count, type_str, object_str, type_id):
        if type_str == "None":
            return None

        return {
            "count": count,
            "type": type_str.lower(),
            "id": type_id,
            "object": object_str,
        }

    @staticmethod
    def _format_daily_price(amount, currency):
        return {
            "price": amount,
            "currency": currency,
        }

    def _parse_requirements(self, requirements_string):
        """Parse several requirements assets."""

        if not requirements_string:
            return None

        requirements_string = html.unescape(requirements_string)
        unparsed_requirements = requirements_string.split("&&")

        return [self._parse_requirement(unparsed_requirement.strip()) for unparsed_requirement in unparsed_requirements]

    def _parse_requirement(self, requirement_string):
        """Parse requirement asset."""

        if not requirement_string:
            return None

        # TODO: quick fix, but I need more investigation when I will have more time
        splits = requirement_string.split(":")
        if len(splits) < 2:
            return None

        requirement_type, id_and_amount = splits

        if ">=" in id_and_amount:
            requirement_id, requirement_count = id_and_amount.split(">=")
        else:
            requirement_id, requirement_count = id_and_amount.split(">")

        requirement_type = requirement_type.strip().capitalize()
        requirement_id = int(requirement_id.strip())
        requirement_count = int(requirement_count.strip())

        # in some case (example: Coal Factory), the amount needed is '> 0' not '>= 1'
        if requirement_count == 0:
            requirement_count = 1

        record_type = get_type_enum_from_string(requirement_type)
        requirement_object = {
            "count": requirement_count,
            "type": requirement_type,
            "object": self.get_record(record_type, requirement_id),
        }

        return requirement_object

    def _parse_daily_cargo(self, item_list_string, cost_list_string):
        """Split daily cargo data into prices and items."""

        items = self._parse_daily_items(item_list_string)

        splitted_prices = [i.split(":") for i in cost_list_string.split("|")]
        prices = []
        for splitted_price in splitted_prices:
            if len(splitted_price) < 2:
                current_app.logger.error("Cannot parse cost_list_string %s", splitted_price)
                continue

            price = {"currency": splitted_price[0]}

            amount = splitted_price[1].split("x")
            if len(amount) > 1:
                item_id = int(amount[0])
                price["price"] = item_id
                price["count"] = amount[1]
                price["object"] = self.items[item_id]
            else:
                price["price"] = int(splitted_price[1])

            prices.append(price)

        cargo = [
            {
                "sprite": {},
                "object": item,
                "cost": price,
                "details": None,
                "expires": None,
            }
            for item, price in zip(items, prices, strict=True)
        ]

        return cargo

    def _parse_daily_items(self, item_list_string):
        items_split = [i.split("x") for i in item_list_string.split("|")]
        items = [
            {
                "count": int(item[1]),
                "type": "item",
                "id": int(item[0]),
                "object": self.items[int(item[0])],
            }
            for item in items_split
        ]

        return items

    def _get_dailies_from_api(self):
        """Get settings service data, sales, motd from API."""

        dailies = self.pixel_starships_api.get_dailies()
        promotions = self.get_current_promotions()

        daily_promotions = []
        for promotion in promotions:
            if promotion["type"] == "DailyDealOffer":
                daily_promotions.append(promotion)

        daily_object = None
        if dailies["SaleType"] == "FleetGift":
            rewards = self._parse_assets_from_string(dailies["SaleRewardString"])
            if rewards:
                # for now, we assume we only have 1 reward
                reward = rewards[0]

                daily_object = self._format_daily_object(reward["count"], reward["type"], reward["data"], reward["id"])
        else:
            record_type = get_type_enum_from_string(dailies["SaleType"])
            daily_object = self._format_daily_object(
                1,
                dailies["SaleType"],
                self.get_record(record_type, int(dailies["SaleArgument"])),
                int(dailies["SaleArgument"]),
            )

        record_type = get_type_enum_from_string(dailies["LimitedCatalogType"])
        offers = {
            "shop": {
                "sprite": self.get_sprite_infos(SHOP_SPRITE_ID),
                "object": self._format_daily_object(
                    1,
                    dailies["LimitedCatalogType"],
                    self.get_record(
                        record_type,
                        int(dailies["LimitedCatalogArgument"]),
                    ),
                    int(dailies["LimitedCatalogArgument"]),
                ),
                "cost": self._format_daily_price(
                    dailies["LimitedCatalogCurrencyAmount"],
                    dailies["LimitedCatalogCurrencyType"],
                ),
                "details": {
                    "left": dailies["LimitedCatalogQuantity"],
                    "max": dailies["LimitedCatalogMaxTotal"],
                },
                "expires": dailies["LimitedCatalogExpiryDate"],
            },
            "blueCargo": {
                "sprite": self.get_sprite_infos(BLUE_CARGO_SPRITE_ID),
                "mineralCrew": self._format_daily_object(
                    1,
                    "Character",
                    self.get_record(RecordTypeEnum.CHARACTER, int(dailies["CommonCrewId"])),
                    int(dailies["CommonCrewId"]),
                ),
                "starbuxCrew": self._format_daily_object(
                    1,
                    "Character",
                    self.get_record(RecordTypeEnum.CHARACTER, int(dailies["HeroCrewId"])),
                    int(dailies["HeroCrewId"]),
                ),
            },
            "greenCargo": {
                "sprite": self.get_sprite_infos(GREEN_CARGO_SPRITE_ID),
                "items": self._parse_daily_cargo(dailies["CargoItems"], dailies["CargoPrices"]),
            },
            "dailyRewards": {
                "sprite": self.get_sprite_infos(DAILY_REWARDS_SPRITE_ID),
                "objects": [
                    self._format_daily_object(
                        int(dailies["DailyRewardArgument"]),
                        "currency",
                        self._format_daily_price(
                            int(dailies["DailyRewardArgument"]),
                            dailies["DailyRewardType"],
                        ),
                        None,
                    )
                ]
                + self._parse_daily_items(dailies["DailyItemRewards"]),
            },
            "sale": {
                "sprite": self.get_sprite_infos(DAILY_SALE_SPRITE_ID),
                "object": daily_object,
                "bonus": int(dailies["SaleArgument"]) if dailies["SaleType"] == "Bonus" else None,
                "options": None
                if dailies["SaleType"] == "None"
                else self._format_daily_sale_options(int(dailies["SaleItemMask"])),
            },
            "promotions": {
                "sprite": self.get_sprite_infos(DAILY_SALE_SPRITE_ID),
                "objects": daily_promotions,
            },
        }

        dailies = {
            "stardate": self.pixel_starships_api.get_stardate(),
            "news": {
                "news": dailies["News"],
                "news_date": dailies["NewsUpdateDate"],
                # not any more available with the new API endpoint
                "maintenance": self.pixel_starships_api.maintenance_message,
                "sprite": self.get_sprite_infos(dailies["NewsSpriteId"]),
            },
            "tournament_news": dailies["TournamentNews"],
            "current_situation": self._get_current_situation(),
            "offers": offers,
            "merchant_markers": self.star_system_merchant_markers,
        }

        return dailies

    def _get_situations_from_api(self):
        """Get situations from API."""

        data = self.pixel_starships_api.get_situations()
        situations = []

        for datum in data:
            situation = {
                "id": int(datum["SituationDesignId"]),
                "name": datum["SituationName"],
                "description": datum["SituationDescription"],
                "sprite": self.get_sprite_infos(datum["IconSpriteId"]),
                "from": datum["FromDate"],
                "end": datum["EndDate"],
            }

            situations.append(situation)

        return situations

    def _get_current_situation(self):
        """Get running situation depending on the current date."""

        utc_now = datetime.datetime.utcnow()

        for situation in self.situations:
            from_date = datetime.datetime.strptime(situation["from"], "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.datetime.strptime(situation["end"], "%Y-%m-%dT%H:%M:%S")
            if from_date <= utc_now <= end_date:
                situation_left_delta = end_date - utc_now
                situation["left"] = format_delta_time(situation_left_delta)

                return situation

        return None

    def _get_star_system_merchant_markers_from_api(self):
        """Get Star System Merchant Markers from API."""

        data = self.pixel_starships_api.get_star_system_markers()
        markers = []

        for datum in data:
            if datum["MarkerType"] != "MerchantShip":
                continue

            costs = self._parse_assets_from_string(datum["CostString"])
            rewards = self._parse_assets_from_string(datum["RewardString"])

            availables_items = []
            for i in range(0, len(rewards)):
                availables_item = {"cost": costs[i], "reward": rewards[i]}

                availables_items.append(availables_item)

            expiry_date = datum["ExpiryDate"]

            # hack, Savy don't put midnight but 5s before...
            if expiry_date.endswith("T23:59:55"):
                next_utc = datetime.datetime.utcnow().date() + datetime.timedelta(days=1)
                expiry_date = next_utc.strftime("%Y-%m-%dT%H:%M:%S")

            marker = {
                "title": datum["Title"],
                "sprite": self.get_sprite_infos(datum["SpriteId"]),
                "items": availables_items,
                "expires": expiry_date,
            }

            markers.append(marker)

        return markers

    def _get_promotions_from_api(self):
        """Get promotions from API."""

        data = self.pixel_starships_api.get_promotions()
        promotions = []

        for datum in data:
            promotion = {
                "id": int(datum["PromotionDesignId"]),
                "type": datum["PromotionType"],
                "title": datum["Title"],
                "subtitle": datum["SubTitle"],
                "description": datum["Description"],
                "rewards": self._parse_assets_from_string(datum["RewardString"]),
                "sprite": self.get_sprite_infos(datum["IconSpriteId"]),
                "from": datum["FromDate"],
                "end": datum["ToDate"],
                "pack": int(datum["PackId"].replace("sale", "")) if datum["PackId"] else None,
            }

            promotions.append(promotion)

        return promotions

    def _parse_assets_from_string(self, assets_string):
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
                        data = self.characters[asset_item_type_id]
                    except KeyError:
                        continue

                # if change's an Item, get all infos of the item
                elif asset_item_type == "item":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        item = self.items[asset_item_type_id]
                        data = PixyShip._create_light_item(item)
                    except KeyError:
                        continue

                # if change's an Item, get all infos of the item
                elif asset_item_type == "room":
                    try:
                        asset_item_type_id = int(asset_item_data)
                        data = self.rooms[asset_item_type_id]
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
                        data = self.skinsets[asset_item_type_id]
                    except KeyError:
                        continue

                # Unknown type
                else:
                    continue

                asset_item_count = 1
                if len(asset_item_id_count_unpacked) > 1:
                    # TODO: handle count based in IAP value, for now ignore it
                    if "[USD/" in assets_string:
                        asset_item_count = None
                    else:
                        asset_item_count = int(asset_item_id_count_unpacked[1])

                line.update(
                    {
                        "count": asset_item_count,
                        "data": data,
                        "id": asset_item_type_id,
                        "type": asset_item_type,
                    }
                )

                assets.append(line)

        return assets

    def get_current_promotions(self):
        """Get running promotions depending on the current date."""

        utc_now = datetime.datetime.utcnow()

        promotions = []

        for promotion in self.promotions:
            # skip infinite promos
            if promotion["from"] == "2000-01-01T00:00:00":
                continue

            from_date = datetime.datetime.strptime(promotion["from"], "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.datetime.strptime(promotion["end"], "%Y-%m-%dT%H:%M:%S")
            if from_date <= utc_now <= end_date:
                promotion_left_delta = end_date - utc_now
                promotion["left"] = format_delta_time(promotion_left_delta)

                promotions.append(promotion)

        return promotions

    def get_record_sprite(self, record_type: RecordTypeEnum, type_id: int, reload_on_error: bool = True):
        """Get sprite date for the given record ID."""

        try:
            if record_type == RecordTypeEnum.ITEM:
                return self.items[type_id]["sprite"]
            elif record_type == RecordTypeEnum.CHARACTER or record_type == RecordTypeEnum.PRESTIGE:
                return self.characters[type_id]["sprite"]
            elif record_type == RecordTypeEnum.ROOM:
                return self.rooms[type_id]["sprite"]
            elif record_type == RecordTypeEnum.SHIP:
                return self.ships[type_id]["mini_ship_sprite"]
            elif record_type == RecordTypeEnum.SPRITE:
                return self.get_sprite_infos(type_id)
            elif record_type == RecordTypeEnum.CRAFT:
                return self.crafts[type_id]["sprite"]
            elif record_type == RecordTypeEnum.SKINSET:
                return self.skinsets[type_id]["sprite"]
            elif record_type == RecordTypeEnum.SKIN:
                return self.skins[type_id]["sprite"]
            else:
                return None
        except KeyError:
            # happens when there's new things, reload
            if reload_on_error:
                self._items = None
                self._characters = None
                self._rooms = None
                self._ships = None
                self._crafts = None
                self._skinsets = None
                self._skins = None
                return self.get_record_sprite(record_type, type_id, False)
            else:
                current_app.logger.error("Cannot find object of type %s with id %d", record_type, type_id)
                return None

    def get_record_name(self, record_type: RecordTypeEnum, type_id: int, reload_on_error: bool = True):
        """Get sprite date for the given record ID."""

        try:
            if record_type == RecordTypeEnum.ITEM:
                return self.items[type_id]["name"]
            elif record_type == RecordTypeEnum.CHARACTER or record_type == RecordTypeEnum.PRESTIGE:
                return self.characters[type_id]["name"]
            elif record_type == RecordTypeEnum.ROOM:
                return self.rooms[type_id]["name"]
            elif record_type == RecordTypeEnum.SHIP:
                return self.ships[type_id]["name"]
            elif record_type == RecordTypeEnum.SPRITE:
                return self.get_sprite_infos(type_id)["source"]
            elif record_type == RecordTypeEnum.CRAFT:
                return self.crafts[type_id]["name"]
            elif record_type == RecordTypeEnum.SKIN:
                return self.skins[type_id]["name"]
            elif record_type == RecordTypeEnum.SKINSET:
                return self.skinsets[type_id]["name"]
            else:
                return None
        except KeyError:
            # happens when there's new things, reload
            if reload_on_error:
                self._items = None
                self._characters = None
                self._rooms = None
                self._ships = None
                self._crafts = None
                self._skins = None
                self._skinsets = None
                return self.get_record_name(record_type, type_id, False)
            else:
                current_app.logger.error("Cannot find object of type %s with id %d", record_type, type_id)
                return None

    def get_player_data(self, search: str = None):
        """Retrieve all players data or players found by given search."""

        query = db.session.query(
            Player.name,
            Player.trophies,
            Alliance.name.label("alliance_name"),
            Alliance.sprite_id,
        ).outerjoin(Alliance, Alliance.id == Player.alliance_id)

        if search:
            query = query.filter(Player.name.ilike("%" + search + "%"))

        query = query.order_by(Player.trophies.desc()).limit(100)

        results = query.all()
        return [
            {
                "name": player.name,
                "lower": player.name.lower(),
                "trophies": player.trophies,
                "alliance": player.alliance_name,
                "alliance_sprite": self.get_sprite_infos(player.sprite_id),
            }
            for player in results
        ]

    def get_ship_data(self, player_name):
        """Get user and ship data from API."""

        ship, user, rooms, stickers = self.summarize_ship(player_name)

        if user:
            data = {
                "rooms": rooms,
                "user": user,
                "ship": ship,
                "stickers": stickers,
                "status": "found",
            }
        else:
            data = {"status": "not found"}

        response = {"data": data, "status": "success"}

        return response

    def summarize_ship(self, player_name):
        """Get ship, user, rooms and upgrade from given player name."""

        user_id = self.find_user_id(player_name)
        if not user_id:
            current_app.logger.error("Cannot find user %s", player_name)
            return None, None, None, None

        ship_data, user_data = self.pixel_starships_api.ship_details(user_id)
        if not ship_data or not user_data:
            current_app.logger.error("Cannot find ship data for user %s", player_name)
            return None, None, None, None

        room_data = self.pixel_starships_api.ship_room_details(user_id)
        if not room_data:
            current_app.logger.error("Cannot find room data for user %s", player_name)
            return None, None, None, None

        user = dict(
            id=user_data["Id"],
            name=user_data["Name"],
            sprite=self.get_sprite_infos(int(user_data["IconSpriteId"])),
            alliance_name=user_data.get("AllianceName"),
            alliance_membership=user_data.get("AllianceMembership"),
            alliance_sprite=self.get_sprite_infos(int(user_data.get("AllianceSpriteId"))),
            trophies=int(user_data["Trophy"]),
            last_date=user_data["LastAlertDate"],
            race=RACES.get(int(ship_data["OriginalRaceId"]), RACES.get(0)),
        )

        searched_users = self.pixel_starships_api.search_users(user_data["Name"], True)
        if searched_users:
            more_user_data = searched_users[0]

            user["alliance_join_date"] = more_user_data.get("AllianceJoinDate")
            user["pvpattack_wins"] = int(more_user_data["PVPAttackWins"])
            user["pvpattack_losses"] = int(more_user_data["PVPAttackLosses"])
            user["pvpattack_draws"] = int(more_user_data["PVPAttackDraws"])
            user["pvpattack_ratio"] = compute_pvp_ratio(
                int(more_user_data["PVPAttackWins"]),
                int(more_user_data["PVPAttackLosses"]),
                int(more_user_data["PVPAttackDraws"]),
            )
            user["pvpdefence_draws"] = int(more_user_data["PVPDefenceDraws"])
            user["pvpdefence_wins"] = int(more_user_data["PVPDefenceWins"])
            user["pvpdefence_losses"] = int(more_user_data["PVPDefenceLosses"])
            user["pvpdefence_ratio"] = compute_pvp_ratio(
                int(more_user_data["PVPDefenceWins"]),
                int(more_user_data["PVPDefenceLosses"]),
                int(more_user_data["PVPDefenceDraws"]),
            )
            user["highest_trophy"] = int(more_user_data["HighestTrophy"])
            user["crew_donated"] = int(more_user_data["CrewDonated"])
            user["crew_received"] = int(more_user_data["CrewReceived"])
            user["creation_date"] = more_user_data["CreationDate"]
            user["last_login_date"] = more_user_data["LastLoginDate"]
        else:
            user["alliance_join_date"] = None
            user["pvpattack_wins"] = None
            user["pvpattack_losses"] = None
            user["pvpattack_draws"] = None
            user["pvpattack_ratio"] = None
            user["pvpdefence_draws"] = None
            user["pvpdefence_wins"] = None
            user["pvpdefence_losses"] = None
            user["pvpdefence_ratio"] = None
            user["highest_trophy"] = None
            user["crew_donated"] = None
            user["crew_received"] = None
            user["creation_date"] = None
            user["last_login_date"] = None

        ship_id = int(ship_data["ShipDesignId"])

        rooms = []
        for current_room_data in room_data:
            room = dict(
                self.convert_room_sprite_to_race_sprite(int(current_room_data["RoomDesignId"]), ship_id),
                design_id=int(current_room_data["RoomDesignId"]),
                row=int(current_room_data["Row"]),
                column=int(current_room_data["Column"]),
                construction=bool(current_room_data["ConstructionStartDate"]),
            )

            room["exterior_sprite"] = self.get_exterior_sprite(int(current_room_data["RoomDesignId"]), ship_id)

            rooms.append(room)

        ship = dict(
            self.ships[ship_id],
            hue=ship_data["HueValue"],
            saturation=ship_data["SaturationValue"],
            brightness=ship_data["BrightnessValue"],
        )

        stickers = self._parse_ship_stickers(ship_data)

        return ship, user, rooms, stickers

    @staticmethod
    def get_tournament_infos():
        utc_now = datetime.datetime.utcnow()
        first_day_next_month = (utc_now.date().replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        tournament_start = first_day_next_month - datetime.timedelta(days=7)
        tournament_start_time = datetime.datetime(tournament_start.year, tournament_start.month, tournament_start.day)
        tournament_left_delta = tournament_start_time - utc_now
        tournament_left_formatted = format_delta_time(tournament_left_delta)

        infos = {
            "start": tournament_start,
            "end": first_day_next_month,
            "left": tournament_left_formatted.strip(),
            "started": tournament_left_delta.total_seconds() < 0,
        }

        return infos

    def _parse_ship_stickers(self, ship_data):
        stickers_string = ship_data["StickerString"]

        if not stickers_string:
            return None

        stickers = []

        for sticker_string in stickers_string.split("|"):
            item_id = int(sticker_string.split("@")[0])
            item = self.items[item_id]
            coords = sticker_string.split("@")[1].split("-")

            sticker = {
                "sprite": item["logo_sprite"],
                "x": coords[0],
                "y": coords[1],
                "size": coords[2],
            }

            stickers.append(sticker)

        return stickers

    def _format_daily_sale_options(self, sale_item_mask):
        """ "From flag determine Sale options."""

        result = []
        options = self.pixel_starships_api.parse_sale_item_mask(sale_item_mask)

        for option in options:
            name = IAP_NAMES[option]
            result.append({"name": name, "value": option})

        return result

    def get_researches_and_ship_min_level(self):
        """Retrieve research and min ship level of the needed lab."""

        researches = self.researches

        # get lab room and its min ship level
        for research in researches.values():
            # TODO: don't use the name but the lab level
            lab_name = "Laboratory Lv{}".format(research["lab_level"])
            if lab_name in self.rooms_by_name:
                room = self.rooms_by_name[lab_name]
                research["min_ship_level"] = room["min_ship_level"]

        return researches

    @staticmethod
    def _parse_module_extra_enhancement(item):
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
                    upgrades.append(PixyShip._create_light_item(item))

        return upgrades
