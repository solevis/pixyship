import flask
from flask import Blueprint, jsonify, request

from app.pixyship import PixyShip
from app.security import enforce_source

api_blueprint = Blueprint("api", __name__)
pixyship = PixyShip()


@api_blueprint.route("/players")
def api_players():
    search = request.args.get("search") or ""
    response = jsonify(pixyship.get_player_data(search))
    response.cache_control.max_age = 300
    return response


@api_blueprint.route("/user/<path:name>")
@enforce_source
def api_ship(name):
    if not name:
        flask.abort(400)

    ship_data = pixyship.get_ship_data(name)

    return jsonify(ship_data)


@api_blueprint.route("/daily")
@enforce_source
def api_daily():
    return jsonify(
        {
            "data": pixyship.dailies,
            "status": "success",
        }
    )


@api_blueprint.route("/changes")
@enforce_source
def api_changes():
    last_prestiges_changes = pixyship.last_prestiges_changes

    return jsonify(
        {
            "data": pixyship.changes,
            "lastprestigeschanges": last_prestiges_changes,
            "status": "success",
        }
    )


@api_blueprint.route("/collections")
@enforce_source
def api_collections():
    return jsonify(
        {
            "data": pixyship.collections,
            "status": "success",
        }
    )


@api_blueprint.route("/achievements")
@enforce_source
def api_achievements():
    return jsonify(
        {
            "data": pixyship.achievements,
            "status": "success",
        }
    )


@api_blueprint.route("/research")
@enforce_source
def api_research():
    return jsonify(
        {
            "data": pixyship.get_researches_and_ship_min_level(),
            "status": "success",
        }
    )


@api_blueprint.route("/prestige/<int:char_id>")
@enforce_source
def api_prestige(char_id):
    prestiges_from_api = pixyship.get_prestiges_from_api(char_id)
    return jsonify(
        {
            "data": prestiges_from_api,
            "status": "success",
        }
    )


@api_blueprint.route("/crew")
@enforce_source
def api_crew():
    return jsonify(
        {
            "data": pixyship.characters,
            "status": "success",
        }
    )


@api_blueprint.route("/items")
@enforce_source
def api_items():
    return jsonify(
        {
            "data": pixyship.items,
            "status": "success",
        }
    )


@api_blueprint.route("/item/<int:item_id>/prices")
@enforce_source
def api_item_prices(item_id):
    data = pixyship.get_item_prices_from_db(item_id)
    return jsonify(
        {
            "data": data,
            "status": "success",
        }
    )


@api_blueprint.route("/item/<int:item_id>/detail")
@enforce_source
def api_item_detail(item_id):
    try:
        item = pixyship.items[item_id]
    except KeyError:
        flask.abort(404)

    last_players_sales = pixyship.get_item_last_players_sales_from_db(item_id, 5000)
    upgrades = pixyship.get_item_upgrades(item["id"])
    return jsonify(
        {
            "data": item,
            "lastPlayersSales": last_players_sales,
            "upgrades": upgrades,
            "status": "success",
        }
    )


@api_blueprint.route("/tournament")
@enforce_source
def api_tournament():
    return jsonify(
        {
            "data": pixyship.get_tournament_infos(),
            "status": "success",
        }
    )


@api_blueprint.route("/rooms")
@enforce_source
def api_rooms():
    rooms = pixyship.rooms

    return jsonify(
        {
            "data": rooms,
            "status": "success",
        }
    )


@api_blueprint.route("/skins")
@enforce_source
def api_skins():
    skins = pixyship.skins

    # keep only skins with sprite_type = "Interior"
    skins = [skin for skin in skins.values() if skin["sprite_type"] == "Interior"]

    return jsonify(
        {
            "data": skins,
            "status": "success",
        }
    )


@api_blueprint.route("/ships")
@enforce_source
def api_ships():
    return jsonify(
        {
            "data": pixyship.ships,
            "status": "success",
        }
    )


@api_blueprint.route("/lastsales/<path:sale_type>/<int:sale_type_id>")
@enforce_source
def api_last_sales(sale_type, sale_type_id):
    last_sales = pixyship.get_last_sales_from_db(sale_type, sale_type_id, 1000)
    return jsonify(
        {
            "data": last_sales,
            "status": "success",
        }
    )


@api_blueprint.route("/lastsalesbysalefrom/<path:sale_from>")
@enforce_source
def api_last_sales_by_type(sale_from):
    last_sales = pixyship.get_last_sales_by_sale_from_from_db(sale_from, 5000)
    return jsonify(
        {
            "data": last_sales,
            "status": "success",
        }
    )


@api_blueprint.route("/crafts")
@enforce_source
def api_crafts():
    crafts = pixyship.crafts

    return jsonify(
        {
            "data": crafts,
            "status": "success",
        }
    )


@api_blueprint.route("/missiles")
@enforce_source
def api_missiles():
    missiles = pixyship.missiles

    return jsonify(
        {
            "data": missiles,
            "status": "success",
        }
    )


@api_blueprint.route("/<path:path>")
def bad_api(_):
    """Places you shouldn't go"""
    return flask.abort(404)
