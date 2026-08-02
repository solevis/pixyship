"""Handle real-time PSS market Pusher events (see app/commands/importer.py's "market-worker" command).

The public "market" Pusher channel only broadcasts a free-text notification per market action
(listed / sold / expired), with a SaleId, a user (the one performing the action) and a short
message. It does not expose the structured fields (ItemDesignId, BuyerShipId, SellerShipId) that
the "MarketService/ListSalesByItemDesignId" endpoint returns, and doesn't reveal a numeric id for
the other side of a completed sale. Resolving those from the broadcast alone is therefore
best-effort, based on observed real traffic:

- "listed" messages look like "Selling <amount> <ItemName>" and are the seller's action
- "sold" messages look like "Bought <amount> <ItemName> from <SellerName>" and are the *buyer's*
  action: the buyer is known (id + name), the seller is only known by name (free text), not id
- the item is resolved by matching the longest known item name found in the message text
- the price/currency is parsed from the free-text "activity argument", e.g. "gas:500000"

This was validated against a short sample of real production traffic, but should keep being
monitored (unresolved items/prices are logged as warnings) and the parsing tuned if needed.
"""

import re
import time
from datetime import datetime

from flask import current_app
from pssapi.entities import Message
from pssapi.enums import ActivityType, MessageType
from sqlalchemy.dialects.postgresql import insert

from app.ext.db import db
from app.models import Listing, MarketMessage
from app.services.base import BaseService
from app.services.item import ItemService
from app.utils.pss import parse_price_from_pricestring

# e.g. "Selling 11 Void Particle" / "Bought 3 Void Particle from SomeName"
QUANTITY_PATTERN = re.compile(r"^(?:Selling|Bought)\s+(?P<amount>\d+)\s+", re.IGNORECASE)

# e.g. "Bought 3 Void Particle from SomeName" -> "SomeName"
SELLER_NAME_PATTERN = re.compile(r"\bfrom\s+(?P<seller>.+)$", re.IGNORECASE)

# fallback when the quantity can't be parsed from the message text
DEFAULT_SALE_AMOUNT = 1


