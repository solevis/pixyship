import time

import flask
from flask import Blueprint, Response, current_app, jsonify, request
from markupsafe import escape

from app.ext import cache
from app.security import enforce_source
from app.services.achievement import AchievementService
from app.services.changes import ChangesService
from app.services.character import CharacterService
from app.services.collection import CollectionService
from app.services.craft import CraftService
from app.services.daily_offer import DailyOfferService
from app.services.item import ItemService
from app.services.market import MarketService
from app.services.missile import MissileService
from app.services.pixyship import PixyShipService
from app.services.player import PlayerService
from app.services.prestige import PrestigeService
from app.services.research import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.skin import SkinService
from app.utils.pss import get_type_enum_from_string

api_blueprint = Blueprint("api", __name__)


def success_response(data: object, **extra: object) -> Response:
    """Return the standard API JSON response, with the given data and extra fields."""
    return jsonify(
        {
            "data": data,
            **extra,
            "status": "success",
            "current_time": time.time(),
        },
    )


# longer than any player name, avoids unbounded cache keys
MAX_PLAYERS_SEARCH_LENGTH = 50


def get_players_search() -> str:
    """Get the normalized players search (the search is case-insensitive)."""
    search = request.args.get("search") or ""
    return search.strip().lower()[:MAX_PLAYERS_SEARCH_LENGTH]


def make_players_search_key() -> str:
    """Make the cache key for the players search."""
    return f"api_players_{get_players_search()}"


@api_blueprint.route("/players")
@enforce_source
@cache.cached(make_cache_key=make_players_search_key)
def api_players() -> Response:
    """Return all players."""
    player_service = PlayerService()
    search = get_players_search()

    return success_response(player_service.get_player_data(search))


@api_blueprint.route("/players/<path:name>")
@enforce_source
@cache.cached()
def api_player(name: str) -> Response:
    """Return the ship data of a player."""
    if not name:
        flask.abort(400)

    player_service = PlayerService()
    ship_data = player_service.get_ship_data(name)

    if ship_data is None:
        flask.abort(404)

    return success_response(ship_data)


@api_blueprint.route("/daily")
@enforce_source
@cache.cached()
def api_daily() -> Response:
    """Return daily offers."""
    daily_offer_service = DailyOfferService()
    return success_response(daily_offer_service.daily_offers)


@api_blueprint.route("/changes")
@enforce_source
@cache.cached()
def api_changes() -> Response:
    """Return the changes and the last prestiges changes."""
    changes_service = ChangesService()
    return success_response(changes_service.changes, lastprestigeschanges=changes_service.last_prestiges_changes)


@api_blueprint.route("/collections")
@enforce_source
@cache.cached()
def api_collections() -> Response:
    """Return the collections."""
    collection_service = CollectionService()
    collections = collection_service.get_collections_with_characters()

    return success_response(collections)


@api_blueprint.route("/achievements")
@enforce_source
@cache.cached()
def api_achievements() -> Response:
    """Return the achievements."""
    achievement_service = AchievementService()
    return success_response(achievement_service.achievements)


@api_blueprint.route("/research")
@enforce_source
@cache.cached()
def api_research() -> Response:
    """Return the researches and the ship min level."""
    research_service = ResearchService()
    return success_response(research_service.get_researches_and_ship_min_level())


@api_blueprint.route("/prestige/<int:char_id>")
@enforce_source
@cache.cached()
def api_prestige(char_id: int) -> Response:
    """Return the prestiges of a character."""
    character_service = CharacterService()
    try:
        character = character_service.characters[char_id]
    except KeyError:
        flask.abort(404)

    character_service.add_collection_data(character)

    prestige_service = PrestigeService()
    return success_response(prestige_service.get_prestiges_from_api(character["id"]), character=character)


@api_blueprint.route("/crew")
@enforce_source
@cache.cached()
def api_crew() -> Response:
    """Return all crew."""
    character_service = CharacterService()
    characters = character_service.get_characters_with_collection_data()

    return success_response(characters)


@api_blueprint.route("/items")
@enforce_source
@cache.cached()
def api_items() -> Response:
    """Return all items."""
    item_service = ItemService()
    return success_response(item_service.items)


