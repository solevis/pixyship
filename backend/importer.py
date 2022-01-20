import argparse
import datetime
import logging
import os
import sys
import time
from urllib import request

from contexttimer import Timer

from config import CONFIG
from constants import PSS_SPRITES_URL
from db import db
from models import Listing, Alliance, Player, DailySale
from pixyship import PixyShip
from run import push_context

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def import_players():
    """Get all top 100 players and top 100 alliances' players and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Importing players')

    pixyship = PixyShip()

    logger.info('## top 100 players')
    top_users = list(pixyship.get_top100_users_from_api().items())
    time.sleep(5)

    logger.info('## top 100 alliances')
    count = 0
    top_alliances = pixyship.get_top100_alliances_from_api()
    for alliance_id, alliance in list(top_alliances.items()):
        try:
            count += 1
            logger.info('[{}/100] {}...'.format(count, alliance['name']))
            top_users += list(pixyship.get_alliance_users_from_api(alliance_id).items())
            time.sleep(5)
        except Exception as e:
            logger.error(e)

    try:
        # purge old data
        db.session.query(Player).delete()
        db.session.query(Alliance).delete()
        db.session.commit()
    except Exception as e:
        logger.error(e)
        db.session.rollback()

    # save new data
    __save_users(top_users)

    logger.info('Done')


def import_assets():
    """Get all items, crews, rooms, ships and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = PixyShip()

    logger.info('Importing items...')
    pixyship.update_items()

    logger.info('Importing characters...')
    pixyship.update_characters()

    logger.info('Importing rooms...')
    pixyship.update_rooms()

    logger.info('Importing ships...')
    pixyship.update_ships()

    logger.info('Importing collections...')
    pixyship.update_collections()

    logger.info('Importing researches...')
    pixyship.update_researches()

    logger.info('Importing sprites...')
    pixyship.update_sprites()

    logger.info('Importing rooms sprites')
    pixyship.update_room_sprites()

    logger.info('Importing trainings...')
    pixyship.update_trainings()

    logger.info('Importing achievements...')
    pixyship.update_achievements()

    logger.info('Done')


def import_daily_sales():
    """Get all items, crews, rooms, ships on sale today and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = PixyShip()

    utc_now = datetime.datetime.utcnow()
    today = datetime.date(utc_now.year, utc_now.month, utc_now.day)

    logger.info('Importing promotions...')
    promotions = pixyship.get_current_promotions()
    for promotion in promotions:
        for reward in promotion['rewards']:
            if reward['type'] in ['starbux', 'purchasePoints']:
                continue

            daily_sale = DailySale(
                type=reward['type'],
                type_id=reward['id'],
                sale_at=promotion['from'],
                sale_from='promotion_{}'.format(promotion['type'].lower()),
                currency=None,
                price=None,
            )

            _save_daily_sale(daily_sale)

    logger.info('Importing daily shop...')
    dailies_offers = pixyship.dailies['offers']
    if not dailies_offers:
        logger.error('Empty dailies_offers')
        return

    daily_shop_offer = dailies_offers['shop']['object']
    if not daily_shop_offer:
        logger.error('Empty daily_shop_offer')
        return

    daily_sale = DailySale(
        type=daily_shop_offer['type'],
        type_id=daily_shop_offer['id'],
        sale_at=today,
        sale_from='shop',
        currency=dailies_offers['shop']['cost']['currency'].lower(),
        price=dailies_offers['shop']['cost']['price'],
    )

    _save_daily_sale(daily_sale)

    daily_bank_offer = dailies_offers['sale']['object']
    if not daily_bank_offer:
        logger.error('Empty daily_bank_offer')
        return

    daily_sale = DailySale(
        type=daily_bank_offer['type'],
        type_id=daily_bank_offer['id'],
        sale_at=today,
        sale_from='sale',
        currency=None,
        price=None,
    )

    _save_daily_sale(daily_sale)

    daily_rewards_offers = dailies_offers['dailyRewards']['objects']
    if not daily_rewards_offers:
        logger.error('Empty daily_rewards_offers')
        return

    for daily_rewards_offer in daily_rewards_offers:
        if daily_rewards_offer['type'] in ['currency', 'starbux', 'purchasePoints']:
            continue

        daily_sale = DailySale(
            type=daily_rewards_offer['type'],
            type_id=daily_rewards_offer['id'],
            sale_at=today,
            sale_from='daily_rewards',
            currency=None,
            price=None,
        )

        _save_daily_sale(daily_sale)

    daily_bluecargo_mineral_offer = dailies_offers['blueCargo']['mineralCrew']
    if not daily_bluecargo_mineral_offer:
        logger.error('Empty daily_bluecargo_mineral_offer')
        return

    daily_sale = DailySale(
        type=daily_bluecargo_mineral_offer['type'],
        type_id=daily_bluecargo_mineral_offer['id'],
        sale_at=today,
        sale_from='blue_cargo_mineral',
        currency='mineral',
        price=None,
    )

    _save_daily_sale(daily_sale)

    daily_bluecargo_starbux_offer = dailies_offers['blueCargo']['starbuxCrew']
    if not daily_bluecargo_starbux_offer:
        logger.error('Empty daily_bluecargo_starbux_offer')
        return

    daily_sale = DailySale(
        type=daily_bluecargo_starbux_offer['type'],
        type_id=daily_bluecargo_starbux_offer['id'],
        sale_at=today,
        sale_from='blue_cargo_starbux',
        currency='starbux',
        price=None,
    )

    _save_daily_sale(daily_sale)

    daily_greencargo_offers = dailies_offers['greenCargo']['items']
    if not daily_greencargo_offers:
        logger.error('Empty daily_greencargo_offers')
        return

    for daily_greencargo_offer in daily_greencargo_offers:
        if daily_greencargo_offer['object']['type'] in ['starbux', 'purchasePoints']:
            continue

        daily_sale = DailySale(
            type=daily_greencargo_offer['object']['type'],
            type_id=daily_greencargo_offer['object']['id'],
            sale_at=today,
            sale_from='green_cargo',
            currency=daily_greencargo_offer['cost']['currency'],
            price=daily_greencargo_offer['cost']['price'],
        )

        _save_daily_sale(daily_sale)


def _save_daily_sale(daily_sale):
    try:
        db.session.add(daily_sale)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        db.session.rollback()


def import_market(first_item_only=False, item=None):
    """Get last market sales for all items."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Importing market prices')

    pixyship = PixyShip()

    # no need to get sales of items not saleable
    items = pixyship.items
    saleable_items = {item_id: item for item_id, item in items.items() if item['saleable']}

    if item:
        try:
            saleable_items = {
                item: saleable_items[item]
            }
        except KeyError:
            logger.error("Unknown item {}".format(item))
            return

    count = 0
    total = len(saleable_items)
    if first_item_only:
        total = 1

    for item_id, item in saleable_items.items():
        count += 1
        logger.info('[{}/{}] {}...'.format(count, total, item['name']))

        sales = pixyship.get_sales_from_api(item_id)

        for sale in sales:
            listing = Listing(
                id=sale['SaleId'],
                sale_at=sale['StatusDate'],
                item_name=item['name'],
                item_id=item_id,
                amount=sale['Quantity'],
                currency=sale['CurrencyType'],
                price=sale['CurrencyValue'],
                user_id=sale['BuyerShipId'],
                user_name=sale['BuyerShipName'],
                seller_id=sale['SellerShipId'],
                seller_name=sale['SellerShipName']
            )

            db.session.merge(listing)

        logger.info('\t{} sales updated'.format(len(sales)))
        db.session.commit()

        if first_item_only:
            break

        time.sleep(3)

    logger.info('Done')


