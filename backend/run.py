import os

import flask
from flask import Flask, jsonify, session, request
from flask_cors import CORS

from config import CONFIG
from db import db
from pixyship import PixyShip

PUBLIC_ENDPOINTS = []
APP_NAME = 'pixyship'

app = Flask(APP_NAME)

# a secret key that will be used for securely signing the session cookie
app.secret_key = CONFIG['SECRET_KEY']

# configure cookie security
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

# database settings
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# configure cors (Cross-Origin Resource Sharing)
if CONFIG['DEV_MODE']:
    cors = CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": "*"}}
    )
else:
    cors = CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": [
                    "https://{}".format(CONFIG['DOMAIN']),
                    "http://{}".format(CONFIG['DOMAIN'])
                ]
            }
        }
    )

# helpers, cached data, etc.
pixyship = PixyShip()


def push_context():
    """Set the app context for repl environments like ipython.

    Do not use in the app.
    See https://flask.palletsprojects.com/en/1.1.x/appcontext/#manually-push-a-context
    """
    app.app_context().push()


def enforce_source(func):
    """Decorator checking in production if the referrer is really PixyShip."""

    def wrapper(*args, **kwargs):
        # no need to check referrer if endpoint is public
        if not CONFIG['DEV_MODE'] and flask.request.endpoint not in PUBLIC_ENDPOINTS:
            # referrer is PixyShip ?
            if flask.request.referrer and '//{}/'.format(CONFIG['DOMAIN']) not in flask.request.referrer:
                flask.abort(404)

        return func(*args, **kwargs)

    # lets flask see the underlying function
    wrapper.__name__ = func.__name__

    return wrapper


@app.before_request
def before_request():
    """Before each request."""

    # manage session timeout
    session.permanent = False

    # check if a "maintenance" file exists, if it's the case, enable maintenance mode
    if os.path.exists("maintenance"):
        flask.abort(503)


@app.after_request
def after_request(response):
    """Before sending the request to the client."""

    # delete the session cookie, unneeded for PixyShip
    response.delete_cookie(app.session_cookie_name)

    # security headers for API
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

    return response


@app.errorhandler(503)
def error_503(_):
    """Maintenance."""
    return 'PixyShip is down for maintenance', 503


@app.route('/api/players')
def api_players():
    search = request.args.get('search') or ''
    response = jsonify(pixyship.get_player_data(search))
    response.cache_control.max_age = 300
    return response


@app.route('/api/user/<path:name>')
@enforce_source
def api_ship(name):
    if not name:
        flask.abort(400)

    ship_data = pixyship.get_ship_data(name)

    return jsonify(ship_data)


@app.route('/api/daily')
@enforce_source
def api_daily():
    return jsonify({
        'data': pixyship.dailies,
        'status': 'success',
    })


@app.route('/api/changes')
@enforce_source
def api_changes():
    last_prestiges_changes = pixyship.last_prestiges_changes

    return jsonify({
        'data': pixyship.changes,
        'lastprestigeschanges': last_prestiges_changes,
        'status': 'success',
    })


@app.route('/api/collections')
@enforce_source
def api_collections():
    return jsonify({
        'data': pixyship.collections,
        'status': 'success',
    })


@app.route('/api/achievements')
@enforce_source
def api_achievements():
    return jsonify({
        'data': pixyship.achievements,
        'status': 'success',
    })


@app.route('/api/research')
@enforce_source
def api_research():
    return jsonify({
        'data': pixyship.get_researches_and_ship_min_level(),
        'status': 'success',
    })


@app.route('/api/prestige/<int:char_id>')
@enforce_source
def api_prestige(char_id):
    return jsonify({
        'data': pixyship.get_prestiges_from_api(char_id),
        'status': 'success',
    })


@app.route('/api/crew')
@enforce_source
def api_crew():
    return jsonify({
        'data': pixyship.characters,
        'status': 'success',
    })


@app.route('/api/items')
@enforce_source
def api_items():
    return jsonify({
        'data': pixyship.items,
        'status': 'success',
    })


@app.route('/api/item/<int:item_id>/prices')
@enforce_source
def api_item_prices(item_id):
    data = pixyship.get_item_prices_from_db(item_id)
    return jsonify({
        'data': data,
        'status': 'success',
    })


@app.route('/api/item/<int:item_id>/detail')
@enforce_source
def api_item_detail(item_id):
    item = pixyship.items[item_id]
    last_players_sales = pixyship.get_item_last_players_sales_from_db(item_id, 50)
    upgrades = pixyship.get_item_upgrades(item['id'])
    return jsonify({
        'data': item,
        'lastPlayersSales': last_players_sales,
        'upgrades': upgrades,
        'status': 'success',
    })


@app.route('/api/tournament')
@enforce_source
def api_tournament():
    return jsonify({
        'data': pixyship.get_tournament_infos(),
        'status': 'success',
    })


@app.route('/api/rooms')
@enforce_source
def api_rooms():
    rooms = pixyship.rooms
    rooms_sprites = pixyship.rooms_sprites
    data = pixyship.merge_rooms_and_sprites(rooms, rooms_sprites)

    return jsonify({
        'data': data,
        'status': 'success',
    })


@app.route('/api/ships')
@enforce_source
def api_ships():
    return jsonify({
        'data': pixyship.ships,
        'status': 'success',
    })

@app.route('/api/lastsales/<path:type>/<int:type_id>')
@enforce_source
def api_last_sales(type, type_id):
    last_sales = pixyship.get_last_sales_from_db(type, type_id, 1000)
    return jsonify({
        'data': last_sales,
        'status': 'success',
    })

@app.route('/api/lastsalesbysalefrom/<path:sale_from>')
@enforce_source
def api_last_sales_by_type(sale_from):
    last_sales = pixyship.get_last_sales_by_sale_from_from_db(sale_from, 5000)
    return jsonify({
        'data': last_sales,
        'status': 'success',
    })

@app.route('/api/<path:path>')
def bad_api(_):
    """Places you shouldn't go"""
    return flask.abort(404)


if __name__ == '__main__':
    """Launch the built-in server.
    Do not use in production.
    """

    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', threaded=True)
