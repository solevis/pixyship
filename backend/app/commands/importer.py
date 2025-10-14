import datetime
import random
import time
from collections.abc import Callable
from pathlib import Path
from urllib import request

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext
from sqlalchemy.dialects.postgresql import insert

from app.constants import PSS_SPRITES_URL
from app.ext.db import db
from app.models import Alliance, DailySale, Listing, MarketMessage, Player
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.achievement import AchievementService
from app.services.changes import ChangesService
from app.services.character import CharacterService
from app.services.collection import CollectionService
from app.services.craft import CraftService
from app.services.daily_offer import DailyOfferService
from app.services.item import ItemService
from app.services.market import MarketService
from app.services.missile import MissileService
from app.services.player import PlayerService
from app.services.prestige import PrestigeService
from app.services.research import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.skin import SkinService
from app.services.sprite import SpriteService
from app.services.training import TrainingService
from app.utils.pss import api_sleep, get_type_enum_from_string

importer_cli = AppGroup("import", help="Import data from PixyShip API.")


def log_command(func: Callable) -> Callable:
    """Log the start and end of a command."""

    def wrapper(*func_args: tuple, **func_kwargs: dict) -> Callable:
        start_time = time.time()
        current_app.logger.info("START")
        result = func(*func_args, **func_kwargs)

        end_time = time.time()  # Capturer le temps de fin
        elapsed_time = end_time - start_time  # Calculer le temps écoulé
        current_app.logger.info("END (%.2fs)", elapsed_time)
        return result

    return wrapper


@importer_cli.command("players", help="Get top players and save them in database.")
@with_appcontext
@log_command
def import_players() -> None:
    """Get all top 100 players and top 100 alliances' players and save them in database."""
    player_service = PlayerService()

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no players to import")
        return

    current_app.logger.info("Importing players")

    current_app.logger.info("## top 100 players")
    top_users = list(player_service.get_top100_users_from_api().items())
    api_sleep(5)

    current_app.logger.info("## top 100 alliances")
    count = 0
    top_alliances = player_service.get_top100_alliances_from_api()
    for alliance_id, alliance in list(top_alliances.items()):
        try:
            count += 1
            current_app.logger.info("[%d/100] %s (%d)...", count, alliance["name"], alliance_id)
            top_users += list(player_service.get_alliance_users_from_api(alliance_id).items())
            api_sleep(5)
        except Exception:
            current_app.logger.exception("Error when importing alliance (%d) users", alliance_id)

    try:
        # purge old data
        db.session.query(Player).delete()
        db.session.query(Alliance).delete()
        db.session.commit()
    except Exception:
        current_app.logger.exception("Error when saving players in database")
        db.session.rollback()

    # save new data
    save_users(top_users)

    current_app.logger.info("Done")


@importer_cli.command("assets", help="Get all assets and save them in database.")
@with_appcontext
@log_command
def import_assets() -> None:
    """Get all items, crews, rooms, ships and save them in database."""
    item_service = ItemService()
    character_service = CharacterService()
    room_service = RoomService()
    ship_service = ShipService()
    collection_service = CollectionService()
    research_service = ResearchService()
    sprite_service = SpriteService()
    skin_service = SkinService()
    training_service = TrainingService()
    achievement_service = AchievementService()
    craft_service = CraftService()
    missile_service = MissileService()
    changes_service = ChangesService()

    current_app.logger.info("Importing sprites...")
    sprite_service.update_sprites()
    sprite_service.update_cache()

    current_app.logger.info("Importing trainings...")
    training_service.update_trainings()
    training_service.update_cache()

    current_app.logger.info("Importing items...")
    item_service.update_items()
    item_service.update_cache()

    current_app.logger.info("Importing characters...")
    character_service.update_characters()
    character_service.update_cache()

    current_app.logger.info("Importing researches...")
    research_service.update_researches()
    research_service.update_cache()

    current_app.logger.info("Importing rooms...")
    room_service.update_rooms()
    room_service.update_cache()

    current_app.logger.info("Importing ships...")
    ship_service.update_ships()
    ship_service.update_cache()

    current_app.logger.info("Importing collections...")
    collection_service.update_collections()
    collection_service.update_cache()

    current_app.logger.info("Importing skinsets...")
    skin_service.update_skinsets()
    skin_service.update_cache()

    current_app.logger.info("Importing skins...")
    skin_service.update_skins()
    skin_service.update_cache()

    current_app.logger.info("Importing achievements...")
    achievement_service.update_achievements()
    achievement_service.update_cache()

    current_app.logger.info("Importing crafts...")
    craft_service.update_crafts()
    craft_service.update_cache()

    current_app.logger.info("Importing missiles...")
    missile_service.update_missiles()
    missile_service.update_cache()

    current_app.logger.info("Invalidating changes cache...")
    changes_service.update_cache()

    current_app.logger.info("Done")


