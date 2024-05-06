import flask
from flask import Blueprint, current_app, jsonify, request

from app.ext import cache
from app.security import enforce_source
from app.services.factory import ServiceFactory
from app.utils.pss import get_type_enum_from_string

api_blueprint = Blueprint("api", __name__)
service_factory = ServiceFactory()


def make_players_search_key():
    search = request.args.get("search") or ""
    return f"api_players_{search}"


@api_blueprint.route("/players")
@enforce_source
@cache.cached(make_cache_key=make_players_search_key)
def api_players():
    """Returns all players."""

    player_service = service_factory.player_service
    search = request.args.get("search") or ""

    return jsonify(
        {
            "data": player_service.get_player_data(search),
            "status": "success",
        },
    )


@api_blueprint.route("/players/<path:name>")
@enforce_source
@cache.cached()
def api_player(name):
    """Returns the ship data of a player."""

    if not name:
        flask.abort(400)

    ship_data = service_factory.player_service.get_ship_data(name)

    if ship_data is None:
        flask.abort(404)

    return jsonify(
        {
            "data": ship_data,
            "status": "success",
        },
    )


@api_blueprint.route("/daily")
@enforce_source
@cache.cached()
def api_daily():
    """Returns daily offers."""

    return jsonify(
        {
            "data": service_factory.daily_offer_service.daily_offers,
            "status": "success",
        },
    )


@api_blueprint.route("/changes")
@enforce_source
@cache.cached()
def api_changes():
    """Returns the changes and the last prestiges changes."""

    return jsonify(
        {
            "data": service_factory.changes_service.changes,
            "lastprestigeschanges": service_factory.changes_service.last_prestiges_changes,
            "status": "success",
        },
    )


@api_blueprint.route("/collections")
@enforce_source
@cache.cached()
def api_collections():
    """Returns the collections."""

    collections = service_factory.collection_service.collections
    characters = service_factory.character_service.characters

    for collection_id, collection in collections.items():
        collection["chars"] = [
            character for character in characters.values() if character["collection"] == collection_id
        ]

    return jsonify(
        {
            "data": collections,
            "status": "success",
        },
    )


@api_blueprint.route("/achievements")
@enforce_source
@cache.cached()
def api_achievements():
    """Returns the achievements."""

    return jsonify(
        {
            "data": service_factory.achievement_service.achievements,
            "status": "success",
        },
    )


@api_blueprint.route("/research")
@enforce_source
@cache.cached()
def api_research():
    """Returns the researches and the ship min level."""

    return jsonify(
        {
            "data": service_factory.research_service.get_researches_and_ship_min_level(),
            "status": "success",
        },
    )


@api_blueprint.route("/prestige/<int:char_id>")
@enforce_source
@cache.cached()
def api_prestige(char_id):
    """Returns the prestiges of a character."""

    try:
        character = service_factory.character_service.characters[char_id]
    except KeyError:
        flask.abort(404)

    return jsonify(
        {
            "data": service_factory.prestige_service.get_prestiges_from_api(character["id"]),
            "status": "success",
        },
    )


@api_blueprint.route("/crew")
@enforce_source
@cache.cached()
def api_crew():
    """Returns all crew."""

    return jsonify(
        {
            "data": service_factory.character_service.characters,
            "status": "success",
        },
    )


@api_blueprint.route("/items")
@enforce_source
@cache.cached()
def api_items():
    """Returns all items."""

    return jsonify(
        {
            "data": service_factory.item_service.items,
            "status": "success",
        },
    )


@api_blueprint.route("/item/<int:item_id>/prices")
@enforce_source
@cache.cached()
def api_item_prices(item_id: int):
    """Returns the item prices."""

    try:
        item = service_factory.item_service.items[item_id]
    except KeyError:
        flask.abort(404)

    return jsonify(
        {
            "data": service_factory.market_service.get_item_prices(item["id"]),
            "status": "success",
        },
    )


@api_blueprint.route("/item/<int:item_id>/detail")
@enforce_source
@cache.cached()
def api_item_detail(item_id):
    """Returns the item details."""

    try:
        item = service_factory.item_service.items[item_id]
    except KeyError:
        flask.abort(404)

    last_players_sales = service_factory.market_service.get_item_last_players_sales_from_db(item["id"], 5000)
    upgrades = service_factory.item_service.get_item_upgrades(item["id"])

    return jsonify(
        {
            "data": item,
            "lastPlayersSales": last_players_sales,
            "upgrades": upgrades,
            "status": "success",
        },
    )


@api_blueprint.route("/tournament")
@enforce_source
@cache.cached()
def api_tournament():
    """Returns the tournament infos."""

    return jsonify(
        {
            "data": service_factory.pixyship_service.get_tournament_infos(),
            "status": "success",
        },
    )


@api_blueprint.route("/rooms")
@enforce_source
@cache.cached()
def api_rooms():
    """Returns all rooms."""

    return jsonify(
        {
            "data": service_factory.room_service.rooms,
            "status": "success",
        },
    )


@api_blueprint.route("/skins")
@enforce_source
@cache.cached()
def api_skins():
    """Returns all skins."""

    # keep only skins with sprite_type = "Interior"
    skins = [skin for skin in service_factory.skin_service.skins.values() if skin["sprite_type"] == "Interior"]

    return jsonify(
        {
            "data": skins,
            "status": "success",
        },
    )


@api_blueprint.route("/ships")
@enforce_source
@cache.cached()
def api_ships():
    """Returns all ships."""

    return jsonify(
        {
            "data": service_factory.ship_service.ships,
            "status": "success",
        },
    )


@api_blueprint.route("/lastsales/<path:sale_type>/<int:sale_type_id>")
@enforce_source
@cache.cached()
def api_last_sales(sale_type, sale_type_id):
    """Returns the last sales of a given type."""

    type_enum = get_type_enum_from_string(sale_type)
    return jsonify(
        {
            "data": service_factory.daily_offer_service.get_last_sales_from_db(type_enum, sale_type_id, 1000),
            "status": "success",
        },
    )


@api_blueprint.route("/lastsalesbysalefrom/<path:sale_from>")
@enforce_source
@cache.cached()
def api_last_sales_by_type(sale_from):
    """Returns the last sales by sale_from."""

    return jsonify(
        {
            "data": service_factory.daily_offer_service.get_last_sales_by_sale_from_from_db(sale_from, 5000),
            "status": "success",
        },
    )


@api_blueprint.route("/crafts")
@enforce_source
@cache.cached()
def api_crafts():
    """Returns all crafts."""

    return jsonify(
        {
            "data": service_factory.craft_service.crafts,
            "status": "success",
        },
    )


@api_blueprint.route("/missiles")
@enforce_source
@cache.cached()
def api_missiles():
    """Returns all missiles."""

    return jsonify(
        {
            "data": service_factory.missile_service.missiles,
            "status": "success",
        },
    )


@api_blueprint.route("/<path:path>")
@enforce_source
def bad_api(path):
    """Places you shouldn't go"""
    current_app.logger.warning("Bad API request: %s", path)
    return flask.abort(404)
