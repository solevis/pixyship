from app.services.changes import ChangesService
from app.services.character import CharacterService
from app.services.collection import CollectionService
from app.services.craft import CraftService
from app.services.item import ItemService
from app.services.market import MarketService
from app.services.missile import MissileService
from app.services.player import PlayerService
from app.services.research import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.sprite import SpriteService


def test_crews(app):
    with app.app_context():
        character_service = CharacterService()
        crews = character_service.get_characters_from_records()

        assert len(crews) > 0
        assert crews[392]["id"] == 392
        assert crews[392]["name"] == "Polaran Pilgrim"


def test_items(app):
    with app.app_context():
        item_service = ItemService()
        items = item_service.get_items_from_records()

        assert len(items) > 0
        assert items[600]["id"] == 600
    assert items[600]["name"] == "Federation Officer Armor"


def test_rooms(app):
    with app.app_context():
        room_service = RoomService()
        (
            rooms,
            _,
        ) = room_service.get_rooms_from_records()

        assert len(rooms) > 0
        assert rooms[10]["id"] == 10
        assert rooms[10]["name"] == "Bedroom Lv2"
        assert rooms[10]["level"] == 2


def test_crafts(app):
    with app.app_context():
        craft_service = CraftService()
        crafts = craft_service.get_crafts_from_records()

        assert len(crafts) > 0
        assert crafts[10]["id"] == 10
        assert crafts[10]["name"] == "Interceptor Lv7"
        assert crafts[10]["hp"] == 5


def test_missiles(app):
    with app.app_context():
        missile_service = MissileService()
        missiles = missile_service.get_missiles_from_records()

        assert len(missiles) > 0
        assert missiles[40]["id"] == 40
        assert missiles[40]["name"] == "Penetrator Lv5"
        assert missiles[40]["volley"] == 1.0


def test_ships(app):
    with app.app_context():
        ship_service = ShipService()
        ships = ship_service.get_ships_from_records()

        assert len(ships) > 0
        assert ships[129]["id"] == 129
        assert ships[129]["name"] == "Oumaumau Invader"
        assert ships[129]["level"] == 11


def test_collections(app):
    with app.app_context():
        collection_service = CollectionService()
        collections = collection_service.get_collections_from_records()

        assert len(collections) > 0
        assert collections[7]["id"] == 7
        assert collections[7]["name"] == "Federation"


def test_researches(app):
    with app.app_context():
        research_service = ResearchService()
        researches = research_service.get_researches_from_records()

        assert len(researches) > 0
        assert researches[42]["ResearchDesignId"] == "42"
        assert researches[42]["ResearchName"] == "Advanced Training Lv5"


def test_prices(app):
    with app.app_context():
        market_service = MarketService()
        prices = market_service.get_prices_from_db()

        assert len(prices) > 0


def test_sprites(app):
    with app.app_context():
        sprite_service = SpriteService()
        sprites = sprite_service.get_sprites_from_records()

        assert len(sprites) > 0


def test_search_player(app):
    with app.app_context():
        player_service = PlayerService()
        players = player_service.get_player_data("Solevis")

        assert len(players) == 1
        assert players[0]["name"] == "Solevis"


def test_changes(app):
    with app.app_context():
        changes_service = ChangesService()
        changes = changes_service.get_changes_from_db()

        assert len(changes) > 0


def test_user_id(app):
    with app.app_context():
        player_service = PlayerService()
        user_id = player_service.find_user_id("Solevis")

        assert user_id == 6635604
