import logging
import argparse
from xml.etree import ElementTree

from contexttimer import Timer

from api_helpers import process_users
from models import Listing, db, Record
from ps_client import PixelStarshipsApi
from run import push_context

log = logging.getLogger(__name__)


def load_players():
    push_context()
    psa = PixelStarshipsApi()

    users = psa.get_top_users()
    process_users(users)

    count = 0
    alliances = psa.get_alliances()
    for alliance_id, alliance in list(alliances.items()):
        try:
            count += 1
            print(count, '------', alliance['name'])
            users = psa.get_alliance_users(alliance_id)
            process_users(users)
        except Exception as e:
            print('*** PROBLEM LOADING ***', e)
            pass


def update_data():
    push_context()
    psa = PixelStarshipsApi()
    psa.update_item_data()
    psa.update_char_data()
    psa.update_room_data()
    psa.update_ship_data()
    psa.update_collection_data()
    psa.update_data(psa.uri_research, 'ResearchDesignId', 'research')


def check_market():
    push_context()
    log.info('Checking market prices')

    # get items from database
    records = Record.query.filter_by(type='item', current=True).all()

    psa = PixelStarshipsApi()

    for record in records:
        item = ElementTree.fromstring(record.data).attrib

        # if item not saleable, no need to get sales
        saleable = (int(item['Flags']) & 1) != 0
        if not saleable:
            continue

        log.info('{}...'.format(item['ItemDesignName']))

        market_data = psa.get_market_data(item)
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

        log.info('{} listings updated'.format(len(market_data)))
        db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", action="store_true")
    parser.add_argument("--players", action="store_true")
    parser.add_argument("--market", action="store_true")
    args = parser.parse_args()

    if args.data:
        with Timer() as t:
            print('START')
            update_data()
            print('END', t.elapsed)

    if args.players:
        with Timer() as t:
            print('START')
            load_players()
            # summarize_names()
            print('END', t.elapsed)

    if args.market:
        with Timer() as t:
            print('START')
            check_market()
            print('END', t.elapsed)