@importer_cli.command("prestiges", help="Get all prestiges and save them in database.")
@with_appcontext
@log_command
def import_prestiges() -> None:
    """Import prestiges for checking changes."""
    prestige_service = PrestigeService()

    current_app.logger.info("Importing prestiges...")
    prestige_service.update_prestiges()

    current_app.logger.info("Done")


@importer_cli.command("daily-sales", help="Get all daily sales and save them in database.")
@with_appcontext
@log_command
def import_daily_sales() -> None:
    """Get all items, crews, rooms, ships on sale today and save them in database."""
    daily_offer_service = DailyOfferService()

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no daily sales to import")
        return

    utc_now = datetime.datetime.now(tz=datetime.UTC)
    today = datetime.date(utc_now.year, utc_now.month, utc_now.day)

    current_app.logger.info("Importing promotions...")
    promotions = daily_offer_service.get_current_promotions()
    for promotion in promotions:
        for reward in promotion["rewards"]:
            if reward["type"] in ["starbux", "purchasePoints"]:
                continue

            daily_sale = DailySale(
                type=reward["type"],
                type_id=reward["id"],
                sale_at=promotion["from"],
                sale_from="promotion_{}".format(promotion["type"].lower()),
                currency=None,
                price=None,
            )

            save_daily_sale(daily_sale)

    current_app.logger.info("Importing daily offers...")
    dailies_offers = daily_offer_service.daily_offers["offers"]
    if not dailies_offers:
        current_app.logger.error("Empty dailies_offers")
        return

    daily_shop_offer = dailies_offers["shop"]["object"]
    if not daily_shop_offer:
        current_app.logger.error("Empty daily_shop_offer")
    else:
        current_app.logger.info("Importing daily shop...")
        daily_sale = DailySale(
            type=daily_shop_offer["type"],
            type_id=daily_shop_offer["id"],
            sale_at=today,
            sale_from="shop",
            currency=dailies_offers["shop"]["cost"]["currency"].lower(),
            price=dailies_offers["shop"]["cost"]["price"],
        )

        save_daily_sale(daily_sale)

    daily_bank_offer = dailies_offers["sale"]["object"]
    if not daily_bank_offer:
        # no sale today, no need to log an error because it's normal
        current_app.logger.info("Empty daily_bank_offer")
    else:
        current_app.logger.info("Importing daily bank...")
        daily_sale = DailySale(
            type=daily_bank_offer["type"],
            type_id=daily_bank_offer["id"],
            sale_at=today,
            sale_from="sale",
            currency=None,
            price=None,
        )

        save_daily_sale(daily_sale)

    daily_rewards_offers = dailies_offers["dailyRewards"]["objects"]
    if not daily_rewards_offers:
        current_app.logger.error("Empty daily_rewards_offers")
    else:
        current_app.logger.info("Importing daily rewards...")
        for daily_rewards_offer in daily_rewards_offers:
            if daily_rewards_offer["type"] in ["currency", "starbux", "purchasePoints"]:
                continue

            daily_sale = DailySale(
                type=daily_rewards_offer["type"],
                type_id=daily_rewards_offer["id"],
                sale_at=today,
                sale_from="daily_rewards",
                currency=None,
                price=None,
            )

            save_daily_sale(daily_sale)

    daily_bluecargo_mineral_offer = dailies_offers["blueCargo"]["mineralCrew"]
    if not daily_bluecargo_mineral_offer:
        current_app.logger.error("Empty daily_bluecargo_mineral_offer")
    else:
        current_app.logger.info("Importing daily blue cargo mineral...")
        daily_sale = DailySale(
            type=daily_bluecargo_mineral_offer["type"],
            type_id=daily_bluecargo_mineral_offer["id"],
            sale_at=today,
            sale_from="blue_cargo_mineral",
            currency="mineral",
            price=None,
        )

        save_daily_sale(daily_sale)

    daily_bluecargo_starbux_offer = dailies_offers["blueCargo"]["starbuxCrew"]
    if not daily_bluecargo_starbux_offer:
        current_app.logger.error("Empty daily_bluecargo_starbux_offer")
    else:
        current_app.logger.info("Importing daily blue cargo starbux...")
        daily_sale = DailySale(
            type=daily_bluecargo_starbux_offer["type"],
            type_id=daily_bluecargo_starbux_offer["id"],
            sale_at=today,
            sale_from="blue_cargo_starbux",
            currency="starbux",
            price=None,
        )

        save_daily_sale(daily_sale)

    daily_greencargo_offers = dailies_offers["greenCargo"]["items"]
    if not daily_greencargo_offers:
        current_app.logger.error("Empty daily_greencargo_offers")
    else:
        current_app.logger.info("Importing daily green cargo...")
        for daily_greencargo_offer in daily_greencargo_offers:
            if daily_greencargo_offer["object"]["type"] in ["starbux", "purchasePoints"]:
                continue

            daily_sale = DailySale(
                type=daily_greencargo_offer["object"]["type"],
                type_id=daily_greencargo_offer["object"]["id"],
                sale_at=today,
                sale_from="green_cargo",
                currency=daily_greencargo_offer["cost"]["currency"],
                price=daily_greencargo_offer["cost"]["price"],
            )

            save_daily_sale(daily_sale)


