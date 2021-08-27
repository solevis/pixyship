import argparse
import logging
import os
import sys
import time
from urllib import request

from contexttimer import Timer

from config import CONFIG
from db import db
from models import Listing, Alliance, Player
from pixyship import Pixyship
from run import push_context

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def import_players():
    """Get all top 100 players and top 100 alliances' players and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Importing players')

    pixyship = Pixyship()

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
    except Exception:
        db.session.rollback()

    # save new data
    __save_users(top_users)

    logger.info('Done')


def import_assets():
    """Get all items, crews, rooms, ships and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Importing assets')

    pixyship = Pixyship()

    pixyship.update_items()
    pixyship.update_characters()
    pixyship.update_rooms()
    pixyship.update_ships()
    pixyship.update_collections()
    pixyship.update_researches()

    logger.info('Done')


def import_market(first_item_only=False, item=None):
    """Get last market sales for all items."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Importing market prices')

    pixyship = Pixyship()

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

    if not os.path.exists(CONFIG['SPRITES_DIRECTORY']):
        os.mkdir(CONFIG['SPRITES_DIRECTORY'])

    pixyship = Pixyship()
    sprites = pixyship.sprites

    for _, sprite in sprites.items():
        image_number = sprite['image_file']
        filename = CONFIG['SPRITES_DIRECTORY'] + '/{}.png'.format(image_number)

        if not os.path.isfile(filename):
            logger.info('getting {}'.format(filename))
            url = pixyship.PSS_SPRITES_URL.format(image_number)
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