def dowload_sprites():
    """Download sprites from PSS."""

    # avoid Flask RuntimeError: No application found
    push_context()

    if not os.path.exists(CONFIG['SPRITES_DIRECTORY']):
        os.mkdir(CONFIG['SPRITES_DIRECTORY'])

    pixyship = PixyShip()
    sprites = pixyship.sprites

    for _, sprite in sprites.items():
        image_number = sprite['image_file']
        filename = CONFIG['SPRITES_DIRECTORY'] + '/{}.png'.format(image_number)

        if not os.path.isfile(filename):
            logger.info('getting {}'.format(filename))
            url = PSS_SPRITES_URL.format(image_number)
            try:
                request.urlretrieve(url, filename)
            except Exception as e:
                logger.error(e)


def __save_users(users):
    """Save users and attached alliance in database."""

    for user_id, user in users:
        player = Player(
            id=user_id,
            name=user['name'],
            trophies=int(user['trophies']),
            alliance_id=user['alliance_id'],
            last_login_at=user['last_login_at']
        )
        db.session.merge(player)

        if user['alliance_name']:
            alliance = Alliance(
                id=user['alliance_id'],
                name=user['alliance_name'],
                sprite_id=user['alliance_sprite_id'],
            )
            db.session.merge(alliance)

        db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets", action="store_true")
    parser.add_argument("--players", action="store_true")
    parser.add_argument("--market", action="store_true")
    parser.add_argument("--market-first-item", action="store_true")
    parser.add_argument("--market-one-item", type=int)
    parser.add_argument("--sprites", action="store_true")
    parser.add_argument("--daily-sales", action="store_true")
    args = parser.parse_args()

    if args.assets:
        with Timer() as t:
            logger.info('START')
            import_assets()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.players:
        with Timer() as t:
            logger.info('START')
            import_players()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.market:
        with Timer() as t:
            logger.info('START')
            import_market()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.market_first_item:
        with Timer() as t:
            logger.info('START')
            import_market(first_item_only=True)
            logger.info('END :: {}s'.format(t.elapsed))

    if args.market_one_item:
        with Timer() as t:
            logger.info('START')
            import_market(item=args.market_one_item)
            logger.info('END :: {}s'.format(t.elapsed))

    if args.sprites:
        with Timer() as t:
            logger.info('START')
            dowload_sprites()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.daily_sales:
        with Timer() as t:
            logger.info('START')
            import_daily_sales()
            logger.info('END :: {}s'.format(t.elapsed))
