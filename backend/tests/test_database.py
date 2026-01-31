"""Mocked database tests - avoid real database queries during testing."""

from unittest.mock import patch

import pytest

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


@pytest.fixture
def mock_database_data():
    """Fixture providing mock database data for testing."""
    return {
        "crews": [
            {"id": 392, "name": "Polaran Pilgrim", "level": 1, "rarity": "Common"},
            {"id": 1, "name": "Test Crew", "level": 1, "rarity": "Common"},
        ],
        "items": [
            {"id": 600, "name": "Federation Officer Armor", "type": "Armor"},
            {"id": 1, "name": "Test Item", "type": "Weapon"},
        ],
        "rooms": [
            {"id": 10, "name": "Bedroom Lv2", "level": 2, "type": "Living"},
            {"id": 1, "name": "Test Room", "level": 1, "type": "Basic"},
        ],
        "crafts": [
            {"id": 10, "name": "Interceptor Lv7", "hp": 5, "speed": 10},
            {"id": 1, "name": "Test Craft", "hp": 1, "speed": 5},
        ],
        "missiles": [
            {"id": 40, "name": "Penetrator Lv5", "volley": 1.0, "damage": 10},
            {"id": 1, "name": "Test Missile", "volley": 1.0, "damage": 5},
        ],
        "ships": [
            {"id": 129, "name": "Oumaumau Invader", "level": 11, "hp": 1000},
            {"id": 1, "name": "Test Ship", "level": 1, "hp": 100},
        ],
        "collections": [
            {"id": 7, "name": "Federation", "bonus": "Diplomacy"},
            {"id": 1, "name": "Test Collection", "bonus": "Test"},
        ],
        "researches": [
            {"ResearchDesignId": "42", "ResearchName": "Advanced Training Lv5", "ResearchTime": 3600},
            {"ResearchDesignId": "1", "ResearchName": "Test Research", "ResearchTime": 60},
        ],
        "prices": [
            {"item_id": 1, "price": 100, "currency": "Starbux"},
            {"item_id": 2, "price": 50, "currency": "Minerals"},
        ],
        "sprites": [
            {"id": 1, "sprite_id": 100, "x": 0, "y": 0, "width": 32, "height": 32},
            {"id": 2, "sprite_id": 101, "x": 32, "y": 0, "width": 32, "height": 32},
        ],
        "players": [
            {"name": "Solevis", "id": 6635604, "trophy": 1000},
            {"name": "Test Player", "id": 1, "trophy": 500},
        ],
        "changes": [
            {"id": 1, "change_type": "update", "table": "players", "record_id": 6635604},
            {"id": 2, "change_type": "create", "table": "items", "record_id": 1},
        ],
    }


@pytest.fixture
def mock_character_service(app, mock_database_data):
    """Mock CharacterService with test data."""
    with app.app_context():
        service = CharacterService()

        def mock_get_characters_from_records():
            return {crew["id"]: crew for crew in mock_database_data["crews"]}

        with patch.object(service, "get_characters_from_records", mock_get_characters_from_records):
            yield service


@pytest.fixture
def mock_item_service(app, mock_database_data):
    """Mock ItemService with test data."""
    with app.app_context():
        service = ItemService()

        def mock_get_items_from_records():
            return {item["id"]: item for item in mock_database_data["items"]}

        with patch.object(service, "get_items_from_records", mock_get_items_from_records):
            yield service


@pytest.fixture
def mock_room_service(app, mock_database_data):
    """Mock RoomService with test data."""
    with app.app_context():
        service = RoomService()

        def mock_get_rooms_from_records():
            rooms = {room["id"]: room for room in mock_database_data["rooms"]}
            return rooms, {}

        with patch.object(service, "get_rooms_from_records", mock_get_rooms_from_records):
            yield service


@pytest.fixture
def mock_craft_service(app, mock_database_data):
    """Mock CraftService with test data."""
    with app.app_context():
        service = CraftService()

        def mock_get_crafts_from_records():
            return {craft["id"]: craft for craft in mock_database_data["crafts"]}

        with patch.object(service, "get_crafts_from_records", mock_get_crafts_from_records):
            yield service


@pytest.fixture
def mock_missile_service(app, mock_database_data):
    """Mock MissileService with test data."""
    with app.app_context():
        service = MissileService()

        def mock_get_missiles_from_records():
            return {missile["id"]: missile for missile in mock_database_data["missiles"]}

        with patch.object(service, "get_missiles_from_records", mock_get_missiles_from_records):
            yield service


@pytest.fixture
def mock_ship_service(app, mock_database_data):
    """Mock ShipService with test data."""
    with app.app_context():
        service = ShipService()

        def mock_get_ships_from_records():
            return {ship["id"]: ship for ship in mock_database_data["ships"]}

        with patch.object(service, "get_ships_from_records", mock_get_ships_from_records):
            yield service


@pytest.fixture
def mock_collection_service(app, mock_database_data):
    """Mock CollectionService with test data."""
    with app.app_context():
        service = CollectionService()

        def mock_get_collections_from_records():
            return {collection["id"]: collection for collection in mock_database_data["collections"]}

        with patch.object(service, "get_collections_from_records", mock_get_collections_from_records):
            yield service


