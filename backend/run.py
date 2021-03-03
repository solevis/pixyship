import io
import os
from datetime import datetime as dt, timedelta

import flask
from PIL import Image
from flask import Flask, render_template, jsonify, send_file, session, request
from flask_cors import CORS

from api_helpers import _get_ship_data, encrypt, player_data
from config import CONFIG
from models import db
from ps_client import PixelStarshipsApi

if __name__ == '__main__':
    CONFIG['DEV_MODE'] = True

APP_NAME = 'pixyship'
app = Flask(APP_NAME, static_folder="../dist/static", template_folder="../dist")
app.secret_key = 'Su8#kKpY4wxMFB*P2X9a66k7%DRbHw'

# Security
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

# SQLAlchemy Object
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['DSN']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


cors_resources = {
    r"/api/*": {
        "origins": [
            "https://{}".format(CONFIG['DOMAIN']),
            "http://{}".format(CONFIG['DOMAIN'])
        ]
    }
}

cors = CORS(
    app,
    supports_credentials=True,
    resources=cors_resources
)

psa = PixelStarshipsApi()


def push_context():
    """ Set the app context for repl environments like ipython. Do not use in the
    app
    """
    app.app_context().push()


@app.before_request
def before_request():
    session.permanent = False
    if os.path.exists("maintenance"):   # Check if a "maintenance" file exists (whatever it is empty or not)
        flask.abort(503)    # No need to worry about the current URL, redirection, etc


@app.after_request
def after_request(response):
    response.delete_cookie(app.session_cookie_name)

    # Security headers
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers['Content-Security-Policy'] = "default-src https:"

    return response


@app.errorhandler(503)
def error_503(error):   # Maintenance
    return 'PixyShip is down for maintenance', 503


def enforce_source(func):
    def wrapper(*args, **kwargs):
        if not(CONFIG['DEV_MODE']
               or (flask.request.referrer
                   and ('//{}/'.format(CONFIG['DOMAIN']) in flask.request.referrer
                        or '//www.{}/'.format(CONFIG['DOMAIN']) in flask.request.referrer))):
            flask.abort(404)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__    # Let's flask see the underlying function
    return wrapper


# APIs first -------------------------------

@app.route('/api/verify/<string:name>')
def api_verify(name):
    if not name:
        flask.abort(400)

    try:
        minerals = int(request.args.get('minerals') or 0)
        gas = int(request.args.get('gas') or 0)

        data, status = check_verification(gas, minerals, name)

        response = {
            'data': data,
            'status': status
        }
        json_response = jsonify(response)
        return json_response

    except ValueError:
        return jsonify({'status': 'fail', 'message': 'Only integer input is accepted'}), 400


def check_verification(gas, minerals, name):
    data_name, m, g, player_id = psa.get_verification_data(name)
    verified = minerals == m and gas == g
    if data_name and verified:
        expires_at = int((dt.utcnow() + timedelta(days=14)).timestamp())
        key_data = {
            'name': name,
            'expires_at': expires_at
        }
        key = encrypt(key_data)
        data = {
            'verified': verified,
            'expires_at': expires_at,
            'key': key,
            'player_id': player_id,
        }
        status = 'success'
    else:
        data = {'verified': False, 'key': None, 'expires_at': 0}
        status = 'fail'
    return data, status


@app.route('/api/players')
def api_players():
    search = request.args.get('search') or ''
    response = jsonify(player_data(search))
    response.cache_control.max_age = 300
    return response


@app.route('/api/name_typeahead')
def api_name_typeahead():
    from api_helpers import search_player

    search = request.args.get('search') or ''
    response = jsonify(search_player(search))
    response.cache_control.max_age = 300
    return response


@app.route('/api/user/<string:name>')
@enforce_source
def api_ship(name):
    if not name:
        flask.abort(400)

    key = request.args.get('key') or ''

    d = _get_ship_data(name, key)
    return d


@app.route('/api/daily')
@enforce_source
def api_daily():
    return jsonify({
        'data': psa.daily_data,
        'status': 'success',
    })


@app.route('/api/changes')
@enforce_source
def api_changes():
    return jsonify({
        'data': psa.change_data,
        'status': 'success',
    })


@app.route('/api/collections')
@enforce_source
def api_collections():
    return jsonify({
        'data': psa.collection_map,
        'status': 'success',
    })


@app.route('/api/research')
@enforce_source
def api_research():
    return jsonify({
        'data': psa.research_map,
        'status': 'success',
    })


@app.route('/api/prestige/<int:char_id>')
@enforce_source
def api_prestige(char_id):
    return jsonify({
        'data': psa.prestige_data(char_id),
        'status': 'success',
    })


@app.route('/api/crew')
@enforce_source
def api_crew():
    return jsonify({
        'data': psa.char_map,
        'status': 'success',
    })


@app.route('/api/items')
@app.route('/api/items2')
@enforce_source
def api_items():
    return jsonify({
        'data': psa.item_map,
        'status': 'success',
    })


@app.route('/api/item/<int:item_id>/prices')
@enforce_source
def api_item_prices(item_id):
    data = psa.get_item_prices(item_id)
    return jsonify({
        'data': data,
        'status': 'success',
    })


@app.route('/api/rooms')
@enforce_source
def api_rooms():
    return jsonify({
        'data': psa.room_map,
        'status': 'success',
    })


@app.route('/api/ships')
@enforce_source
def api_ships():
    return jsonify({
        'data': psa.ship_map,
        'status': 'success',
    })


@app.route('/api/sprite/<int:sprite_id>')
def sprite(sprite_id):
    d = psa.sprite_map.get(sprite_id, {})
    if d:
        filename = filename_from_id(d['image_file'])
        try:
            with Image.open(filename) as im:
                part = im.crop((d['x'], d['y'], d['x'] + d['width'], d['y'] + d['height']))
                output = io.BytesIO()
                part.save(output, 'PNG')
                output.seek(0)
                return send_file(output, mimetype='image/png')
        except IOError:
            pass
    return flask.abort(404)


@app.route('/api/<path:path>')
def bad_api(path):
    """Places you shouldn't go"""
    return flask.abort(404)


@app.route('/crew/<int:id>')
def page_crew_prestige(id):
    return render_template('index.html')


# Vue Rendering
@app.route('/crew')
@app.route('/items')
@app.route('/rooms')
@app.route('/ships')
@app.route('/builder')
@app.route('/changes')
@app.route('/players')
@app.route('/collections')
@app.route('/research')
@app.route('/', defaults={'path': ''})
def page_base(path=''):
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/<path:path>')
def catch_all(path):
    return flask.redirect("/")


def dev_run():
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    dev_run()
