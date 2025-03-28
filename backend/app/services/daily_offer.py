import datetime
from functools import cached_property

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
from app.ext import cache, db
from app.models import DailySale, Record
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.services.item import ItemService
from app.utils.calculation import format_delta_time
from app.utils.pss import get_type_enum_from_string


class DailyOfferService(BaseService):
    """Service to manage daily offers."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()

    @cached_property
    @cache.cached(key_prefix="daily_offers")
    def daily_offers(self) -> dict:
        """Get daily offers."""
        return self.get_daily_offers_from_api()

    @cached_property
    @cache.cached(key_prefix="promotions")
    def promotions(self) -> list[dict]:
        """Get promotions."""
        return self.get_promotions_from_api()

    @cached_property
    @cache.cached(key_prefix="situations")
    def situations(self) -> list[dict]:
        """Get situations."""
        return self.get_situations_from_api()

    @cached_property
    @cache.cached(key_prefix="star_system_merchant_markers")
    def star_system_merchant_markers(self) -> list[dict]:
        """Get Star System Merchant Markers."""
        return self.get_star_system_merchant_markers_from_api()

    def get_daily_offers_from_api(self) -> dict:
        """Get settings service data, sales, motd from API."""
        dailies: dict = self.pixel_starships_api.get_dailies()
        promotions = self.get_current_promotions()

        daily_promotions = [promotion for promotion in promotions if promotion["type"] == "DailyDealOffer"]

        daily_object = None
        if dailies["SaleType"] == "FleetGift":
            rewards = self.pixyship_service.parse_assets_from_string(dailies["SaleRewardString"])
            if rewards:
                # for now, we assume we only have 1 reward
                reward = rewards[0]

                daily_object = self.format_daily_object(reward["count"], reward["type"], reward["data"], reward["id"])
        else:
            record_type = get_type_enum_from_string(dailies["SaleType"])
            if record_type is None or record_type == TypeEnum.NONE:
                current_app.logger.error("Cannot get record type from string %s", dailies["SaleType"])
                record_details = None
            else:
                record_details = self.record_details_service.get_record_details(
                    record_type, int(dailies["SaleArgument"])
                )

            daily_object = self.format_daily_object(
                1,
                dailies["SaleType"],
                record_details,
                int(dailies["SaleArgument"]),
            )

        daily_rewards_price = self.format_daily_price(
            int(dailies["DailyRewardArgument"]),
            dailies["DailyRewardType"],
        )

        shop_record_type = get_type_enum_from_string(dailies["LimitedCatalogType"])
        if shop_record_type is None:
            current_app.logger.error("Cannot get record type from string %s", dailies["LimitedCatalogType"])
            shop_record_details = None
        else:
            shop_record_details = self.record_details_service.get_record_details(
                shop_record_type,
                int(dailies["LimitedCatalogArgument"]),
            )

        shop_cost = self.format_daily_price(
            dailies["LimitedCatalogCurrencyAmount"],
            dailies["LimitedCatalogCurrencyType"],
        )

        offers = {
            "shop": {
                "sprite": self.sprite_service.get_sprite_infos(SHOP_SPRITE_ID),
                "object": self.format_daily_object(
                    1,
                    dailies["LimitedCatalogType"],
                    shop_record_details,
                    int(dailies["LimitedCatalogArgument"]),
                ),
                "cost": shop_cost,
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
                        daily_rewards_price,
                        None,
                    ),
                    *self.parse_daily_items(dailies["DailyItemRewards"]),
                ],
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

        return {
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

    def get_current_promotions(self) -> list[dict]:
        """Get running promotions depending on the current date."""
        utc_now = datetime.datetime.now(tz=datetime.UTC)

        promotions = []

        for promotion in self.promotions:
            # skip infinite promos
            if promotion["from"] == "2000-01-01T00:00:00":
                continue

            from_date = datetime.datetime.strptime(promotion["from"], "%Y-%m-%dT%H:%M:%S").astimezone(datetime.UTC)
            end_date = datetime.datetime.strptime(promotion["end"], "%Y-%m-%dT%H:%M:%S").astimezone(datetime.UTC)
            if from_date <= utc_now <= end_date:
                promotion_left_delta = end_date - utc_now
                promotion["left"] = format_delta_time(promotion_left_delta)

                promotions.append(promotion)

        return promotions

    def get_promotions_from_api(self) -> list[dict]:
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
    def format_daily_object(count: int, type_str: str, object_: dict | None, type_id: int | None) -> dict | None:
        """Format daily object."""
        if type_str == "None":
            return None

        return {
            "count": count,
            "type": type_str.lower(),
            "id": type_id,
            "object": object_,
        }

    @staticmethod
    def format_daily_price(amount: int, currency: str) -> dict:
        """Format daily price."""
        return {
            "price": amount,
            "currency": currency,
        }

    def parse_daily_cargo(self, item_list_string: str, cost_list_string: str) -> list[dict]:
        """Split daily cargo data into prices and items."""
        items = self.parse_daily_items(item_list_string)

        splitted_prices = [i.split(":") for i in cost_list_string.split("|")]
        prices = []
        for splitted_price in splitted_prices:
            if len(splitted_price) < 2:
                current_app.logger.error("Cannot parse cost_list_string %s", splitted_price)
                continue

            price: dict = {"currency": splitted_price[0]}

            amount = splitted_price[1].split("x")
            if len(amount) > 1:
                item_id = int(amount[0])
                price["price"] = item_id
                price["count"] = amount[1]
                price["object"] = self.item_service.items[item_id]
            else:
                price["price"] = int(splitted_price[1])

            prices.append(price)

        return [
            {
                "sprite": {},
                "object": item,
                "cost": price,
                "details": None,
                "expires": None,
            }
            for item, price in zip(items, prices, strict=True)
        ]

    def parse_daily_items(self, item_list_string: str) -> list[dict]:
        """Parse daily items from API."""
        items_split = [i.split("x") for i in item_list_string.split("|")]
        return [
            {
                "count": int(item[1]),
                "type": "item",
                "id": int(item[0]),
                "object": self.item_service.items[int(item[0])],
            }
            for item in items_split
        ]

    def get_situations_from_api(self) -> list[dict]:
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

    def get_current_situation(self) -> dict | None:
        """Get running situation depending on the current date."""
        utc_now = datetime.datetime.now(tz=datetime.UTC)

        for situation in self.situations:
            from_date = datetime.datetime.strptime(situation["from"], "%Y-%m-%dT%H:%M:%S").astimezone(datetime.UTC)
            end_date = datetime.datetime.strptime(situation["end"], "%Y-%m-%dT%H:%M:%S").astimezone(datetime.UTC)
            if from_date <= utc_now <= end_date:
                situation_left_delta = end_date - utc_now
                situation["left"] = format_delta_time(situation_left_delta)

                return situation

        return None

    def get_star_system_merchant_markers_from_api(self) -> list[dict]:
        """Get Star System Merchant Markers from API."""
        data = self.pixel_starships_api.get_star_system_markers()
        markers = []

        for datum in data:
            if datum["MarkerType"] != "MerchantShip":
                continue

            costs = self.pixyship_service.parse_assets_from_string(datum["CostString"])
            rewards = self.pixyship_service.parse_assets_from_string(datum["RewardString"])

            availables_items = []
            for i in range(len(rewards)):
                availables_item = {"cost": costs[i], "reward": rewards[i]}

                availables_items.append(availables_item)

            expiry_date = datum["ExpiryDate"]

            # Savy don't put midnight but 5s before...
            if expiry_date.endswith("T23:59:55"):
                next_utc = datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=1)
                expiry_date = next_utc.strftime("%Y-%m-%dT%H:%M:%S")

            marker = {
                "title": datum["Title"],
                "sprite": self.sprite_service.get_sprite_infos(datum["SpriteId"]),
                "items": availables_items,
                "expires": expiry_date,
            }

            markers.append(marker)

        return markers

    def format_daily_sale_options(self, sale_item_mask: int) -> list[dict]:
        """From flag determine Sale options."""
        result = []
        options = self.pixel_starships_api.parse_sale_item_mask(int(sale_item_mask))

        for option in options:
            name = IAP_NAMES[option]
            result.append({"name": name, "value": option})

        return result

    @staticmethod
    def get_last_sales_from_db(sale_type: TypeEnum, sale_type_id: int, limit: int) -> list[dict]:
        """Get last sales from database."""
        result: list[DailySale] = (
            DailySale.query.filter_by(type_id=sale_type_id, type=sale_type)
            .order_by(desc(DailySale.sale_at))
            .limit(limit)
            .all()
        )

        return [
            {
                "id": row.id,
                "date": row.sale_at,
                "sale_from": SALE_FROM_MAP.get(row.sale_from, row.sale_from),
                "currency": row.currency,
                "price": row.price,
            }
            for row in result
        ]

    def get_last_sales_by_sale_from_from_db(self, sale_from: str, limit: int) -> list[dict]:
        """Get last sales for given type from database."""
        sale_from_values = ["blue_cargo_mineral", "blue_cargo_starbux"] if sale_from == "blue_cargo" else [sale_from]

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