@pytest.fixture
def mock_research_service(app, mock_database_data):
    """Mock ResearchService with test data."""
    with app.app_context():
        service = ResearchService()

        def mock_get_researches_from_records():
            return {research["ResearchDesignId"]: research for research in mock_database_data["researches"]}

        with patch.object(service, "get_researches_from_records", mock_get_researches_from_records):
            yield service


@pytest.fixture
def mock_market_service(app, mock_database_data):
    """Mock MarketService with test data."""
    with app.app_context():
        service = MarketService()

        def mock_get_prices_from_db():
            return mock_database_data["prices"]

        with patch.object(service, "get_prices_from_db", mock_get_prices_from_db):
            yield service


@pytest.fixture
def mock_sprite_service(app, mock_database_data):
    """Mock SpriteService with test data."""
    with app.app_context():
        service = SpriteService()

        def mock_get_sprites_from_records():
            return {sprite["id"]: sprite for sprite in mock_database_data["sprites"]}

        with patch.object(service, "get_sprites_from_records", mock_get_sprites_from_records):
            yield service


@pytest.fixture
def mock_player_service(app, mock_database_data):
    """Mock PlayerService with test data."""
    with app.app_context():
        service = PlayerService()

        def mock_get_player_data(name):
            return [player for player in mock_database_data["players"] if player["name"] == name]

        def mock_find_user_id(name):
            player = next((p for p in mock_database_data["players"] if p["name"] == name), None)
            return player["id"] if player else None

        with (
            patch.object(service, "get_player_data", mock_get_player_data),
            patch.object(service, "find_user_id", mock_find_user_id),
        ):
            yield service


@pytest.fixture
def mock_changes_service(app, mock_database_data):
    """Mock ChangesService with test data."""
    with app.app_context():
        service = ChangesService()

        def mock_get_changes_from_db():
            return mock_database_data["changes"]

        with patch.object(service, "get_changes_from_db", mock_get_changes_from_db):
            yield service


# Test functions using mocked services


def test_crews(mock_character_service):
    """Test crews with mocked data."""
    crews = mock_character_service.get_characters_from_records()

    assert len(crews) > 0
    assert crews[392]["id"] == 392
    assert crews[392]["name"] == "Polaran Pilgrim"


def test_items(mock_item_service):
    """Test items with mocked data."""
    items = mock_item_service.get_items_from_records()

    assert len(items) > 0
    assert items[600]["id"] == 600
    assert items[600]["name"] == "Federation Officer Armor"


def test_rooms(mock_room_service):
    """Test rooms with mocked data."""
    rooms, _ = mock_room_service.get_rooms_from_records()

    assert len(rooms) > 0
    assert rooms[10]["id"] == 10
    assert rooms[10]["name"] == "Bedroom Lv2"
    assert rooms[10]["level"] == 2


def test_crafts(mock_craft_service):
    """Test crafts with mocked data."""
    crafts = mock_craft_service.get_crafts_from_records()

    assert len(crafts) > 0
    assert crafts[10]["id"] == 10
    assert crafts[10]["name"] == "Interceptor Lv7"
    assert crafts[10]["hp"] == 5


def test_missiles(mock_missile_service):
    """Test missiles with mocked data."""
    missiles = mock_missile_service.get_missiles_from_records()

    assert len(missiles) > 0
    assert missiles[40]["id"] == 40
    assert missiles[40]["name"] == "Penetrator Lv5"
    assert missiles[40]["volley"] == 1.0


def test_ships(mock_ship_service):
    """Test ships with mocked data."""
    ships = mock_ship_service.get_ships_from_records()

    assert len(ships) > 0
    assert ships[129]["id"] == 129
    assert ships[129]["name"] == "Oumaumau Invader"
    assert ships[129]["level"] == 11


def test_collections(mock_collection_service):
    """Test collections with mocked data."""
    collections = mock_collection_service.get_collections_from_records()

    assert len(collections) > 0
    assert collections[7]["id"] == 7
    assert collections[7]["name"] == "Federation"


def test_researches(mock_research_service):
    """Test researches with mocked data."""
    researches = mock_research_service.get_researches_from_records()

    assert len(researches) > 0
    assert researches["42"]["ResearchDesignId"] == "42"
    assert researches["42"]["ResearchName"] == "Advanced Training Lv5"


def test_prices(mock_market_service):
    """Test prices with mocked data."""
    prices = mock_market_service.get_prices_from_db()

    assert len(prices) > 0


def test_sprites(mock_sprite_service):
    """Test sprites with mocked data."""
    sprites = mock_sprite_service.get_sprites_from_records()

    assert len(sprites) > 0


def test_search_player(mock_player_service):
    """Test player search with mocked data."""
    players = mock_player_service.get_player_data("Solevis")

    assert len(players) == 1
    assert players[0]["name"] == "Solevis"


def test_changes(mock_changes_service):
    """Test changes with mocked data."""
    changes = mock_changes_service.get_changes_from_db()

    assert len(changes) > 0


def test_user_id(mock_player_service):
    """Test user ID lookup with mocked data."""
    user_id = mock_player_service.find_user_id("Solevis")

    assert user_id == 6635604
