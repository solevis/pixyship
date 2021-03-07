import os

import flask
from flask import Flask, render_template, jsonify, session, request
from flask_cors import CORS

from api_helpers import get_ship_data, get_player_data
from config import CONFIG
from db import db
from ps_client import PixelStarshipsApi


APP_NAME = 'pixyship'
app = Flask(APP_NAME, static_folder="../dist/static", template_folder="../dist")

# a secret key that will be used for securely signing the session cookie
app.secret_key = CONFIG['SECRET_KEY']

# configure cookie security
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)

# database settings
app.config['SQLALCHEMY_DATABASE_URI'] = CONFIG['DSN']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# configure cors (Cross-Origin Resource Sharing)
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

pixel_starships_api = PixelStarshipsApi()


def push_context():
    """Set the app context for repl environments like ipython.

    Do not use in the app.
    See https://flask.palletsprojects.com/en/1.1.x/appcontext/#manually-push-a-context
    """
    app.app_context().push()


def enforce_source(func):
    """Decorator checking in production if the referrer is really Pixyship."""

    def wrapper(*args, **kwargs):
        # not needed to check referrer in DEV
        if not (CONFIG['DEV_MODE']
                # referrer is present
                or (flask.request.referrer
                    # referrer is Pixyship ?
                    and ('//{}/'.format(CONFIG['DOMAIN']) in flask.request.referrer
                         # check also www subdomain
                         or '//www.{}/'.format(CONFIG['DOMAIN']) in flask.request.referrer))):
            flask.abort(404)
        return func(*args, **kwargs)

    # let's flask see the underlying function
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

    # delete the session cookie, unneeded for Pixyship
    response.delete_cookie(app.session_cookie_name)

    # security headers
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers['Content-Security-Policy'] = \
        "default-src 'self';" \
        "img-src 'self' data: pixelstarships.s3.amazonaws.com;" \
        "style-src 'self' 'unsafe-inline' 'unsafe-eval';" \
        "script-src 'self' 'unsafe-eval';" \
        "report-uri /csp_report;"

    return response


@app.errorhandler(503)
def error_503(error):
    """Maintenance."""
    return 'PixyShip is down for maintenance', 503


@app.route('/api/players')
def api_players():
    search = request.args.get('search') or ''
    response = jsonify(get_player_data(search))
    response.cache_control.max_age = 300
    return response


@app.route('/api/user/<string:name>')
@enforce_source
def api_ship(name):
    if not name:
        flask.abort(400)

    ship_data = get_ship_data(name)

    return ship_data


@app.route('/api/daily')
@enforce_source
def api_daily():
    return jsonify({
        'data': pixel_starships_api.daily_data,
        'status': 'success',
    })


@app.route('/api/changes')
@enforce_source
def api_changes():
    return jsonify({
        'data': pixel_starships_api.change_data,
        'status': 'success',
    })


@app.route('/api/collections')
@enforce_source
def api_collections():
    return jsonify({
        'data': pixel_starships_api.collection_map,
        'status': 'success',
    })


@app.route('/api/research')
@enforce_source
def api_research():
    return jsonify({
        'data': pixel_starships_api.research_map,
        'status': 'success',
    })


@app.route('/api/prestige/<int:char_id>')
@enforce_source
def api_prestige(char_id):
    return jsonify({
        'data': pixel_starships_api.get_prestige_data(char_id),
        'status': 'success',
    })


@app.route('/api/crew')
@enforce_source
def api_crew():
    return jsonify({
        'data': pixel_starships_api.char_map,
        'status': 'success',
    })


@app.route('/api/items')
@enforce_source
def api_items():
    return jsonify({
        'data': pixel_starships_api.item_map,
        'status': 'success',
    })


@app.route('/api/item/<int:item_id>/prices')
@enforce_source
def api_item_prices(item_id):
    data = pixel_starships_api.get_item_prices(item_id)
    return jsonify({
        'data': data,
        'status': 'success',
    })


@app.route('/api/rooms')
@enforce_source
def api_rooms():
    return jsonify({
        'data': pixel_starships_api.room_map,
        'status': 'success',
    })


@app.route('/api/ships')
@enforce_source
def api_ships():
    return jsonify({
        'data': pixel_starships_api.ship_map,
        'status': 'success',
    })


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


@app.route('/csp_report', methods=['POST'])
def csp_report():
    if CONFIG['CSP_REPORT_LOG']:
        with open(CONFIG['CSP_REPORT_LOG'], "a") as fh:
            fh.write(request.data.decode() + "\n")

    return 'done'


@app.route('/<path:path>')
def catch_all(path):
    return flask.redirect("/")


if __name__ == '__main__':
    """Launch the built-in server. 
    Do not use in production.
    """

    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', threaded=True)
