import datetime
import os
import random
import time
from typing import Callable, Any, Tuple, Dict
from urllib import request

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext
from sqlalchemy.dialects.postgresql import insert

from app.constants import PSS_SPRITES_URL
from app.ext.db import db
from app.models import Listing, Alliance, Player, DailySale
from app.models import MarketMessage
from app.pixyship import PixyShip
from app.utils import api_sleep

importer_cli = AppGroup("import", help="Import data from PixyShip API.")


def log_command(func: Callable) -> Callable:
    def wrapper(*func_args: Tuple[Any], **func_kwargs: Dict[str, Any]) -> Any:
        start_time = time.time()
        current_app.logger.info("START")
        result = func(*func_args, **func_kwargs)

        end_time = time.time()  # Capturer le temps de fin
        elapsed_time = end_time - start_time  # Calculer le temps écoulé
        current_app.logger.info(f"END ({elapsed_time:.2f}s)")
        return result

    return wrapper


@importer_cli.command("players", help="Get top players and save them in database.")
@with_appcontext
@log_command
def import_players():
    """Get all top 100 players and top 100 alliances' players and save them in database."""

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no players to import")
        return

    current_app.logger.info("Importing players")

    pixyship = PixyShip()

    current_app.logger.info("## top 100 players")
    top_users = list(pixyship.get_top100_users_from_api().items())
    api_sleep(5)

    current_app.logger.info("## top 100 alliances")
    count = 0
    top_alliances = pixyship.get_top100_alliances_from_api()
    for alliance_id, alliance in list(top_alliances.items()):
        try:
            count += 1
            current_app.logger.info("[{}/100] {} ({})...".format(count, alliance["name"], alliance_id))
            top_users += list(pixyship.get_alliance_users_from_api(alliance_id).items())
            api_sleep(5)
        except Exception as e:
            current_app.logger.exception("Error when importing alliance ({}) users: {}".format(alliance_id, e))

    try:
        # purge old data
        db.session.query(Player).delete()
        db.session.query(Alliance).delete()
        db.session.commit()
    except Exception as e:
        current_app.logger.exception("Error when saving players in database: {}".format(e))
        db.session.rollback()

    # save new data
    _save_users(top_users)

    current_app.logger.info("Done")


@importer_cli.command("assets", help="Get all assets and save them in database.")
@with_appcontext
@log_command
def import_assets():
    """Get all items, crews, rooms, ships and save them in database."""

    pixyship = PixyShip()

    current_app.logger.info("Importing items...")
    pixyship.update_items()

    current_app.logger.info("Importing characters...")
    pixyship.update_characters()

    current_app.logger.info("Importing rooms...")
    pixyship.update_rooms()

    current_app.logger.info("Importing ships...")
    pixyship.update_ships()

    current_app.logger.info("Importing collections...")
    pixyship.update_collections()

    current_app.logger.info("Importing researches...")
    pixyship.update_researches()

    current_app.logger.info("Importing sprites...")
    pixyship.update_sprites()

    current_app.logger.info("Importing skins...")
    pixyship.update_skins()

    current_app.logger.info("Importing trainings...")
    pixyship.update_trainings()

    current_app.logger.info("Importing achievements...")
    pixyship.update_achievements()

    current_app.logger.info("Importing crafts...")
    pixyship.update_crafts()

    current_app.logger.info("Importing missiles...")
    pixyship.update_missiles()

    current_app.logger.info("Done")


@importer_cli.command("prestiges", help="Get all prestiges and save them in database.")
@with_appcontext
@log_command
def import_prestiges():
    """Import prestiges for checking changes."""

    pixyship = PixyShip()

    current_app.logger.info("Importing prestiges...")
    pixyship.update_prestiges()

    current_app.logger.info("Done")


@importer_cli.command("daily-sales", help="Get all daily sales and save them in database.")
@with_appcontext
@log_command
def import_daily_sales():
    """Get all items, crews, rooms, ships on sale today and save them in database."""

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no daily sales to import")
        return

    pixyship = PixyShip()

    utc_now = datetime.datetime.utcnow()
    today = datetime.date(utc_now.year, utc_now.month, utc_now.day)

    current_app.logger.info("Importing promotions...")
    promotions = pixyship.get_current_promotions()
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

            _save_daily_sale(daily_sale)

    current_app.logger.info("Importing daily offers...")
    dailies_offers = pixyship.dailies["offers"]
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

        _save_daily_sale(daily_sale)

    daily_bank_offer = dailies_offers["sale"]["object"]
    if not daily_bank_offer:
        current_app.logger.error("Empty daily_bank_offer")
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

        _save_daily_sale(daily_sale)

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

            _save_daily_sale(daily_sale)

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

        _save_daily_sale(daily_sale)

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

        _save_daily_sale(daily_sale)

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

            _save_daily_sale(daily_sale)