@api_blueprint.route("/item/<int:item_id>/prices")
@enforce_source
@cache.cached()
def api_item_prices(item_id: int) -> Response:
    """Return the item prices."""
    try:
        item_service = ItemService()
        item = item_service.items[item_id]
    except KeyError:
        flask.abort(404)

    market_service = MarketService()
    return success_response(market_service.get_item_prices(item["id"]))


@api_blueprint.route("/item/<int:item_id>/detail")
@enforce_source
@cache.cached()
def api_item_detail(item_id: int) -> Response:
    """Return the item details."""
    item_service = ItemService()
    try:
        item = item_service.items[item_id]
    except KeyError:
        flask.abort(404)

    market_service = MarketService()
    last_players_sales = market_service.get_item_last_players_sales_from_db(item["id"], 5000)
    upgrades = item_service.get_item_upgrades(item["id"])

    return success_response(item, lastPlayersSales=last_players_sales, upgrades=upgrades)


@api_blueprint.route("/tournament")
@enforce_source
@cache.cached()
def api_tournament() -> Response:
    """Return the tournament infos."""
    pixyship_service = PixyShipService()
    return success_response(pixyship_service.get_tournament_infos())


@api_blueprint.route("/rooms")
@enforce_source
@cache.cached()
def api_rooms() -> Response:
    """Return all rooms."""
    room_service = RoomService()
    return success_response(room_service.rooms)


@api_blueprint.route("/skins")
@enforce_source
@cache.cached()
def api_skins() -> Response:
    """Return all skins."""
    skin_service = SkinService()
    skins = skin_service.skins

    # Remove duplicate skins with the same name
    skins_filtered = {}
    known_names = set()
    for skin_id, skin in skins.items():
        if skin["name"] not in known_names:
            skins_filtered[skin_id] = skin
            known_names.add(skin["name"])

    return success_response(skins_filtered)


@api_blueprint.route("/ships")
@enforce_source
@cache.cached()
def api_ships() -> Response:
    """Return all ships."""
    ship_service = ShipService()
    return success_response(ship_service.ships)


@api_blueprint.route("/lastsales/<path:sale_type>/<int:sale_type_id>")
@enforce_source
@cache.cached()
def api_last_sales(sale_type: str, sale_type_id: int) -> Response:
    """Return the last sales of a given type."""
    type_enum = get_type_enum_from_string(sale_type)
    if type_enum is None:
        flask.abort(404)

    daily_offer_service = DailyOfferService()
    return success_response(daily_offer_service.get_last_sales_from_db(type_enum, sale_type_id, 1000))  # type: ignore[arg-type]


@api_blueprint.route("/lastsalesbysalefrom/<path:sale_from>")
@enforce_source
@cache.cached()
def api_last_sales_by_type(sale_from: str) -> Response:
    """Return the last sales by sale_from."""
    daily_offer_service = DailyOfferService()
    return success_response(daily_offer_service.get_last_sales_by_sale_from_from_db(sale_from, 5000))


@api_blueprint.route("/crafts")
@enforce_source
@cache.cached()
def api_crafts() -> Response:
    """Return all crafts."""
    craft_service = CraftService()
    return success_response(craft_service.crafts)


@api_blueprint.route("/missiles")
@enforce_source
@cache.cached()
def api_missiles() -> Response:
    """Return all missiles."""
    missile_service = MissileService()
    return success_response(missile_service.missiles)


@api_blueprint.route("/config")
@enforce_source
@cache.cached()
def api_config() -> Response:
    """Return the config."""
    return jsonify(
        {
            "spriteUrl": current_app.config["SPRITE_URL"],
            "discordUrl": current_app.config["DISCORD_URL"],
            "githubUrl": current_app.config["GITHUB_URL"],
            "donationUrl": current_app.config["DONATION_URL"],
        },
    )


@api_blueprint.route("/time")
@enforce_source
def api_time() -> Response:
    """Return the current time."""
    response = jsonify(
        {
            "current_time": time.time(),
        },
    )
    response.cache_control.no_store = True
    return response


@api_blueprint.route("/<path:path>")
@enforce_source
def bad_api(path: str) -> Response:
    """Bad API request."""
    current_app.logger.warning("Bad API request: %s", escape(path))
    return flask.abort(404)
