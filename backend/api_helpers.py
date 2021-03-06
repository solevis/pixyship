from operator import itemgetter

from flask import jsonify

from db import db
from models import Alliance
from models import Player
from ps_client import PixelStarshipsApi


def get_player_data(search: str = None):
    """Retrieve all players data or players found by given search."""

    pixel_starships_api = PixelStarshipsApi()

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

    results = query.all()
    return [
        {
            'name': player.name,
            'lower': player.name.lower(),
            'trophies': player.trophies,
            'alliance': player.alliance_name,
            'alliance_sprite': pixel_starships_api.sprite_data(player.sprite_id),
        }
        for player in results
    ]


def save_users(users):
    """Save users and attached alliance in database."""

    users = list(users.items())

    for user_id, user in users:
        player = Player(
            id=user_id,
            name=user['name'],
            trophies=int(user['trophies']),
            alliance_id=user['alliance_id'],
            last_login_at=user['last_login_at']
        )
        db.session.merge(player)

        if user['alliance_name']:
            alliance = Alliance(
                id=user['alliance_id'],
                name=user['alliance_name'],
                sprite_id=user['alliance_sprite_id'],
            )
            db.session.merge(alliance)

        db.session.commit()


def get_ship_data(player_name):
    """Get user and ship data from API."""

    ship, user, rooms, upgrades = summarize_ship(player_name)

    if user:
        data = {
            'rooms': rooms,
            'user': user,
            'ship': ship,
            'upgrades': upgrades,
            'status': 'found'
        }

        data['user']['confirmed'] = True
        data = limit_data(data)
    else:
        data = {
            'status': 'not found'
        }

    response = {
        'data': data,
        'status': 'success'
    }

    json_response = jsonify(response)
    return json_response


def limit_data(data):
    """Remove data that shouldn't be visible to others."""

    data['user']['confirmed'] = False
    data.pop('upgrades')
    data['ship'].pop('power_gen')
    data['ship'].pop('power_use')
    data['ship'].pop('hp')
    data['ship'].pop('shield')
    data['ship'].pop('immunity_date')

    for r in data['rooms']:
        r.pop('armor')
        r.pop('upgradable')
        r.pop('construction')
        r.pop('defense')

    return data


def summarize_ship(player_name):
    """Get ship, user, rooms and upgrade from given player name."""

    pixel_starships_api = PixelStarshipsApi()

    user_id = pixel_starships_api.get_user_id(player_name)

    if not user_id:
        return None, None, None, None

    data = pixel_starships_api.inspect_ship(user_id)

    # only seen on admin players so far
    if 'InspectShip' in data:
        return None, None, None, None

    upgrades = []
    user_data = data['ShipService']['InspectShip']['User']
    ship_data = data['ShipService']['InspectShip']['Ship']

    user = dict(
        id=user_data['@Id'],
        name=user_data['@Name'],
        sprite=pixel_starships_api.sprite_data(int(user_data['@IconSpriteId'])),
        alliance_name=user_data.get('@AllianceName'),
        alliance_sprite=pixel_starships_api.sprite_data(int(user_data.get('@AllianceSpriteId'))),
        trophies=int(user_data['@Trophy']),
        last_date=user_data['@LastAlertDate'],
    )

    ship_id = int(ship_data['@ShipDesignId'])
    immunity_date = ship_data['@ImmunityDate']

    rooms = [
        dict(
            pixel_starships_api.interiorize(int(room['@RoomDesignId']), ship_id),
            design_id=int(room['@RoomDesignId']),
            id=int(room['@RoomId']),
            row=int(room['@Row']),
            column=int(room['@Column']),
            construction=bool(room['@ConstructionStartDate']),
            upgradable=pixel_starships_api.is_room_upgradeable(int(room['@RoomDesignId']), ship_id),
        )
        for room in ship_data['Rooms']['Room']
    ]

    for room in rooms:
        if room['upgradable']:
            upgrade = pixel_starships_api.get_upgrade_room(room['design_id'])
            if upgrade:
                cost = upgrade['upgrade_cost']
                upgrades.append(
                    dict(
                        description=room['name'],
                        amount=cost,
                        currency=upgrade['upgrade_currency'],
                        seconds=upgrade['upgrade_seconds'])
                )

    ship = dict(
        pixel_starships_api.ship_map[ship_id],
        power_use=sum([room['power_use'] for room in rooms]),
        power_gen=sum([room['power_gen'] for room in rooms]),
        shield=sum([room['capacity'] for room in rooms if room['type'] == 'Shield']),
        immunity_date=immunity_date,
    )

    layout = pixel_starships_api.get_layout(rooms, ship)
    pixel_starships_api.calc_armor_effects(rooms, layout)

    return ship, user, rooms, sorted(upgrades, key=itemgetter('amount'))
