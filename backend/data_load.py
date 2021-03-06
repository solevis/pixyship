import argparse
import logging
import os
import sys
from urllib import request
from xml.etree import ElementTree

from contexttimer import Timer

from api_helpers import save_users
from config import CONFIG
from db import db
from models import Listing, Record
from ps_client import PixelStarshipsApi
from run import push_context

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def update_players():
    """Get all top 100 players and top 100 alliances' players and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Updating players')

    pixel_starships_api = PixelStarshipsApi()

    top_users = pixel_starships_api.get_top100_users()
    save_users(top_users)

    count = 0
    top_alliances = pixel_starships_api.get_top100_alliances()
    for alliance_id, alliance in list(top_alliances.items()):
        try:
            count += 1
            logger.info('[{}/100] {}...'.format(count, alliance['name']))
            top_users = pixel_starships_api.get_alliance_users(alliance_id)
            save_users(top_users)
        except Exception as e:
            logger.error(e)

    logger.info('Done')


def update_data():
    """Get all items, crews, rooms, ships and save them in database."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Updating data')

    pixel_starships_api = PixelStarshipsApi()

    pixel_starships_api.update_item_data()
    pixel_starships_api.update_char_data()
    pixel_starships_api.update_room_data()
    pixel_starships_api.update_ship_data()
    pixel_starships_api.update_collection_data()
    pixel_starships_api.update_data(pixel_starships_api.uri_research, 'ResearchDesignId', 'research')

    logger.info('Done')


def update_market():
    """Get last market sales for all items."""

    # avoid Flask RuntimeError: No application found
    push_context()

    logger.info('Updating market prices')

    # get items from database
    records = Record.query.filter_by(type='item', current=True).all()

    pixel_starships_api = PixelStarshipsApi()

    for record in records:
        item = ElementTree.fromstring(record.data).attrib

        # if item not saleable, no need to get sales
        saleable = (int(item['Flags']) & 1) != 0
        if not saleable:
            continue

        logger.info('{}...'.format(item['ItemDesignName']))

        market_data = pixel_starships_api.get_market_data(item)
        for k, v in market_data.items():
            listing = Listing(
                id=k,
                sale_at=v['sale_at'],
                item_name=v['item_name'],
                item_id=v['item_id'],
                amount=v['amount'],
                currency=v['currency'],
                price=v['price'],
                user_id=v['user_id']
            )

            db.session.merge(listing)

        logger.info('{} listings updated'.format(len(market_data)))
        db.session.commit()

    logger.info('Done')


def update_sprites():
    """Download sprites from PSS."""

    if not os.path.exists(CONFIG['SPRITES_DIRECTORY']):
        os.mkdir(CONFIG['SPRITES_DIRECTORY'])

    pixel_starships_api = PixelStarshipsApi()
    sprites = pixel_starships_api.sprite_map

    for _, sprite in sprites.items():
        image_number = sprite['image_file']
        filename = CONFIG['SPRITES_DIRECTORY'] + '/{}.png'.format(image_number)

        if not os.path.isfile(filename):
            logger.info('getting {}'.format(filename))
            url = pixel_starships_api.ps_asset_url.format(image_number)
            try:
                request.urlretrieve(url, filename)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", action="store_true")
    parser.add_argument("--players", action="store_true")
    parser.add_argument("--market", action="store_true")
    parser.add_argument("--sprites", action="store_true")
    args = parser.parse_args()

    if args.data:
        with Timer() as t:
            logger.info('START')
            update_data()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.players:
        with Timer() as t:
            logger.info('START')
            update_players()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.market:
        with Timer() as t:
            logger.info('START')
            update_market()
            logger.info('END :: {}s'.format(t.elapsed))

    if args.sprites:
        with Timer() as t:
            logger.info('START')
            update_sprites()
            logger.info('END :: {}s'.format(t.elapsed))