def _save_daily_sale(daily_sale):
    """Save daily sale in database."""

    try:
        insert_command = (
            insert(DailySale.__table__)
            .values(
                type=daily_sale.type,
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
    except Exception as e:
        current_app.logger.exception("Error when saving Daily Sale in database: {}".format(e))
        db.session.rollback()


@importer_cli.command("market", help="Get last market sales and save them in database.")
@click.option("--one-item-only", is_flag=True, help="Import randomly only one item")
@click.option("--item", type=int, default=None, help="Import only the given item")
@with_appcontext
@log_command
def import_market(one_item_only: bool, item: int):
    """Get last market sales and save them in database."""

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no sales to import")
        return

    current_app.logger.info("Importing market sales")

    pixyship = PixyShip()

    # no need to get sales of items not saleable
    items = pixyship.items
    saleable_items = {item_id: item for item_id, item in items.items() if item["saleable"]}

    if item:
        try:
            saleable_items = {item: saleable_items[item]}
        except KeyError:
            current_app.logger.error("Unknown item {}".format(item))
            return

    count = 0
    total = len(saleable_items)
    if one_item_only:
        total = 1

    saleable_items_items = list(saleable_items.items())
    saleable_items_ordered = random.sample(saleable_items_items, k=len(saleable_items_items))

    for item_id, item in saleable_items_ordered:
        count += 1
        current_app.logger.info("[{}/{}] item: {} ({})".format(count, total, item["name"], item_id))

        sales = pixyship.get_sales_from_api(item_id)
        current_app.logger.info("[{}/{}] retrieved: {}".format(count, total, len(sales)))

        for sale in sales:
            listing = Listing(
                id=sale["SaleId"],
                sale_at=sale["StatusDate"],
                item_name=item["name"],
                item_id=item_id,
                amount=sale["Quantity"],
                currency=sale["CurrencyType"],
                price=sale["CurrencyValue"],
                user_id=sale["BuyerShipId"],
                user_name=sale.get("BuyerShipName", ""),
                seller_id=sale["SellerShipId"],
                seller_name=sale.get("SellerShipName", ""),
            )

            db.session.merge(listing)

        current_app.logger.info("[{}/{}] saved: {}".format(count, total, len(sales)))
        db.session.commit()

        if one_item_only:
            break

        api_sleep(3, force_sleep=True)

    current_app.logger.info("Done")


@importer_cli.command("market-messages", help="Get last market messages and save them in database.")
@click.option("--one-item-only", is_flag=True, help="Import randomly only one item")
@click.option("--item", type=int, default=None, help="Import only the given item")
@with_appcontext
@log_command
def import_market_messages(one_item_only: bool, item: int):
    """Get last market messages and save them in database."""

    if current_app.config["USE_STAGING_API"]:
        current_app.logger.info("In staging mode, no market messages to import")
        return

    current_app.logger.info("Importing market messages")

    pixyship = PixyShip()

    # no need to get sales of items not saleable
    items = pixyship.items
    items_with_offstat = {item_id: item for item_id, item in items.items() if item["has_offstat"]}

    if item:
        try:
            items_with_offstat = {item: items_with_offstat[item]}
        except KeyError:
            current_app.logger.error("Unknown item {}".format(item))
            return

    count = 0
    total = len(items_with_offstat)
    if one_item_only:
        total = 1

    items_with_offstat_items = list(items_with_offstat.items())
    items_with_offstat_ordered = random.sample(items_with_offstat_items, k=len(items_with_offstat_items))

    for item_id, item in items_with_offstat_ordered:
        count += 1
        current_app.logger.info("[{}/{}] item: {} ({})".format(count, total, item["name"], item_id))

        messages = pixyship.get_market_messages_from_api(item_id)
        current_app.logger.info("[{}/{}] retrieved: {}".format(count, total, len(messages)))

        for message in messages:
            market_message = MarketMessage(
                id=message["MessageId"],
                message=message["Message"],
                sale_id=message["SaleId"],
                item_id=item_id,
                user_id=message["UserId"],
                message_type=message["MessageType"],
                channel_id=message["ChannelId"],
                activit_type=message["ActivityType"],
                message_date=message["MessageDate"],
            )

            _save_market_message(market_message)

        db.session.commit()

        if one_item_only:
            break

        api_sleep(1, force_sleep=True)

    current_app.logger.info("Done")


def _save_market_message(market_message):
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
    except Exception as e:
        current_app.logger.exception("Error when saving Market Message in database: {}".format(e))
        db.session.rollback()


@importer_cli.command("sprites", help="Download sprites from PSS.")
@with_appcontext
@log_command
def dowload_sprites():
    """Download sprites from PSS."""

    if not os.path.exists(current_app.config["SPRITES_DIRECTORY"]):
        os.mkdir(current_app.config["SPRITES_DIRECTORY"])

    pixyship = PixyShip()
    sprites = pixyship.sprites

    for _, sprite in sprites.items():
        image_number = sprite["image_file"]
        filename = current_app.config["SPRITES_DIRECTORY"] + "/{}.png".format(image_number)

        if not os.path.isfile(filename):
            current_app.logger.info("getting {}".format(filename))
            url = PSS_SPRITES_URL.format(image_number)
            try:
                request.urlretrieve(url, filename)
            except Exception as e:
                current_app.logger.exception("Error when downloading sprite ({}): {}".format(url, e))


def _save_users(users):
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
