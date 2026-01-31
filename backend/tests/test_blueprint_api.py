"""Mocked blueprint API tests - avoid real API calls and database queries."""

from unittest.mock import patch

import pytest
from flask import url_for


@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses for blueprint testing."""
    return {
        "players": [
            {"name": "Solevis", "id": 6635604, "trophy": 1000, "ship": "Test Ship"},
            {"name": "Test Player", "id": 1, "trophy": 500, "ship": "Basic Ship"},
        ],
        "player_ship": {
            "player": {"name": "Solevis", "id": 6635604, "trophy": 1000},
            "ship": {"name": "Test Ship", "level": 10, "hp": 1000},
            "rooms": [{"name": "Bridge", "level": 5}, {"name": "Engine", "level": 3}],
        },
        "daily": {
            "shop": {"currency": "Starbux", "amount": 100, "items": ["Item1", "Item2"]},
            "cargo": {"common": "Crew1", "hero": "Crew2"},
            "rewards": [{"type": "Starbux", "amount": 50}],
        },
        "changes": {
            "changes": [
                {"id": 1, "type": "update", "table": "players", "record_id": 6635604},
                {"id": 2, "type": "create", "table": "items", "record_id": 1},
            ],
            "last_prestiges": [
                {"character1": 196, "character2": 338, "date": "2023-01-01"},
            ],
        },
        "collections": [
            {"id": 1, "name": "Federation", "bonus": "Diplomacy", "characters": [1, 2, 3]},
            {"id": 2, "name": "Polaran", "bonus": "Science", "characters": [4, 5, 6]},
        ],
        "achievements": [
            {"id": 1, "name": "First Victory", "description": "Win your first battle"},
            {"id": 2, "name": "Master Trader", "description": "Complete 100 trades"},
        ],
        "research": [
            {"id": 1, "name": "Advanced Training", "time": 3600, "cost": 100},
            {"id": 2, "name": "Shield Upgrade", "time": 7200, "cost": 200},
        ],
        "prestige": [
            {"character1": 196, "character2": 338, "requirements": "Level 10"},
            {"character1": 338, "character2": 196, "requirements": "Level 15"},
        ],
        "crafts": [
            {"id": 1, "name": "Interceptor", "hp": 100, "speed": 15},
            {"id": 2, "name": "Bomber", "hp": 150, "speed": 10},
        ],
        "missiles": [
            {"id": 1, "name": "Basic Missile", "damage": 10, "volley": 1},
            {"id": 2, "name": "Advanced Missile", "damage": 25, "volley": 2},
        ],
        "ships": [
            {"id": 1, "name": "Basic Ship", "level": 1, "hp": 100},
            {"id": 2, "name": "Advanced Ship", "level": 10, "hp": 1000},
        ],
        "items": [
            {"id": 1, "name": "Basic Item", "type": "Weapon", "price": 100},
            {"id": 2, "name": "Advanced Item", "type": "Armor", "price": 500},
        ],
        "rooms": [
            {"id": 1, "name": "Bridge", "level": 1, "type": "Command"},
            {"id": 2, "name": "Engine", "level": 1, "type": "Engineering"},
        ],
        "skins": [
            {"id": 1, "name": "Basic Skin", "type": "Ship", "rarity": "Common"},
            {"id": 2, "name": "Advanced Skin", "type": "Ship", "rarity": "Rare"},
        ],
        "sprites": [
            {"id": 1, "sprite_id": 100, "x": 0, "y": 0, "width": 32, "height": 32},
            {"id": 2, "sprite_id": 101, "x": 32, "y": 0, "width": 32, "height": 32},
        ],
        "search": [
            {"name": "Solevis", "id": 6635604, "trophy": 1000},
            {"name": "Test Player", "id": 1, "trophy": 500},
        ],
    }


@pytest.fixture
def mock_player_service(mock_api_responses):
    """Mock PlayerService for testing."""
    with patch("app.services.player.PlayerService") as mock_service:
        instance = mock_service.return_value

        def mock_get_player_data(search=""):
            if search:
                return [p for p in mock_api_responses["players"] if p["name"].lower() == search.lower()]
            return mock_api_responses["players"]

        def mock_get_ship_data(name):
            if name == "Solevis":
                return mock_api_responses["player_ship"]
            return None

        instance.get_player_data = mock_get_player_data
        instance.get_ship_data = mock_get_ship_data

        yield instance


@pytest.fixture
def mock_daily_offer_service(mock_api_responses):
    """Mock DailyOfferService for testing."""
    with patch("app.services.daily_offer.DailyOfferService") as mock_service:
        instance = mock_service.return_value
        instance.daily_offers = mock_api_responses["daily"]
        yield instance


@pytest.fixture
def mock_changes_service(mock_api_responses):
    """Mock ChangesService for testing."""
    with patch("app.services.changes.ChangesService") as mock_service:
        instance = mock_service.return_value
        instance.changes = mock_api_responses["changes"]["changes"]
        instance.last_prestiges_changes = mock_api_responses["changes"]["last_prestiges"]
        yield instance


@pytest.fixture
def mock_collection_service(mock_api_responses):
    """Mock CollectionService for testing."""
    with patch("app.services.collection.CollectionService") as mock_service:
        instance = mock_service.return_value
        instance.collections = mock_api_responses["collections"]
        yield instance


@pytest.fixture
def mock_achievement_service(mock_api_responses):
    """Mock AchievementService for testing."""
    with patch("app.services.achievement.AchievementService") as mock_service:
        instance = mock_service.return_value
        instance.achievements = mock_api_responses["achievements"]
        yield instance


@pytest.fixture
def mock_research_service(mock_api_responses):
    """Mock ResearchService for testing."""
    with patch("app.services.research.ResearchService") as mock_service:
        instance = mock_service.return_value
        instance.researches = dict(enumerate(mock_api_responses["research"]))

        def mock_get_researches_and_ship_min_level():
            return instance.researches

        instance.get_researches_and_ship_min_level = mock_get_researches_and_ship_min_level
        yield instance


@pytest.fixture
def mock_prestige_service(mock_api_responses):
    """Mock PrestigeService for testing."""
    with patch("app.services.prestige.PrestigeService") as mock_service:
        instance = mock_service.return_value

        def mock_get_prestige(char_id):
            return [p for p in mock_api_responses["prestige"] if p["character1"] == char_id]

        instance.get_prestige = mock_get_prestige
        yield instance


@pytest.fixture
def mock_craft_service(mock_api_responses):
    """Mock CraftService for testing."""
    with patch("app.services.craft.CraftService") as mock_service:
        instance = mock_service.return_value
        instance.crafts = mock_api_responses["crafts"]
        yield instance


@pytest.fixture
def mock_missile_service(mock_api_responses):
    """Mock MissileService for testing."""
    with patch("app.services.missile.MissileService") as mock_service:
        instance = mock_service.return_value
        instance.missiles = mock_api_responses["missiles"]
        yield instance


@pytest.fixture
def mock_ship_service(mock_api_responses):
    """Mock ShipService for testing."""
    with patch("app.services.ship.ShipService") as mock_service:
        instance = mock_service.return_value
        instance.ships = mock_api_responses["ships"]
        yield instance


@pytest.fixture
def mock_item_service(mock_api_responses):
    """Mock ItemService for testing."""
    with patch("app.services.item.ItemService") as mock_service:
        instance = mock_service.return_value
        instance.items = mock_api_responses["items"]
        yield instance


@pytest.fixture
def mock_room_service(mock_api_responses):
    """Mock RoomService for testing."""
    with patch("app.services.room.RoomService") as mock_service:
        instance = mock_service.return_value
        instance.rooms = mock_api_responses["rooms"]
        yield instance


@pytest.fixture
def mock_skin_service(mock_api_responses):
    """Mock SkinService for testing."""
    with patch("app.services.skin.SkinService") as mock_service:
        instance = mock_service.return_value
        instance.skins = mock_api_responses["skins"]
        yield instance


@pytest.fixture
def mock_sprite_service(mock_api_responses):
    """Mock SpriteService for testing."""
    with patch("app.services.sprite.SpriteService") as mock_service:
        instance = mock_service.return_value
        instance.sprites = mock_api_responses["sprites"]
        yield instance


# Test functions using mocked services


def test_api_players(client, app, mock_player_service):
    """Test players endpoint with mocked data."""
    # Clear cache to ensure we get fresh data
    with app.test_request_context():
        from app.ext import cache

        cache.clear()

    with app.test_request_context(), patch("app.blueprints.api.PlayerService", return_value=mock_player_service):
        response = client.get(url_for("api.api_players"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["name"] == "Solevis"


def test_api_player(client, app, mock_player_service):
    """Test player endpoint with mocked data."""
    with app.test_request_context(), patch("app.blueprints.api.PlayerService", return_value=mock_player_service):
        response = client.get(url_for("api.api_player", name="Solevis"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert data["data"]["player"]["name"] == "Solevis"
    assert data["data"]["ship"]["name"] == "Test Ship"


def test_api_daily(client, app, mock_daily_offer_service):
    """Test daily endpoint with mocked data."""
    with (
        app.test_request_context(),
        patch("app.blueprints.api.DailyOfferService", return_value=mock_daily_offer_service),
    ):
        response = client.get(url_for("api.api_daily"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "shop" in data["data"]


def test_api_changes(client, app):
    """Test changes endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_changes"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "lastprestigeschanges" in data


def test_api_collections(client, app):
    """Test collections endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_collections"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_achievements(client, app):
    """Test achievements endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_achievements"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_research(client, app, mock_research_service):
    """Test research endpoint with mocked data."""
    with app.test_request_context(), patch("app.blueprints.api.ResearchService", return_value=mock_research_service):
        response = client.get(url_for("api.api_research"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_prestige(client, app):
    """Test prestige endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_prestige", char_id=196))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_crafts(client, app):
    """Test crafts endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_crafts"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_missiles(client, app):
    """Test missiles endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_missiles"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_ships(client, app):
    """Test ships endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_ships"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_items(client, app):
    """Test items endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_items"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_rooms(client, app):
    """Test rooms endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_rooms"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0


def test_api_skins(client, app):
    """Test skins endpoint with mocked data."""
    with app.test_request_context():
        response = client.get(url_for("api.api_skins"))
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert len(data["data"]) > 0