def save_daily_sale(daily_sale: DailySale) -> None:
    """Save daily sale in database."""
    daily_sale_type = get_type_enum_from_string(daily_sale.type)
    try:
        insert_command = (
            insert(DailySale.__table__)
            .values(
                type=daily_sale_type,
                type_id=daily_sale.type_id,
                sale_at=daily_sale.sale_at,
                sale_from=daily_sale.sale_from,
                currency=daily_sale.currency,
                price=daily_sale.price,
            )
            .on_conflict_do_nothing()
        )

        db.session.execute(insert_command)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Error when saving Daily Sale in database")
        db.session.rollback()


@importer_cli.command("market", help="Get last market sales and save them in database.")
@click.option("--one-item-only", is_flag=True, help="Import randomly only one item")
@click.option("--item-id", type=int, default=None, help="Import only the given item")
@with_appcontext
@log_command
def import_market(one_item_only: bool, item_id: int | None) -> None:
    """Get last market sales and save them in database."""
    item_service = ItemService()
    market_service = MarketService()
    pixel_starships_api = PixelStarshipsApi()

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no sales to import")
        return

    current_app.logger.info("Importing market sales")

    # no need to get sales of items not saleable
    items = item_service.items
    saleable_items: dict[int, dict] = {item_id: item for item_id, item in items.items() if item["saleable"]}

    if item_id:
        try:
            saleable_items = {item_id: saleable_items[item_id]}
        except KeyError:
            current_app.logger.exception("Unknown item %d", item_id)
            return

    total = len(saleable_items)
    if one_item_only:
        total = 1

    saleable_items_items = list(saleable_items.items())
    saleable_items_ordered = random.sample(saleable_items_items, k=len(saleable_items_items))

    for count, (current_item_id, current_item) in enumerate(saleable_items_ordered, start=1):
        current_app.logger.info("[%d/%d] item: %s (%d)", count, total, current_item["name"], current_item_id)

        sales = market_service.get_sales_from_api(pixel_starships_api, current_item_id)
        current_app.logger.info("[%d/%d] retrieved: %d", count, total, len(sales))

        for sale in sales:
            listing = Listing(
                id=sale["SaleId"],
                sale_at=sale["StatusDate"],
                item_name=current_item["name"],
                item_id=current_item_id,
                amount=sale["Quantity"],
                currency=sale["CurrencyType"],
                price=sale["CurrencyValue"],
                user_id=sale["BuyerShipId"],
                user_name=sale.get("BuyerShipName", ""),
                seller_id=sale["SellerShipId"],
                seller_name=sale.get("SellerShipName", ""),
            )

            db.session.merge(listing)

        current_app.logger.info("[%d/%d] saved: %d", count, total, len(sales))
        db.session.commit()

        if one_item_only:
            break

        api_sleep(3, force_sleep=True)

    market_service.update_cache()
    current_app.logger.info("Done")


