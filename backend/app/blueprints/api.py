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
from app.services.reasearch import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.skin import SkinService
from app.utils.pss import get_type_enum_from_string

api_blueprint = Blueprint("api", __name__)


def make_players_search_key() -> str:
    """Make the cache key for the players search."""
    search = request.args.get("search") or ""
    return f"api_players_{search}"


@api_blueprint.route("/players")
@enforce_source
@cache.cached(make_cache_key=make_players_search_key)
def api_players() -> Response:
    """Return all players."""
    player_service = PlayerService()
    search = request.args.get("search") or ""

    return jsonify(
        {
            "data": player_service.get_player_data(search),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/players/<path:name>")
@enforce_source
@cache.cached()
def api_player(name: str) -> Response:
    """Return the ship data of a player."""
    if not name:
        flask.abort(400)

    player_service = PlayerService()
    ship_data = player_service.get_ship_data(escape(name))

    if ship_data is None:
        flask.abort(404)

    return jsonify(
        {
            "data": ship_data,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/daily")
@enforce_source
@cache.cached()
def api_daily() -> Response:
    """Return daily offers."""
    daily_offer_service = DailyOfferService()
    return jsonify(
        {
            "data": daily_offer_service.daily_offers,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/changes")
@enforce_source
@cache.cached()
def api_changes() -> Response:
    """Return the changes and the last prestiges changes."""
    changes_service = ChangesService()
    return jsonify(
        {
            "data": changes_service.changes,
            "lastprestigeschanges": changes_service.last_prestiges_changes,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/collections")
@enforce_source
@cache.cached()
def api_collections() -> Response:
    """Return the collections."""
    collection_service = CollectionService()
    collections = collection_service.collections
    character_service = CharacterService()
    characters = character_service.characters

    collections_to_remove = []
    for collection_id, collection in collections.items():
        collection_characters = [
            character for character in characters.values() if character["collection"] == collection_id
        ]
        if collection_characters:
            collection["chars"] = collection_characters
        else:
            collections_to_remove.append(collection_id)

    # Remove collections without characters
    for collection_id in collections_to_remove:
        collections.pop(collection_id)

    return jsonify(
        {
            "data": collections,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/achievements")
@enforce_source
@cache.cached()
def api_achievements() -> Response:
    """Return the achievements."""
    achievement_service = AchievementService()
    return jsonify(
        {
            "data": achievement_service.achievements,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/research")
@enforce_source
@cache.cached()
def api_research() -> Response:
    """Return the researches and the ship min level."""
    research_service = ResearchService()
    return jsonify(
        {
            "data": research_service.get_researches_and_ship_min_level(),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/prestige/<int:char_id>")
@enforce_source
@cache.cached()
def api_prestige(char_id: int) -> Response:
    """Return the prestiges of a character."""
    try:
        character_service = CharacterService()
        character = character_service.characters[char_id]
    except KeyError:
        flask.abort(404)

    prestige_service = PrestigeService()
    return jsonify(
        {
            "data": prestige_service.get_prestiges_from_api(character["id"]),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/crew")
@enforce_source
@cache.cached()
def api_crew() -> Response:
    """Return all crew."""
    character_service = CharacterService()
    characters = character_service.characters
    collection_service = CollectionService()
    collections = collection_service.collections

    for character in characters.values():
        if character["collection"]:
            character["collection_sprite"] = collections[character["collection"]]["icon_sprite"]
            character["collection_name"] = collections[character["collection"]]["name"]

    return jsonify(
        {
            "data": characters,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/items")
@enforce_source
@cache.cached()
def api_items() -> Response:
    """Return all items."""
    item_service = ItemService()
    return jsonify(
        {
            "data": item_service.items,
            "status": "success",
            "current_time": time.time(),
        },
    )


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
    return jsonify(
        {
            "data": market_service.get_item_prices(item["id"]),
            "status": "success",
            "current_time": time.time(),
        },
    )


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

    return jsonify(
        {
            "data": item,
            "lastPlayersSales": last_players_sales,
            "upgrades": upgrades,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/tournament")
@enforce_source
@cache.cached()
def api_tournament() -> Response:
    """Return the tournament infos."""
    pixyship_service = PixyShipService()
    return jsonify(
        {
            "data": pixyship_service.get_tournament_infos(),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/rooms")
@enforce_source
@cache.cached()
def api_rooms() -> Response:
    """Return all rooms."""
    room_service = RoomService()
    return jsonify(
        {
            "data": room_service.rooms,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/skins")
@enforce_source
@cache.cached()
def api_skins() -> Response:
    """Return all skins."""
    # keep only skins with sprite_type = "Interior"
    skin_service = SkinService()
    skins = [skin for skin in skin_service.skins.values() if skin["sprite_type"] == "Interior"]

    return jsonify(
        {
            "data": skins,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/ships")
@enforce_source
@cache.cached()
def api_ships() -> Response:
    """Return all ships."""
    ship_service = ShipService()
    return jsonify(
        {
            "data": ship_service.ships,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/lastsales/<path:sale_type>/<int:sale_type_id>")
@enforce_source
@cache.cached()
def api_last_sales(sale_type: str, sale_type_id: int) -> Response:
    """Return the last sales of a given type."""
    type_enum = get_type_enum_from_string(escape(sale_type))
    if type_enum is None:
        flask.abort(404)

    daily_offer_service = DailyOfferService()
    return jsonify(
        {
            "data": daily_offer_service.get_last_sales_from_db(type_enum, sale_type_id, 1000),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/lastsalesbysalefrom/<path:sale_from>")
@enforce_source
@cache.cached()
def api_last_sales_by_type(sale_from: str) -> Response:
    """Return the last sales by sale_from."""
    daily_offer_service = DailyOfferService()
    return jsonify(
        {
            "data": daily_offer_service.get_last_sales_by_sale_from_from_db(escape(sale_from), 5000),
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/crafts")
@enforce_source
@cache.cached()
def api_crafts() -> Response:
    """Return all crafts."""
    craft_service = CraftService()
    return jsonify(
        {
            "data": craft_service.crafts,
            "status": "success",
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/missiles")
@enforce_source
@cache.cached()
def api_missiles() -> Response:
    """Return all missiles."""
    missile_service = MissileService()
    return jsonify(
        {
            "data": missile_service.missiles,
            "status": "success",
            "current_time": time.time(),
        },
    )


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
    return jsonify(
        {
            "current_time": time.time(),
        },
    )


@api_blueprint.route("/<path:path>")
@enforce_source
def bad_api(path: str) -> Response:
    """Bad API request."""
    current_app.logger.warning("Bad API request: %s", escape(path))
    return flask.abort(404)
