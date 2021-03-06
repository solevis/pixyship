from api_helpers import search_player
from ps_client import PixelStarshipsApi
from run import push_context


def test_crews():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    crews = pixel_starships_api._load_char_map()

    assert len(crews) > 0
    assert crews[392]['id'] == 392
    assert crews[392]['name'] == 'Polaran Pilgrim'


def test_items():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    items = pixel_starships_api._load_item_map()

    assert len(items) > 0
    assert items[600]['id'] == 600
    assert items[600]['name'] == 'Federation Officer Armor'


def test_rooms():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    rooms, _ = pixel_starships_api._load_room_map()

    assert len(rooms) > 0
    assert rooms[10]['id'] == 10
    assert rooms[10]['name'] == 'Bedroom Lv2'
    assert rooms[10]['level'] == 2


def test_upgrades():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    _, upgrades = pixel_starships_api._load_room_map()

    assert len(upgrades) > 0
    assert upgrades[10] == 20


def test_ships():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    ships = pixel_starships_api._load_ship_map()

    assert len(ships) > 0
    assert ships[129]['id'] == 129
    assert ships[129]['name'] == 'Oumaumau Invader'
    assert ships[129]['level'] == 11


def test_collections():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    collections = pixel_starships_api._load_collection_map()

    assert len(collections) > 0
    assert collections[7]['CollectionDesignId'] == '7'
    assert collections[7]['CollectionName'] == 'Federation'


def test_researches():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    researches = pixel_starships_api._load_research_map()

    assert len(researches) > 0
    assert researches[42]['ResearchDesignId'] == '42'
    assert researches[42]['ResearchName'] == 'Advanced Training Lv5'


def test_prices():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    prices = pixel_starships_api._load_prices()

    assert len(prices) > 0


def test_sprites():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    sprites = pixel_starships_api._load_sprite_map()

    assert len(sprites) > 0


def test_search_player():
    # avoid Flask RuntimeError: No application found
    push_context()

    players = search_player('Solevis')

    assert len(players) == 2
    assert players[0]['name'] == 'Solevis'
    assert players[1]['name'] == 'MiniSolevis'


def test_changes():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    changes = pixel_starships_api.get_changes()

    assert len(changes) > 0


def test_user_id():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    user_id = pixel_starships_api.get_user_id('Solevis')

    assert user_id == 6635604
