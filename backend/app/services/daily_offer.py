import datetime

from flask import current_app
from sqlalchemy import and_, desc

from app.constants import (
    BLUE_CARGO_SPRITE_ID,
    DAILY_REWARDS_SPRITE_ID,
    DAILY_SALE_SPRITE_ID,
    GREEN_CARGO_SPRITE_ID,
    IAP_NAMES,
    SALE_FROM_MAP,
    SHOP_SPRITE_ID,
)
from app.enums import TypeEnum
from app.ext import db
from app.models import DailySale, Record
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.services.item import ItemService
from app.utils.math import format_delta_time
from app.utils.pss import get_type_enum_from_string


class DailyOfferService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._daily_offers = {}
        self._promotions: list[dict] = []
        self._situations: list[dict] = []
        self._star_system_merchant_markers: list[dict] = []

    @property
    def daily_offers(self):
        if not self._daily_offers:
            self._daily_offers = self.get_daily_offers_from_api()

        return self._daily_offers

    @property
    def promotions(self) -> list[dict]:
        if not self._promotions:
            self._promotions = self.get_promotions_from_api()

        return self._promotions

    @property
    def situations(self) -> list[dict]:
        if not self._situations:
            self._situations = self.get_situations_from_api()

        return self._situations

    @property
    def star_system_merchant_markers(self) -> list[dict]:
        if not self._star_system_merchant_markers:
            self._star_system_merchant_markers = self.get_star_system_merchant_markers_from_api()

        return self._star_system_merchant_markers

    def get_daily_offers_from_api(self):
        """Get settings service data, sales, motd from API."""

        dailies = self.pixel_starships_api.get_dailies()
        promotions = self.get_current_promotions()

        daily_promotions = []
        for promotion in promotions:
            if promotion["type"] == "DailyDealOffer":
                daily_promotions.append(promotion)

        daily_object = None
        if dailies["SaleType"] == "FleetGift":
            rewards = self.pixyship_service.parse_assets_from_string(dailies["SaleRewardString"])
            if rewards:
                # for now, we assume we only have 1 reward
                reward = rewards[0]

                daily_object = self.format_daily_object(reward["count"], reward["type"], reward["data"], reward["id"])
        else:
            record_type = get_type_enum_from_string(dailies["SaleType"])
            daily_object = self.format_daily_object(
                1,
                dailies["SaleType"],
                self.record_details_service.get_record_details(record_type, int(dailies["SaleArgument"])),
                int(dailies["SaleArgument"]),
            )

        record_type = get_type_enum_from_string(dailies["LimitedCatalogType"])
        offers = {
            "shop": {
                "sprite": self.sprite_service.get_sprite_infos(SHOP_SPRITE_ID),
                "object": self.format_daily_object(
                    1,
                    dailies["LimitedCatalogType"],
                    self.record_details_service.get_record_details(
                        record_type,
                        int(dailies["LimitedCatalogArgument"]),
                    ),
                    int(dailies["LimitedCatalogArgument"]),
                ),
                "cost": self.format_daily_price(
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
                "sprite": self.sprite_service.get_sprite_infos(BLUE_CARGO_SPRITE_ID),
                "mineralCrew": self.format_daily_object(
                    1,
                    "Character",
                    self.character_service.characters.get(int(dailies["CommonCrewId"])),
                    int(dailies["CommonCrewId"]),
                ),
                "starbuxCrew": self.format_daily_object(
                    1,
                    "Character",
                    self.character_service.characters.get(int(dailies["HeroCrewId"])),
                    int(dailies["HeroCrewId"]),
                ),
            },
            "greenCargo": {
                "sprite": self.sprite_service.get_sprite_infos(GREEN_CARGO_SPRITE_ID),
                "items": self.parse_daily_cargo(dailies["CargoItems"], dailies["CargoPrices"]),
            },
            "dailyRewards": {
                "sprite": self.sprite_service.get_sprite_infos(DAILY_REWARDS_SPRITE_ID),
                "objects": [
                    self.format_daily_object(
                        int(dailies["DailyRewardArgument"]),
                        "currency",
                        self.format_daily_price(
                            int(dailies["DailyRewardArgument"]),
                            dailies["DailyRewardType"],
                        ),
                        None,
                    )
                ]
                + self.parse_daily_items(dailies["DailyItemRewards"]),
            },
            "sale": {
                "sprite": self.sprite_service.get_sprite_infos(DAILY_SALE_SPRITE_ID),
                "object": daily_object,
                "bonus": int(dailies["SaleArgument"]) if dailies["SaleType"] == "Bonus" else None,
                "options": None
                if dailies["SaleType"] == "None"
                else self.format_daily_sale_options(int(dailies["SaleItemMask"])),
            },
            "promotions": {
                "sprite": self.sprite_service.get_sprite_infos(DAILY_SALE_SPRITE_ID),
                "objects": daily_promotions,
            },
        }

        dailies = {
            "stardate": PixelStarshipsApi.get_stardate(),
            "news": {
                "news": dailies["News"],
                "news_date": dailies["NewsUpdateDate"],
                # not any more available with the new API endpoint
                "maintenance": self.pixel_starships_api.maintenance_message,
                "sprite": self.sprite_service.get_sprite_infos(dailies["NewsSpriteId"]),
            },
            "tournament_news": dailies["TournamentNews"],
            "current_situation": self.get_current_situation(),
            "offers": offers,
            "merchant_markers": self.star_system_merchant_markers,
        }

        return dailies

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

    def get_promotions_from_api(self):
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
                "rewards": self.pixyship_service.parse_assets_from_string(datum["RewardString"]),
                "sprite": self.sprite_service.get_sprite_infos(datum["IconSpriteId"]),
                "from": datum["FromDate"],
                "end": datum["ToDate"],
                "pack": int(datum["PackId"].replace("sale", "")) if datum["PackId"] else None,
            }

            promotions.append(promotion)

        return promotions

    @staticmethod
    def format_daily_object(count, type_str, object_str, type_id):
        if type_str == "None":
            return None

        return {
            "count": count,
            "type": type_str.lower(),
            "id": type_id,
            "object": object_str,
        }

    @staticmethod
    def format_daily_price(amount, currency):
        return {
            "price": amount,
            "currency": currency,
        }

    def parse_daily_cargo(self, item_list_string, cost_list_string):
        """Split daily cargo data into prices and items."""

        items = self.parse_daily_items(item_list_string)

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
                price["object"] = self.item_service.items[item_id]
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

    def parse_daily_items(self, item_list_string):
        items_split = [i.split("x") for i in item_list_string.split("|")]
        items = [
            {
                "count": int(item[1]),
                "type": "item",
                "id": int(item[0]),
                "object": self.item_service.items[int(item[0])],
            }
            for item in items_split
        ]

        return items

    def get_situations_from_api(self):
        """Get situations from API."""

        data = self.pixel_starships_api.get_situations()
        situations = []

        for datum in data:
            situation = {
                "id": int(datum["SituationDesignId"]),
                "name": datum["SituationName"],
                "description": datum["SituationDescription"],
                "sprite": self.sprite_service.get_sprite_infos(datum["IconSpriteId"]),
                "from": datum["FromDate"],
                "end": datum["EndDate"],
            }

            situations.append(situation)

        return situations

    def get_current_situation(self):
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

    def get_star_system_merchant_markers_from_api(self):
        """Get Star System Merchant Markers from API."""

        data = self.pixel_starships_api.get_star_system_markers()
        markers = []

        for datum in data:
            if datum["MarkerType"] != "MerchantShip":
                continue

            costs = self.pixyship_service.parse_assets_from_string(datum["CostString"])
            rewards = self.pixyship_service.parse_assets_from_string(datum["RewardString"])

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
                "sprite": self.sprite_service.get_sprite_infos(datum["SpriteId"]),
                "items": availables_items,
                "expires": expiry_date,
            }

            markers.append(marker)

        return markers

    def format_daily_sale_options(self, sale_item_mask):
        """ "From flag determine Sale options."""

        result = []
        options = self.pixel_starships_api.parse_sale_item_mask(sale_item_mask)

        for option in options:
            name = IAP_NAMES[option]
            result.append({"name": name, "value": option})

        return result

    @staticmethod
    def get_last_sales_from_db(sale_type, sale_type_id, limit):
        """Get last sales from database."""

        result: list[DailySale] = (
            DailySale.query.filter_by(type_id=sale_type_id, type=sale_type)
            .order_by(desc(DailySale.sale_at))
            .limit(limit)
            .all()
        )

        last_sales = []
        for row in result:
            last_sales.append(
                {
                    "id": row.id,
                    "date": row.sale_at,
                    "sale_from": SALE_FROM_MAP.get(row.sale_from, row.sale_from),
                    "currency": row.currency,
                    "price": row.price,
                }
            )

        return last_sales

    def get_last_sales_by_sale_from_from_db(self, sale_from, limit):
        """Get last sales for given type from database."""

        if sale_from == "blue_cargo":
            sale_from_values = ["blue_cargo_mineral", "blue_cargo_starbux"]
        else:
            sale_from_values = [sale_from]

        results: list[tuple[DailySale, Record]] = (
            db.session.query(DailySale, Record)
            .join(
                Record,
                and_(DailySale.type == Record.type, DailySale.type_id == Record.type_id, Record.current == True),  # noqa: E712
            )
            .filter(DailySale.sale_from.in_(sale_from_values))
            .order_by(DailySale.sale_at.desc())
            .limit(limit)
            .all()
        )

        last_sales = []
        for row in results:
            daily_sale = row[0]
            record = row[1]

            sprite = self.sprite_service.get_sprite_infos(record.sprite_id)

            last_sale = {
                "type": record.type.lower(),
                "id": record.type_id,
                "name": record.name,
                "sprite": sprite,
                "currency": daily_sale.currency,
                "price": daily_sale.price,
                "date": str(daily_sale.sale_at),
            }

            if record.type == TypeEnum.CHARACTER:
                last_sale["char"] = self.character_service.characters[record.type_id]
            elif record.type == TypeEnum.ITEM:
                item = self.item_service.items[record.type_id]
                last_sale["item"] = ItemService.create_light_item(item)

            last_sales.append(last_sale)

        return last_sales