class MarketPusherService(BaseService):
    """Resolve and persist PSS market Pusher events (item listed / sold / expired) in real time."""

    def __init__(self) -> None:
        super().__init__()
        self._items_by_name_cache: list[tuple[str, int]] | None = None
        self._items_by_name_cached_at: float = 0.0

    @property
    def items_by_name(self) -> list[tuple[str, int]]:
        """Get known item names sorted from longest to shortest, to match the most specific name first.

        This is a derived index (name -> id, sorted), not a duplicate of ItemService's own "items"
        cache: it's local to this worker process and only exists to avoid re-sorting the whole
        catalog on every single Pusher message. Its freshness follows the same CACHE_DEFAULT_TIMEOUT
        as ItemService.items itself (a fresh ItemService() is used to re-check that cache, since
        ItemService.items is a cached_property and would otherwise stay pinned to whatever it read
        at the first call for this instance's lifetime).
        """
        now = time.monotonic()
        ttl = current_app.config["CACHE_DEFAULT_TIMEOUT"]
        is_stale = (now - self._items_by_name_cached_at) > ttl

        if self._items_by_name_cache is None or is_stale:
            items = ItemService().items
            names = [(item["name"], item_id) for item_id, item in items.items() if item["name"]]
            self._items_by_name_cache = sorted(names, key=lambda name_id: len(name_id[0]), reverse=True)
            self._items_by_name_cached_at = now

        return self._items_by_name_cache

    def resolve_item(self, text: str) -> tuple[int, str] | None:
        """Best-effort resolution of the item referenced in a free-text market message."""
        lowered = text.lower()
        for name, item_id in self.items_by_name:
            if name.lower() in lowered:
                return item_id, name

        return None

    @staticmethod
    def parse_price(activity_argument: str | None) -> tuple[int, str] | None:
        """Best-effort parsing of a market Pusher activity argument, e.g. "gas:500000"."""
        if not activity_argument:
            return None

        amount, currency = parse_price_from_pricestring(activity_argument)
        if not amount or not currency:
            return None

        return amount, currency.capitalize()

    @staticmethod
    def parse_quantity(message_text: str | None) -> int | None:
        """Best-effort parsing of the sold/listed quantity from the message text."""
        if not message_text:
            return None

        match = QUANTITY_PATTERN.match(message_text)
        if not match:
            return None

        return int(match.group("amount"))

    @staticmethod
    def parse_seller_name(message_text: str | None) -> str | None:
        """Best-effort parsing of the seller name from a "sold" message text (buyer's numeric id isn't available)."""
        if not message_text:
            return None

        match = SELLER_NAME_PATTERN.search(message_text)
        if not match:
            return None

        return match.group("seller").strip() or None

    @staticmethod
    def to_naive_datetime(value: datetime | None) -> datetime | None:
        """Strip timezone info, database columns are plain TIMESTAMP (no timezone)."""
        if value is None:
            return None

        return value.replace(tzinfo=None)

    def handle_message(self, raw_message: dict) -> None:
        """Handle a single message from the market Pusher channel (sync callback, see pssapi.pusher.Pusher)."""
        try:
            message = Message(dict(raw_message))
        except Exception:
            current_app.logger.exception("Unable to parse market pusher payload: %r", raw_message)
            return

        if message.message_id is None or message.message_type_enum != MessageType.MARKET:
            return

        activity_type = message.activity_type_enum
        if activity_type not in (ActivityType.MARKET_LISTED, ActivityType.MARKET_SOLD, ActivityType.MARKET_EXPIRED):
            return

        item = self.resolve_item(message.message or "")
        if item is None:
            current_app.logger.warning(
                "Could not resolve item from market pusher message %r (sale %s)",
                message.message,
                message.sale_id,
            )

        self.save_market_message(message, item[0] if item else None)

        if activity_type == ActivityType.MARKET_SOLD and item is not None:
            self.save_listing(message, item[0], item[1])

    @staticmethod
    def save_market_message(message: Message, item_id: int | None) -> None:
        """Save the raw market pusher message in database."""
        try:
            sale_id = int(message.sale_id)
        except (TypeError, ValueError):
            current_app.logger.warning("Market pusher message %s has no valid SaleId, skipping", message.message_id)
            return

        try:
            insert_command = (
                insert(MarketMessage.__table__)
                .values(
                    id=message.message_id,
                    message=message.message,
                    sale_id=sale_id,
                    item_id=item_id,
                    user_id=message.user_id,
                    message_type=message.message_type,
                    channel_id=str(message.channel_id),
                    activit_type=message.activity_type,
                    message_date=MarketPusherService.to_naive_datetime(message.message_date),
                )
                .on_conflict_do_nothing()
            )

            db.session.execute(insert_command)
            db.session.commit()
        except Exception:
            current_app.logger.exception("Error when saving market pusher message in database")
            db.session.rollback()

    @staticmethod
    def save_listing(message: Message, item_id: int, item_name: str) -> None:
        """Save a completed sale as a Listing, best-effort from the market pusher message."""
        price_info = MarketPusherService.parse_price(message.activity_argument)
        if price_info is None:
            current_app.logger.warning(
                "Could not parse price from market pusher activity argument %r for sale %s, skipping listing",
                message.activity_argument,
                message.sale_id,
            )
            return

        try:
            sale_id = int(message.sale_id)
        except (TypeError, ValueError):
            current_app.logger.warning(
                "Market pusher sold message %s has no valid SaleId, skipping listing", message.message_id
            )
            return

        price, currency = price_info
        amount = MarketPusherService.parse_quantity(message.message) or DEFAULT_SALE_AMOUNT

        listing = Listing(
            id=sale_id,
            sale_at=MarketPusherService.to_naive_datetime(message.message_date),
            item_name=item_name,
            item_id=item_id,
            amount=amount,
            currency=currency,
            price=price,
            # a "sold" message is broadcast as the buyer's action ("Bought X from <seller>"): the
            # buyer is known (id + name), the seller's name is in the free text but their numeric
            # id isn't available without an extra SearchUsers call
            user_id=message.user_id,
            user_name=message.user_name,
            seller_id=None,
            seller_name=MarketPusherService.parse_seller_name(message.message),
        )

        try:
            db.session.merge(listing)
            db.session.commit()
        except Exception:
            current_app.logger.exception("Error when saving market pusher listing in database")
            db.session.rollback()
