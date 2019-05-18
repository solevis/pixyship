import logging

from contexttimer import Timer

from api_helpers import process_users
from models import Listing, db
from ps_client import PixelStarshipsApi
from run import push_context

log = logging.getLogger(__name__)


def load_players():
    push_context()
    psa = PixelStarshipsApi()
    alliances = psa.get_alliances()

    users = psa.get_top_users()
    process_users(users)

    count = 0
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

    psa = PixelStarshipsApi()
    market_data = psa.get_market_data()
    for k, v in market_data.items():
        listing = Listing(
            id=k,
            sale_at=v['sale_at'],
            item_name=v['item_name'],
            item_id=v['item_id'],
            amount=v['amount'],
            currency=v['currency'],
            price=v['price'],
            user_id=v['user_id'],
            modification=v['modification']
        )
        db.session.merge(listing)

    log.info('{} listings updated'.format(len(market_data)))
    db.session.commit()


if __name__ == '__main__':
    with Timer() as t:
        print('START')
        load_players()
        # summarize_names()
        print('END', t.elapsed)
