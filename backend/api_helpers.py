import json
from datetime import datetime

from cryptography.fernet import Fernet
from flask import jsonify

from db import db
from models import Alliance
from ps_client import PixelStarshipsApi
from ship import Ship

psa = PixelStarshipsApi()


def search_player(search=None):
    from models import Player
    if search:
        users = psa.search_user(search)
        process_users(users)

    like = '%' + (search or '') + '%'
    res = Player.query.filter(Player.name.ilike(like)).order_by(Player.trophies.desc()).limit(100).all()
    return [
        {
            'name': x.name,
            'lower': x.name.lower(),
            'trophies': x.trophies,
        }
        for x in res
    ]


def player_data(search: str = None):
    print(search)
    from models import Player, Alliance
    query = (
        db.session
        .query(Player.name, Player.trophies, Alliance.name.label('alliance_name'), Alliance.sprite_id)
        .outerjoin(Alliance, Alliance.id == Player.alliance_id)
    )
    if search:
        query = query.filter(Player.name.ilike('%' + search + '%'))
    query = (
        query
        .order_by(Player.trophies.desc())
        .limit(100)
    )
    res = query.all()
    return [
        {
            'name': x.name,
            'lower': x.name.lower(),
            'trophies': x.trophies,
            'alliance': x.alliance_name,
            'alliance_sprite': psa.sprite_data(x.sprite_id),
        }
        for x in res
    ]


def process_users(users):
    from db import db
    from models import Player

    users = list(users.items())
    for user_id, user in users:
        user['trophies'] = int(user['trophies'])
        p = Player(
            id=user_id,
            name=user['name'],
            trophies=user['trophies'],
            alliance_id=user['alliance_id'],
            last_login_at=user['last_login_at']
        )
        db.session.merge(p)

        if user['alliance_name']:
            a = Alliance(
                id=user['alliance_id'],
                name=user['alliance_name'],
                sprite_id=user['alliance_sprite_id'],
            )
            db.session.merge(a)
        db.session.commit()


FERNET_KEY = b'_R1jVlzuV7K0gpI1IMb1M5zkFWD3kt9kjp2YE-BtrTI='
FERNET = Fernet(FERNET_KEY)


def encrypt(key_data):
    return FERNET.encrypt(bytes(json.dumps(key_data), encoding='utf-8')).decode()


def decrypt(key):
    try:
        data = json.loads(FERNET.decrypt(bytes(key, encoding='utf-8')).decode())
    except Exception:
        data = {}
    return data


def _get_ship_data(name, key):
    key_data = decrypt(key)
    confirmed = name == key_data.get('name') and key_data.get('expires_at', 0) > datetime.utcnow().timestamp()
    s, u, c, r, i, g = Ship(name).summarize()
    if u:
        data = {
            'chars': c,
            'rooms': r,
            'user': u,
            'ship': s,
            'upgrades': g,
            'items': i,
            'status': 'found'
        }
        # name = u['name']  # Get the "correctly" formatted name
        data['user']['confirmed'] = True
        if not confirmed:
            data = _limit_data(data)
    else:
        data = {'status': 'not found'}
    response = {
        'data': data,
        'status': 'success'
    }
    json_response = jsonify(response)
    return json_response


def _limit_data(data):
    # Remove data that shouldn't be visible to others
    data['user']['confirmed'] = False
    data.pop('items')
    data.pop('upgrades')
    data['ship'].pop('power_gen')
    data['ship'].pop('power_use')
    data['ship'].pop('hp')
    data['ship'].pop('shield')
    data['ship'].pop('char_hp')
    data['ship'].pop('char_attack')
    data['ship'].pop('repair')
    data['ship'].pop('immunity_date')
    for r in data['rooms']:
        r.pop('armor')
        r.pop('upgradable')
        r.pop('construction')
        r.pop('defense')
        r.pop('chars')
    for c in data['chars']:
        c.pop('ability')
        c.pop('attack')
        c.pop('engine')
        c.pop('equipment')
        c.pop('fire_resist')
        c.pop('hp')
        c.pop('pilot')
        c.pop('repair')
        c.pop('research')
        c.pop('run')
        c.pop('shield')
        c.pop('stamina')
        c.pop('training')
        c.pop('training_limit')
        c.pop('upgradable')
        c.pop('walk')
        c.pop('weapon')
        c.pop('xp')
        c.pop('progression_type')
        c.pop('order')
        c.pop('character_id')
        c.pop('room_id')
    return data
