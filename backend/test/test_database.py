from pixyship import Pixyship
from run import push_context


def test_crews():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    crews = pixyship._get_characters_from_db()

    assert len(crews) > 0
    assert crews[392]['id'] == 392
    assert crews[392]['name'] == 'Polaran Pilgrim'


def test_items():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    items = pixyship._get_items_from_db()

    assert len(items) > 0
    assert items[600]['id'] == 600
    assert items[600]['name'] == 'Federation Officer Armor'


def test_rooms():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    rooms, _ = pixyship._get_rooms_from_db()

    assert len(rooms) > 0
    assert rooms[10]['id'] == 10
    assert rooms[10]['name'] == 'Bedroom Lv2'
    assert rooms[10]['level'] == 2


def test_upgrades():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    _, upgrades = pixyship._get_rooms_from_db()

    assert len(upgrades) > 0
    assert upgrades[10] == 20


def test_ships():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    ships = pixyship._get_ships_from_db()

    assert len(ships) > 0
    assert ships[129]['id'] == 129
    assert ships[129]['name'] == 'Oumaumau Invader'
    assert ships[129]['level'] == 11


def test_collections():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    collections = pixyship._get_collections_from_db()

    assert len(collections) > 0
    assert collections[7]['CollectionDesignId'] == '7'
    assert collections[7]['CollectionName'] == 'Federation'


def test_researches():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    researches = pixyship._get_researches_from_db()

    assert len(researches) > 0
    assert researches[42]['ResearchDesignId'] == '42'
    assert researches[42]['ResearchName'] == 'Advanced Training Lv5'


def test_prices():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    prices = pixyship._get_prices_from_db()

    assert len(prices) > 0


def test_sprites():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    sprites = pixyship._get_sprites_from_api()

    assert len(sprites) > 0


def test_search_player():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    players = pixyship.get_player_data('Solevis')

    assert len(players) == 2
    assert players[0]['name'] == 'Solevis'
    assert players[1]['name'] == 'MiniSolevis'


def test_changes():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    changes = pixyship.get_changes_from_db()

    assert len(changes) > 0


def test_user_id():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixyship = Pixyship()
    user_id = pixyship.find_user_id('Solevis')

    assert user_id == 6635604
