import re
from collections import defaultdict
from functools import cached_property

from sqlalchemy import desc, text

from app.constants import SHORT_ENHANCE_MAP
from app.ext import cache
from app.ext.db import db
from app.models import Listing
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService

# one offstat in a market message, e.g. "(+12.2 Ability)", "(+5.1 Fire Resistance)" or "(+12,5 Ability)"
OFFSTAT_PATTERN = re.compile(r"\(\+\s*(\d+(?:[.,]\d+)?)\s+([^()]+?)\s*\)")


class MarketService(BaseService):
    """Service to manage market."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def prices(self) -> dict[int, dict]:
        """Get prices data."""
        prices = cache.get("prices")
        if prices is None:
            prices = self.get_prices_from_db()
            cache.set("prices", prices)

        return prices

    def update_cache(self) -> None:
        """Load prices in cache."""
        cache.set("prices", self.get_prices_from_db())

    @staticmethod
    def get_prices_from_db() -> dict[int, dict]:
        """Get all history market summary from database."""
        sql = """
                SELECT l.item_id
                     , l.currency
                     , SUM(l.amount)                                                    AS count
                     , percentile_disc(.25) WITHIN GROUP (ORDER BY l.price::float8 / l.amount)  AS p25
                     , percentile_disc(.5) WITHIN GROUP (ORDER BY l.price::float8 / l.amount)   AS p50
                     , percentile_disc(.75) WITHIN GROUP (ORDER BY l.price::float8 / l.amount)  AS p75
                FROM listing l
                WHERE l.amount > 0
                  AND l.sale_at > (now() - INTERVAL '48 HOURS')
                GROUP BY l.item_id, l.currency
            """

        result = db.session.execute(text(sql)).fetchall()
        prices: dict = defaultdict(dict)
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
    def get_item_prices(item_id: int) -> dict:
        """Get item history market from database."""
        sql = """
                SELECT item_id
                     , item_name
                     , currency
                     , sale_at::DATE                                               AS sale_date
                     , SUM(amount)                                                 AS count
                     , percentile_disc(.25) WITHIN GROUP (ORDER BY price::float8 / amount) AS p25
                     , percentile_disc(.5) WITHIN GROUP (ORDER BY price::float8 / amount)  AS p50
                     , percentile_disc(.75) WITHIN GROUP (ORDER BY price::float8 / amount) AS p75
                FROM listing
                WHERE item_id = :item_id
                  AND amount > 0
                  -- whole days only, written without a cast on sale_at so the index can be used
                  AND sale_at >= date_trunc('day', now() - INTERVAL '6 months') + INTERVAL '1 day'
                GROUP BY item_id, item_name, currency, sale_at::DATE
                ORDER BY item_id, item_name, currency, sale_at::DATE
            """

        result = db.session.execute(text(sql), {"item_id": item_id}).fetchall()
        prices: dict[int, dict] = defaultdict(lambda: defaultdict(dict))

        for row in result:
            currency = row[2]
            sale_date = str(row[3])
            prices[currency][sale_date] = {
                "count": row[4],
                "p25": row[5],
                "p50": row[6],
                "p75": row[7],
            }

        return {
            "id": item_id,
            "prices": prices,
        }

    @staticmethod
    def get_item_last_players_sales_from_db(item_id: int, limit: int) -> list[dict]:
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
            offstats = MarketService.parse_offstats(row[7])

            last_sales.append(
                {
                    "id": int(row[6]),
                    "date": str(row[0]),
                    "quantity": row[1],
                    "currency": row[2],
                    "price": row[3],
                    "buyer": row[4],
                    "seller": row[5],
                    "offstats": offstats,
                },
            )

        return last_sales

    @staticmethod
    def parse_offstats(message: str | None) -> list[dict]:
        """Parse all offstats from a market message, e.g. "Selling 1 Item (+12.2 Ability) (+1.5 Engine)"."""
        if not message:
            return []

        return [
            {
                "value": value,
                "bonus": bonus,
                # the map keys are the API enhancement names, without spaces (e.g. "FireResistance")
                "short_bonus": SHORT_ENHANCE_MAP.get(bonus.replace(" ", ""), bonus),
            }
            for value, bonus in OFFSTAT_PATTERN.findall(message)
        ]

    @staticmethod
    def get_sales_from_api(pixel_starships_api: PixelStarshipsApi, item_id: int) -> list:
        """Get market history of item."""
        # get max sale_id to retrieve only new sales
        max_sale_id_result = (
            Listing.query.filter(Listing.item_id == item_id).order_by(desc(Listing.id)).limit(1).first()
        )

        if max_sale_id_result is not None:
            max_sale_id = max_sale_id_result.id if max_sale_id_result.id is not None else 0
        else:
            max_sale_id = 0

        return pixel_starships_api.get_sales(item_id, max_sale_id)

    @staticmethod
    def get_market_messages_from_api(item_id: int) -> list:
        """Get market messages of item."""
        pixel_starships_api = PixelStarshipsApi()
        return pixel_starships_api.get_market_messages(item_id)