@importer_cli.command("market-messages", help="Get last market messages and save them in database.")
@click.option("--one-item-only", is_flag=True, help="Import randomly only one item")
@click.option("--item-id", type=int, default=None, help="Import only the given item")
@with_appcontext
@log_command
def import_market_messages(one_item_only: bool, item_id: int | None) -> None:
    """Get last market messages and save them in database."""
    item_service = ItemService()

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no market messages to import")
        return

    current_app.logger.info("Importing market messages")

    # no need to get sales of items not saleable
    items = item_service.items
    items_with_offstat: dict[int, dict] = {item_id: item for item_id, item in items.items() if item["has_offstat"]}

    if item_id:
        try:
            items_with_offstat = {item_id: items_with_offstat[item_id]}
        except KeyError:
            current_app.logger.exception("Unknown item %d", item_id)
            return

    total = len(items_with_offstat)
    if one_item_only:
        total = 1

    items_with_offstat_items: list[tuple[int, dict]] = list(items_with_offstat.items())
    items_with_offstat_ordered: list[tuple[int, dict]] = random.sample(
        items_with_offstat_items, k=len(items_with_offstat_items)
    )

    for count, (current_item_id, current_item) in enumerate(items_with_offstat_ordered, start=1):
        current_app.logger.info("[%d/%d] item: %s (%d)", count, total, current_item["name"], current_item_id)

        messages = MarketService.get_market_messages_from_api(current_item_id)
        current_app.logger.info("[%d/%d] retrieved: %d", count, total, len(messages))

        for message in messages:
            market_message = MarketMessage(
                id=message["MessageId"],
                message=message["Message"],
                sale_id=message["SaleId"],
                item_id=current_item_id,
                user_id=message["UserId"],
                message_type=message["MessageType"],
                channel_id=message["ChannelId"],
                activit_type=message["ActivityType"],
                message_date=message["MessageDate"],
            )

            save_market_message(market_message)

        db.session.commit()

        if one_item_only:
            break

        api_sleep(1, force_sleep=True)

    current_app.logger.info("Done")


def save_market_message(market_message: MarketMessage) -> None:
    """Save market message in database."""
    try:
        insert_command = (
            insert(MarketMessage.__table__)
            .values(
                id=market_message.id,
                message=market_message.message,
                sale_id=market_message.sale_id,
                item_id=market_message.item_id,
                user_id=market_message.user_id,
                message_type=market_message.message_type,
                channel_id=market_message.channel_id,
                activit_type=market_message.activit_type,
                message_date=market_message.message_date,
            )
            .on_conflict_do_nothing()
        )

        db.session.execute(insert_command)
        db.session.commit()
    except Exception:
        current_app.logger.exception("Error when saving Market Message in database")
        db.session.rollback()


@importer_cli.command("sprites", help="Download sprites from PSS.")
@with_appcontext
@log_command
def dowload_sprites() -> None:
    """Download sprites from PSS."""
    sprite_service = SpriteService()

    sprites_directory = Path(current_app.config["SPRITES_DIRECTORY"])
    if not sprites_directory.exists():
        sprites_directory.mkdir()

    sprites = sprite_service.sprites

    for sprite in sprites.values():
        image_number = sprite["image_file"]
        filename = current_app.config["SPRITES_DIRECTORY"] + f"/{image_number}.png"

        if not Path(filename).is_file():
            current_app.logger.info("Downloading %s", filename)
            url = PSS_SPRITES_URL.format(image_number)
            try:
                request.urlretrieve(url, filename)
            except Exception:
                current_app.logger.exception("Error downloading sprite: %s", url)


def save_users(users: list) -> None:
    """Save users and attached alliance in database."""
    for user_id, user in users:
        player = Player(
            id=user_id,
            name=user["name"],
            trophies=int(user["trophies"]),
            alliance_id=user["alliance_id"],
            last_login_at=user["last_login_at"],
        )
        db.session.merge(player)

        if user["alliance_name"]:
            alliance = Alliance(
                id=user["alliance_id"],
                name=user["alliance_name"],
                sprite_id=user["alliance_sprite_id"],
            )
            db.session.merge(alliance)

        db.session.commit()
