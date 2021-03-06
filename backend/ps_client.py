import datetime
import hashlib
import random
from collections import defaultdict, Counter
from typing import Tuple
from urllib.parse import quote
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import requests
from sqlalchemy import func, desc

from config import CONFIG
from db import db
from models import Device, Player, Record, Listing
from user_login_resp import TOKEN_EXPIRED_RE


def dict_get(d, *args):
    v = d or {}
    for a in args:
        v = v.get(a) or {}
    return v


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PixelStarshipsApi(metaclass=Singleton):

    min_devices = 10
    ps_asset_url = 'https://pixelstarships.s3.amazonaws.com/{}.png'
    pickle_file = 'settings.pickle'
    image_dir = 'images'
    default_server = 'http://api.pixelstarships.com'

    # A map to find the correct interior for a given race's ship
    # This fails for some rock ship cause this isn't actually how it works
    interior_map = {
        83: [83, 84, 83, 82, 1302, 561, 3134],
        1532: [1532, 1534, 1532, 1533, 1536, 1535, 3163],
        871: [871, 872, 871, 869, 870, 873, 3135],
    }

    ability_map = {
        'DamageToSameRoomCharacters': {'name': 'Gas', 'sprite': 2706},
        'HealRoomHp': {'name': 'Urgent Repair', 'sprite': 2709},
        'HealSelfHp': {'name': 'First Aid', 'sprite': 2707},
        'AddReload': {'name': 'Rush', 'sprite': 2703},
        'FireWalk': {'name': 'Fire Walk', 'sprite': 5389},
        'DamageToCurrentEnemy': {'name': 'Critical Strike', 'sprite': 2708},
        'DamageToRoom': {'name': 'Ultra Dismantle', 'sprite': 2710},
        'DeductReload': {'name': 'System Hack', 'sprite': 2704},
        'HealSameRoomCharacters': {'name': 'Healing Rain', 'sprite': 2705},
        'Freeze': {'name': 'Freeze', 'sprite': 5390},
        'SetFire': {'name': 'Arson', 'sprite': 5388},
        'Bloodlust': {'name': 'Bloodlust', 'sprite': 13866},
        'Invulnerability': {'name': 'Phase Shift', 'sprite': 13319},
        'ProtectRoom': {'name': 'Stasis Shield', 'sprite': 13320},
        'None': {'name': '', 'sprite': 110}  # Empty sprite
    }

    rarity_map = {
        'Legendary': 7,
        'Special': 6,
        'Hero': 5,
        'Epic': 4,
        'Unique': 3,
        'Elite': 2,
        'Common': 1,
    }

    rarity_color = {
        'Common': 'grey',
        'Elite': 'white',
        'Unique': 'blue',
        'Epic': 'purple',
        'Hero': 'gold',
        'Special': 'gold',
        'Legendary': 'gold',
    }

    level_xp = {
        1: 90, 2: 360, 3: 810, 4: 1440, 5: 2250, 6: 3270, 7: 4500, 8: 5940, 9: 7590, 10: 9450, 11: 11580, 12: 13980,
        13: 16650, 14: 19590, 15: 22800, 16: 26340, 17: 30210, 18: 34410, 19: 38940, 20: 43800, 21: 49020, 22: 54600,
        23: 60540, 24: 66840, 25: 73500, 26: 80550, 27: 87990, 28: 95820, 29: 104040, 30: 112650, 31: 121680,
        32: 131130, 33: 141000, 34: 151290, 35: 162000, 36: 173160, 37: 184770, 38: 196830, 39: 209340, 40: 222300
    }

    leg_level_xp = {
        1: 0, 2: 810, 3: 2160, 4: 4050, 5: 6480, 6: 9540, 7: 13230, 8: 17550, 9: 22500, 10: 28080, 11: 34440, 12: 41530,
        13: 49370, 14: 57980, 15: 67380, 16: 77590, 17: 88630, 18: 100520, 19: 113280, 20: 126930, 21: 141490,
        22: 156980, 23: 173420, 24: 190830, 25: 209230, 26: 228640, 27: 249080, 28: 270570, 29: 295230, 30: 318880,
        31: 343640, 32: 369530, 33: 396570, 34: 424780, 35: 454180, 36: 484790, 37: 516630, 38: 549720, 39: 584080,
        40: 622960
    }

    # Possible discount % to char level cost by ship level (added extra level, 12)
    ship_level_to_discount = {1: 0, 2: 0, 3: 10, 4: 10, 5: 15, 6: 15, 7: 25, 8: 30, 9: 35, 10: 35, 11: 35, 12: 35}

    char_gas = [0, 0, 25, 50, 100, 200, 500, 1000, 2000, 5000,
                10000, 15000, 20000, 30000, 40000, 55000, 67000, 80000, 95000, 110000,
                130000, 160000, 180000, 200000, 240000, 270000, 310000, 350000, 390000, 430000,
                480000, 540000, 590000, 650000, 720000, 780000, 850000, 930000, 1000000, 1100000]

    leg_char_gas = [200000, 250000, 300000, 350000, 400000, 450000, 500000, 550000, 600000, 650000, 700000,
                    750000, 800000, 850000, 900000, 950000, 1000000, 1050000, 1100000, 1150000, 1200000, 1250000,
                    1300000, 1350000, 1400000, 1450000, 1500000, 1550000, 1600000, 1650000, 1700000, 1750000,
                    1800000, 1850000, 1900000, 1950000, 2000000, 2050000, 2100000]

    setting = ('/SettingService/getlatestversion3?languagekey=en&deviceType=DeviceTypeAndroid', None)
    ship_inspect = ('/ShipService/InspectShip2?userId={user_id}&version={version}', 'ShipDesignVersion')
    user_search = ('/UserService/SearchUsers?searchString={search}', '')
    file_sprites = ('/FileService/ListSprites?version={version}', 'FileVersion')
    ship_designs = ('/ShipService/ListAllShipDesigns2?languageKey=en&version={version}', 'ShipDesignVersion')
    room_designs = ('/RoomService/ListRoomDesigns2?languageKey=en&version={version}', 'RoomDesignVersion')
    char_designs = (
        '/CharacterService/ListAllCharacterDesigns2?languageKey=en&version={version}',
        'CharacterDesignVersion'
    )
    item_designs = ('/ItemService/ListItemDesigns2?languageKey=en&version={version}', 'ItemDesignVersion')
    alliance_by_ranking = ('/AllianceService/ListAlliancesByRanking?take=100', '')
    message_marketplace = ('/MessageService/ListActiveMarketplaceMessages2?itemSubType=None&rarity=None', '')
    alliance_users = ('/AllianceService/ListUsers?allianceId={alliance_id}&skip=0&take=100', '')
    ladder_users = ('/LadderService/ListUsersByRanking?from=1&to=100', '')
    char_prestige_to = ('/CharacterService/PrestigeCharacterTo?characterDesignId={char_id}', '')
    char_prestige_from = ('/CharacterService/PrestigeCharacterFrom?characterDesignId={char_id}', '')
    collections = ('/CollectionService/ListAllCollectionDesigns?version={version}', 'CollectionDesignVersion')
    uri_research = ('/ResearchService/ListAllResearchDesigns2', None)
    market_item = ('/MarketService/ListSalesByItemDesignId?itemDesignId={item_design_id}&saleStatus={sale_status}&from={start}&to={end}', None)

    # 0 - Rock?
    # 1 - Pirate/Dark
    # 2 - Fed/Blue
    # 3 - Qtari/Gold
    # 4 - Visiri/Red
    # 5 - UFO/Green
    # 6 - Starbase

    def api_url(self, path: Tuple[str, str], server: str = None, **params):
        if path[1]:
            params['version'] = self.settings[path[1]] if hasattr(self, 'settings') else 1
        return (server or self.server) + path[0].format(**params)

    def expired(self, key):
        d = self.data_expiration[key]
        if not d:
            return True
        return datetime.datetime.utcnow().timestamp() - d > 0

    def expire_at(self, key, secs):
        self.data_expiration[key] = datetime.datetime.utcnow().timestamp() + secs

    def __init__(self):
        self._change_data = None
        self._char_map = None
        self._collection_map = None
        self._daily_data = None
        self._device_ind = 0
        self._devices = None
        self._item_map = None
        self._item_name_map = None
        self._prestige_map = {}
        self._research_map = None
        self._prices = {}
        self._room_map = None
        self._ship_map = None
        self._sprite_map = None
        self._upgrade_map = None
        self.api_calls = []
        self.data_expiration = defaultdict(lambda: None)
        self.settings = self.get_settings()

        self.server = 'http://' + self.settings['ProductionServer']

    @staticmethod
    def get_random_device():
        d = Device.query.order_by(func.random()).limit(1).first()
        return d

    def get_devices(self):
        devices = Device.query.all()
        if len(devices) < self.min_devices:
            for x in range(0, self.min_devices - len(devices)):
                k, c = self.generate_device()
                d = Device(key=k, checksum=c)
                db.session.add(d)
            db.session.commit()
            devices = Device.query.all()
        return devices

    def generate_device(self):
        k = self.create_device_key()
        c = self.md5_checksum(k)
        print('Generating new device')
        return k, c

    @staticmethod
    def create_device_key():
        h = '0123456789abcdef'
        return ''.join(
            random.choice(h)
            + random.choice('26ae')
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
            + random.choice(h)
        )

    @staticmethod
    def md5_checksum(s):
        return hashlib.md5((s + 'DeviceTypeMacsavysoda').encode('utf-8')).hexdigest()

    @property
    def devices(self):
        if not self._devices:
            self._devices = self.get_devices()
        return self._devices

    def get_device(self):
        # Get the next device
        ds = self.devices
        if self._device_ind is None:
            self._device_ind = random.randrange(len(self.devices))
        if self._device_ind >= len(ds):
            self._device_ind = 0
        d = ds[self._device_ind]
        self._device_ind += 1
        d = db.session.merge(d)
        db.session.refresh(d)

        return d

    EXPIRE_SECS = 60 * 60 * 6   # 6 hours

    @property
    def sprite_map(self):
        if not self._sprite_map or self.expired('sprite'):
            self._sprite_map = self._load_sprite_map()
            self.expire_at('sprite', self.EXPIRE_SECS)
        return self._sprite_map

    @property
    def prices(self):
        if not self._prices or self.expired('prices'):
            self._prices = self._load_prices()
            self.expire_at('prices', self.EXPIRE_SECS)
        return self._prices

    @property
    def ship_map(self):
        if not self._ship_map or self.expired('ship'):
            self._ship_map = self._load_ship_map()
            self.expire_at('ship', self.EXPIRE_SECS)
        return self._ship_map

    @property
    def room_map(self):
        if not self._room_map or self.expired('room'):
            self._room_map, self._upgrade_map = self._load_room_map()
            self.expire_at('room', self.EXPIRE_SECS)
        return self._room_map

    @property
    def research_map(self):
        if not self._research_map or self.expired('room'):
            self._research_map = self._load_research_map()
            self.expire_at('research', self.EXPIRE_SECS)
        return self._research_map

    @property
    def upgrade_map(self):
        if not self._upgrade_map or self.expired('room'):
            self._room_map, self._upgrade_map = self._load_room_map()
            self.expire_at('room', self.EXPIRE_SECS)
        return self._upgrade_map

    @property
    def char_map(self):
        if not self._char_map or self.expired('char'):
            self._char_map = self._load_char_map()
            self.expire_at('char', self.EXPIRE_SECS)
            self.fill_char_collection_data()
        return self._char_map

    @property
    def collection_map(self):
        if not self._collection_map or self.expired('collection'):
            self._collection_map = self._load_collection_map()
            self.expire_at('collection', self.EXPIRE_SECS)
            self.fill_char_collection_data()
        return self._collection_map

    def fill_char_collection_data(self):
        # When both maps are available fill in dependent info
        if self.char_map and self.collection_map:

            for c in self._char_map.values():
                # Fill in collection data
                if c['collection']:
                    c['collection_sprite'] = self.collection_map[c['collection']]['icon_sprite']
                    c['collection_name'] = self.collection_map[c['collection']]['name']

            for k, v in self._collection_map.items():
                # Fill in chars
                v['chars'] = [c for c in self.char_map.values() if c['collection'] == k]

    @property
    def item_map(self):
        if not self._item_map or self.expired('item'):
            self._item_map = self._load_item_map()
            self._item_name_map = {v['name']: k for k, v in self._item_map.items()}
            self.expire_at('item', self.EXPIRE_SECS)
        return self._item_map

    @property
    def item_name_map(self):
        if not self._item_map or self.expired('item'):
            self._item_map = self._load_item_map()
            self._item_name_map = {v['name']: k for k, v in self._item_map.items()}
            self.expire_at('item', self.EXPIRE_SECS)
        return self._item_name_map

    @property
    def daily_data(self):
        if not self._daily_data or self.expired('daily'):
            self._daily_data = self.get_dailies()
            self.expire_at('daily', 60 * 5)
        return self._daily_data

    @property
    def change_data(self):
        if not self._change_data or self.expired('change'):
            self._change_data = self.get_changes()
            self.expire_at('change', 60 * 5)
        return self._change_data

    def prestige_data(self, char_id):
        # if ((char_id not in self._prestige_map)
        #         or (self._prestige_map[char_id]['expires_at'] < datetime.datetime.now())):

        self._prestige_map[char_id] = self.get_prestige_data(char_id)
        return self._prestige_map[char_id]

    def sprite_data(self, sprite_id):
        if not sprite_id:
            return {}
        if isinstance(sprite_id, str):
            sprite_id = int(sprite_id)
        assert isinstance(sprite_id, int)

        s = self.sprite_map.get(sprite_id)
        if not s:
            return {}

        return {
            'source': s['image_file'],
            'x': s['x'],
            'y': s['y'],
            'width': s['width'],
            'height': s['height'],
        }

    CALLS_PER_PERIOD = 50
    SECONDS_PER_PERIOD = 10

    def _rate_limit(self):
        pass
        # # Wait until the limit.  It was suggested that there is a per device rate limit of roughly 1 call per second.
        # while len(self.api_calls) >= self.CALLS_PER_PERIOD:
        #     # remove records older than now
        #     now_point = datetime.datetime.now()
        #
        #     self.api_calls = list(filter(lambda d: d > now_point, self.api_calls))
        #     if len(self.api_calls) >= self.CALLS_PER_PERIOD:
        #         print('... api wait, would have waited')
        #         time.sleep(1)
        #
        # self.api_calls.append(datetime.datetime.now() + datetime.timedelta(seconds=self.SECONDS_PER_PERIOD))

    def call(self, url, access=False):
        final_url = url
        if access:
            d = self.get_device()
            final_url = url + d.access_token_param()

        # self._rate_limit()
        r = requests.get(final_url)

        if TOKEN_EXPIRED_RE.search(r.text):
            # This only happens for a credentialed request
            d.cycle_token()
            final_url = url + d.access_token_param()
            # self._rate_limit()
            r = requests.get(final_url)

        if r.encoding is None:
            r.encoding = 'utf-8'
        return r

    def inspect_ship(self, user_id):
        # Check the cache
        url = self.api_url(self.ship_inspect, user_id=user_id)
        r = self.call(url, True)
        root = ElementTree.fromstring(r.text)
        return etree_to_dict(root)

    # TODO: MOVE
    def is_room_upgradeable(self, room_design_id, ship_design_id):
        upgrade_id = self.upgrade_map.get(room_design_id)
        if not upgrade_id:
            return False

        req_ship_level = self.room_map[upgrade_id]['min_ship_level']
        ship_level = self.ship_map[ship_design_id]['level']

        return req_ship_level <= ship_level

    # TODO: MOVE
    @staticmethod
    def get_layout(rooms, ship):
        layout = [[0] * ship['columns'] for _ in range(ship['rows'])]
        for r in rooms:
            x = r['column']
            y = r['row']
            i = r['id']
            for ox in range(r['width']):
                for oy in range(r['height']):
                    layout[y + oy][x + ox] = i
        return layout

    # TODO: MOVE
    def calc_armor_effects(self, rooms, layout):
        for r in rooms:
            armor = 0
            if r['power_gen'] + r['power_use'] > 0:
                # Check left, right, top and bottom side
                x = r['column']
                y = r['row']
                w = r['width']
                h = r['height']
                for ox in range(w):
                    armor += self.safe_get_armor(layout, rooms, x + ox, y - 1)
                    armor += self.safe_get_armor(layout, rooms, x + ox, y + h)
                for oy in range(h):
                    armor += self.safe_get_armor(layout, rooms, x - 1, y + oy)
                    armor += self.safe_get_armor(layout, rooms, x + w, y + oy)
            r['armor'] = armor

    # TODO: MOVE
    @staticmethod
    def safe_get_armor(layout, rooms, x, y):
        neighbor = layout[y][x]
        if not neighbor:
            return 0
        room = [r for r in rooms if r['id'] == neighbor][0]
        if room['type'] == 'Wall':
            return room['capacity']
        return 0

    def interiorize(self, room_id, ship_id):
        # Convert rooms to the correct interior
        room = self.get_object('Room', room_id)

        if room['type'] in ('Wall', 'Lift'):
            ship = self.get_object('Ship', ship_id)

            if room['sprite']['source'] in self.interior_map:
                # Make a new sprite in a new room to keep from overwriting original data
                room = room.copy()
                sprite = room['sprite'].copy()
                sprite['source'] = self.interior_map[room['sprite']['source']][ship['race']]
                room['sprite'] = sprite

        return room

    stat_map = {
        'hp': '@HpImprovement',
        'pilot': '@PilotImprovement',
        'attack': '@AttackImprovement',
        'repair': '@RepairImprovement',
        'weapon': '@WeaponImprovement',
        'shield': '@ShieldImprovement',
        'science': '@ScienceImprovement',
        'engine': '@EngineImprovement',
        'research': None,
        'ability': '@AbilityImprovement'
    }

    # These could be treated as 0 start 0 end stats
    enhance_stats = {
        'fireresistance': 'fire_resist',
        'stamina': 'stamina',
        'resurrectskill': 'resurrect'
    }

    def _verification_data(self, data):
        user_d = data['ShipService']['InspectShip']['User']
        ship_d = data['ShipService']['InspectShip']['Ship']
        name = user_d['@Name']
        items = sorted(
            [
                dict(
                    self.item_map[int(x['@ItemDesignId'])],
                    quantity=int(x['@Quantity']),
                )
                for x in ship_d['Items']['Item']
                if int(x['@Quantity']) > 0
            ], key=lambda x: (self.item_type[x['type']], x['name'])
        )
        minerals = [i['quantity'] for i in items if i['type'] == 'Mineral'] or [0]
        gas = [i['quantity'] for i in items if i['type'] == 'Gas'] or [0]
        minerals = minerals[0]
        gas = gas[0]
        return name, minerals, gas

    # TODO: MOVE
    def get_verification_data(self, name, user_id=None):
        # data = self._ship_from_cache(name)
        if True:
            user_id = user_id or self.get_user_id(name)
            if user_id:
                data = self.inspect_ship(user_id)
                return (*self._verification_data(data), user_id)

        return None, None, None, None

    def search_user(self, search):
        search = quote(search)
        url = self.api_url(self.user_search, search=search)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        users = etree_to_dict(root)['UserService']['SearchUsers']['Users']
        user_list = users['User'] if users else []
        return self._users_from_xml(user_list)

    @staticmethod
    def get_user_id(search_name):
        # Given a name return the user_id.  This should only be an exact match.
        res = Player.query.filter(Player.name.ilike(search_name)).limit(1).first()
        if res:
            return res.id
        return None

    def get_upgrade_room(self, room_design_id):
        upgrade_id = self.upgrade_map[room_design_id]
        if upgrade_id:
            return self.room_map[upgrade_id]
        return None

    # TODO: Is this even used?
    def _load_sprite_map(self):
        url = self.api_url(self.file_sprites)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        data = etree_to_dict(root)['FileService']['ListSprites']['Sprites']['Sprite']
        return {
            int(d['@SpriteId']): {
                'image_file': int(d['@ImageFileId']),
                'x': int(d['@X']),
                'y': int(d['@Y']),
                'width': int(d['@Width']),
                'height': int(d['@Height']),
                'sprite_key': d['@SpriteKey'],
            }
            for d in data
        }

    @staticmethod
    def _load_prices():
        sql = """
            SELECT item_id
                , currency
                , SUM(amount) as count
                , percentile_disc(.25) WITHIN GROUP (ORDER BY price/amount) AS p25
                , percentile_disc(.5) WITHIN GROUP (ORDER BY price/amount) AS p50
                , percentile_disc(.75) WITHIN GROUP (ORDER BY price/amount) AS p75
            FROM listing
            WHERE amount > 0
            {}
            GROUP BY item_id, currency
        """.format('' if CONFIG.get('DEV_MODE') else "  AND sale_at > (now() - INTERVAL '48 HOURS')")
        res = db.session.execute(sql).fetchall()
        data = defaultdict(dict)
        for r in res:
            data[r[0]][r[1]] = {
                'count': r[2],
                'p25': r[3],
                'p50': r[4],
                'p75': r[5],
            }
        return data

    @staticmethod
    def get_item_prices(item_id):
        sql = """
            SELECT item_id
                , item_name
                , currency
                , sale_at::DATE AS sale_date
                , SUM(amount) AS count
                , percentile_disc(.25) WITHIN GROUP (ORDER BY price/amount) AS p25
                , percentile_disc(.5) WITHIN GROUP (ORDER BY price/amount) AS p50
                , percentile_disc(.75) WITHIN GROUP (ORDER BY price/amount) AS p75
            FROM listing
            WHERE item_id = :item_id
                AND amount > 0
                AND sale_at::DATE >= now() - '6 months'::INTERVAL
            GROUP BY item_id, item_name, currency, sale_at::DATE
            ORDER BY item_id, item_name, currency, sale_at::DATE
            """
        res = db.session.execute(sql, {'item_id': item_id}).fetchall()
        prices = defaultdict(lambda: defaultdict(dict))

        for r in res:
            prices[r[2]][str(r[3])] = {
                'count': r[4],
                'p25': r[5],
                'p50': r[6],
                'p75': r[7],
            }
        p = {k: dict(v) for k, v in prices.items()}
        data = {
            'id': item_id,
            'prices': p,
        }
        return data

    def update_ship_data(self):
        url = self.api_url(self.ship_designs)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get('ShipDesignId')
            Record.update_data('ship', record_id, c)

    def _load_ship_map(self):
        records = Record.query.filter_by(type='ship', current=True).all()
        data = {}
        for r in records:
            x = ElementTree.fromstring(r.data).attrib
            data[r.type_id] = {
                'id': r.type_id,
                'name': x['ShipDesignName'],
                'description': x['ShipDescription'],
                'level': int(x['ShipLevel']),
                'hp': int(x['Hp']),
                'repair_time': int(x['RepairTime']),
                'exterior_sprite': self.sprite_data(int(x['ExteriorSpriteId'])),
                'interior_sprite': self.sprite_data(int(x['InteriorSpriteId'])),
                'logo_sprite': self.sprite_data(int(x['LogoSpriteId'])),
                'mini_ship_sprite': self.sprite_data(int(x['MiniShipSpriteId'])),
                'frame_sprite': self.sprite_data(int(x['RoomFrameSpriteId'])),
                'left_door_sprite': self.sprite_data(int(x['DoorFrameLeftSpriteId'])),
                'right_door_sprite': self.sprite_data(int(x['DoorFrameRightSpriteId'])),
                'rows': int(x['Rows']),
                'columns': int(x['Columns']),
                'race': int(x['RaceId']),
                'mask': x['Mask'],
                'mineral_cost': x['MineralCost'],
                'starbux_cost': x['StarbuxCost'],
                'mineral_capacity': x['MineralCapacity'],
                'gas_capacity': x['GasCapacity'],
                'equipment_capacity': x['EquipmentCapacity'],
                'ship_type': x['ShipType'],
            }
        return data

    def update_data(self, uri, attr, record_name):
        """Update data and save records
        """
        url = self.api_url(uri)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get(attr)
            Record.update_data(record_name, record_id, c)

    def _load_research_map(self):
        records = Record.query.filter_by(type='research', current=True).all()
        data = {}
        for r in records:
            x = ElementTree.fromstring(r.data).attrib
            data[r.type_id] = {
                **x,
                'id': r.type_id,
                'name': x['ResearchName'],
                'description': x['ResearchDescription'],
                'gas_cost': int(x['GasCost']),
                'starbux_cost': int(x['StarbuxCost']),
                'lab_level': int(x['RequiredLabLevel']),
                'research_seconds': int(x['ResearchTime']),
                'logo_sprite': self.sprite_data(x['LogoSpriteId']),
                'sprite': self.sprite_data(x['ImageSpriteId']),
                'required_research_id': int(x['RequiredResearchDesignId']),
                'research_type': x['ResearchDesignType'],
                # Argument="0"
                # AvailabilityMask="3"
                # RequiredItemDesignId="0"/>
            }
        for d in data.values():
            d['required_research_name'] = (
                data[d['required_research_id']]['name']
                if d['required_research_id']
                else ''
            )
        return data

    @staticmethod
    def price_from_pricestring(pricestring):
        if not pricestring:
            return 0, None

        parts = pricestring.split(':')
        return int(parts[1]), parts[0]

    def update_room_data(self):
        url = self.api_url(self.room_designs)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get('RoomDesignId')
            Record.update_data('room', record_id, c)

    def _load_room_map(self):
        records = Record.query.filter_by(type='room', current=True).all()
        data = {}
        for r in records:
            e = ElementTree.fromstring(r.data)
            x = e.attrib
            m_list = list(e.iter('MissileDesign'))
            m = m_list[0].attrib if m_list else None
            data[r.type_id] = {
                'id': r.type_id,
                'name': x['RoomName'],
                'short_name': x['RoomShortName'],
                'type': x['RoomType'],
                'level': int(x['Level']),
                'capacity': int(x['Capacity']),
                'height': int(x['Rows']),
                'width': int(x['Columns']),
                'sprite': self.sprite_data(int(x['ImageSpriteId'])),
                'construction_sprite': self.sprite_data(int(x['ConstructionSpriteId'])),
                'power_use': int(x['MaxSystemPower']),
                'power_gen': int(x['MaxPowerGenerated']),
                'min_ship_level': int(x['MinShipLevel']),
                'upgrade_from_id': int(x['UpgradeFromRoomDesignId']),
                'defense': int(x['DefaultDefenceBonus']),
                'reload': int(x['ReloadTime']),
                'refill_cost': int(x['RefillUnitCost']),
                'show_frame': x['RoomType'] not in ('Lift', 'Wall', 'Corridor'),
                'upgrade_cost': self.price_from_pricestring(x['PriceString'])[0],
                'upgrade_currency': self.price_from_pricestring(x['PriceString'])[1],
                'upgrade_seconds': int(x['ConstructionTime']),
                'description': x['RoomDescription'],
                'system_damage': float(m['SystemDamage']) if m else 0,
                'hull_damage': float(m['HullDamage']) if m else 0,
                'character_damage': float(m['CharacterDamage']) if m else 0,
                'manufacture_type': x['ManufactureType'],
            }

        upgrade_map = {
            v['upgrade_from_id']: k for
            k, v in data.items()
        }
        return data, upgrade_map

    @staticmethod
    def int_range(values, start_key, end_key):
        start = int(values[start_key])
        end = int(values[end_key])
        return start, end

    @staticmethod
    def float_range(values, start_key, end_key):
        start = float(values.get(start_key, 0))
        end = float(values.get(end_key, 0))
        return start, end

    equipment_slots = ['Head', 'Body', 'Leg', 'Hand', 'Accessory']

    def get_equipment_slots(self, char_def):
        em = int(char_def['EquipmentMask'])
        output = [int(x) for x in '{:05b}'.format(em)]
        slots = {self.equipment_slots[4 - i]: {} for i, b in enumerate(output) if b}
        return slots

    def update_char_data(self):
        url = self.api_url(self.char_designs)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get('CharacterDesignId')
            Record.update_data('char', record_id, c)

    def _load_char_map(self):
        records = Record.query.filter_by(type='char', current=True).all()
        data = {}
        for r in records:
            x = ElementTree.fromstring(r.data)
            a = x.attrib
            data[r.type_id] = {
                'name': a['CharacterDesignName'],
                'id': r.type_id,
                'sprite': self.sprite_data(int(a['ProfileSpriteId'])),
                'head_sprite': self.sprite_data(int(x[0][0].attrib['StandardSpriteId'])),
                'body_sprite': self.sprite_data(int(x[0][1].attrib['StandardSpriteId'])),
                'leg_sprite': self.sprite_data(int(x[0][2].attrib['StandardSpriteId'])),
                'rarity': a['Rarity'].lower(),     # Sprites for gems are 1593. 1594
                'rarity_order': self.rarity_map[a['Rarity']],
                'hp': self.int_range(a, 'Hp', 'FinalHp'),
                'pilot': self.float_range(a, 'Pilot', 'FinalPilot'),
                'attack': self.float_range(a, 'Attack', 'FinalAttack'),
                'repair': self.float_range(a, 'Repair', 'FinalRepair'),
                'weapon': self.float_range(a, 'Weapon', 'FinalWeapon'),
                'shield': self.float_range(a, 'Shield', 'FinalShield'),
                'engine': self.float_range(a, 'Engine', 'FinalEngine'),
                'research': self.float_range(a, 'Research', 'FinalResearch'),
                'science': self.float_range(a, 'Science', 'FinalScience'),
                'ability': self.float_range(a, 'SpecialAbilityArgument', 'SpecialAbilityFinalArgument'),
                'special_ability': self.ability_map.get(a['SpecialAbilityType'], {'name': ''})['name'],
                'ability_sprite':
                    self.sprite_data(self.ability_map.get(a['SpecialAbilityType'], {'sprite': 110})['sprite']),
                'fire_resist': int(a['FireResistance']),
                'resurrect': 0,
                'walk': int(a['WalkingSpeed']),
                'run': int(a['RunSpeed']),
                'training_limit': int(a['TrainingCapacity']),
                'progression_type': a['ProgressionType'],
                'equipment': self.get_equipment_slots(a),
                'collection': int(a['CollectionDesignId']),
                'collection_sprite': None,
                'collection_name': '',
            }

        # Computed properties
        data = {
            k: dict(v, width=max(v['head_sprite']['width'], v['body_sprite']['width'], v['leg_sprite']['width']))
            for k, v in data.items()
        }
        return data

    item_type = {
        'Mineral': 1,
        'Gas': 2,
        'Missile': 3,
        'Craft': 4,
        'Android': 5,
        'Equipment': 6,
    }

    slot_map = {
        'None': None,
        'EquipmentHead': 'Head',
        'EquipmentWeapon': 'Hand',
        'EquipmentBody': 'Body',
        'EquipmentLeg': 'Leg',
        'EquipmentAccessory': 'Accessory',
        'MineralPack': 'Mineral Pack',
        'GasPack': 'Gas Pack',
        'InstantPrize': 'Instant Prize',
    }

    enhance_map = {
        'FireResistance': 'Fire Resistance',
        'None': None
    }

    @staticmethod
    def parse_recipe(item_list_string, items):
        o = []
        if item_list_string:
            ingredients = [i.split('x') for i in item_list_string.split('|')]
            for i in ingredients:
                item = items.get(int(i[0]))
                if item:
                    line = {
                        'count': int(i[1]),
                        'name': item['name'],
                        'sprite': item['sprite'],
                    }
                    o.append(line)
        return o

    def update_collection_data(self):
        url = self.api_url(self.collections)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get('CollectionDesignId')
            Record.update_data('collection', record_id, c)

    def _load_collection_map(self):
        records = Record.query.filter_by(type='collection', current=True).all()
        data = {}
        for r in records:
            x = ElementTree.fromstring(r.data).attrib
            x.update({
                'name': x['CollectionName'],
                'min': int(x['MinCombo']),
                'max': int(x['MaxCombo']),
                'base_enhancement': int(x['BaseEnhancementValue']),
                'sprite': self.sprite_data(int(x['SpriteId'])),
                'step_enhancement': int(x['StepEnhancementValue']),
                'icon_sprite': self.sprite_data(int(x['IconSpriteId'])),
                'chars': [],
            })
            data[r.type_id] = x

        return data

    def update_item_data(self):
        url = self.api_url(self.item_designs)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        for c in root[0][0]:
            record_id = c.get('ItemDesignId')
            Record.update_data('item', record_id, c, ['FairPrice', 'MarketPrice'])

    def _load_item_map(self):
        records = Record.query.filter_by(type='item', current=True).all()
        data = {}
        for r in records:
            x = ElementTree.fromstring(r.data).attrib
            data[r.type_id] = {
                'name': x['ItemDesignName'],
                'description': x['ItemDesignDescription'],
                'sprite': self.sprite_data(int(x['ImageSpriteId'])),
                'slot': self.slot_map.get(x['ItemSubType'], x['ItemSubType']),
                'enhancement': x.get('EnhancementType').lower(),
                'disp_enhancement': self.enhance_map.get(x['EnhancementType'], x['EnhancementType']),
                'bonus': float(x.get('EnhancementValue')),
                'type': x.get('ItemType'),
                'rarity': x.get('Rarity').lower(),
                'ingredients': x['Ingredients'],
                'market_price': int(x['MarketPrice']),
                'fair_price': int(x['FairPrice']),
                'prices': self.prices.get(int(x['ItemDesignId'])),
                'id': r.type_id,
            }

        # Second pass required for self references
        for d in data.values():
            d['recipe'] = self.parse_recipe(d['ingredients'], data)

        return data

    def get_alliances(self):
        # Get the top 100 alliances
        url = self.api_url(self.alliance_by_ranking)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        alliances = etree_to_dict(root)['AllianceService']['ListAlliancesByRanking']['Alliances']['Alliance']

        return {
            int(x['@AllianceId']): {
                'name': x['@AllianceName'],
            }
            for x in alliances
        }

    def get_item_sales(self, item, max_sale_id = 0):
        """Download sales for given item from PSS API."""
        sales = {}

        # offset, API returns sales only by 20 by 20
        start = 0
        end = 20

        max_sale_id_reached = False
        while "sale_id from API not equal to given max_sale_id":
            url = self.api_url(self.market_item,
                               item_design_id=int(item['ItemDesignId']),
                               sale_status='Sold',
                               start=start,
                               end=end
                               )
            request = self.call(url)
            root = ElementTree.fromstring(request.text)

            # parse HTTP body as XML and find sales nodes
            sale_nodes = root.find('.//Sales')

            # no more sales available
            if len(sale_nodes) == 0:
                break

            for sale_node in sale_nodes:
                sale_id = int(sale_node.get('SaleId', '0'))

                sale = {
                    'sale_at': sale_node.get('StatusDate', '0'),
                    'currency': sale_node.get('CurrencyType', '0'),
                    'price': int(sale_node.get('CurrencyValue', '0')),
                    'user_id': int(sale_node.get('BuyerShipId', '0')),
                    'amount': int(sale_node.get('Quantity', '0')),
                    'item_name': item['ItemDesignName'],
                    'item_id': int(item['ItemDesignId']),
                }

                if sale_id > max_sale_id:
                    sales[sale_id] = sale
                else:
                    max_sale_id_reached = True
                    break

            if max_sale_id_reached:
                break

            # next page
            start += 20
            end += 20

        return sales

    def get_market_data(self, item):
        # get max sale_id to retrieve only new sales
        max_sale_id_result = Listing.query \
            .filter(Listing.item_id == int(item['ItemDesignId'])) \
            .order_by(desc(Listing.id)) \
            .limit(1) \
            .first()

        if max_sale_id_result is not None:
            max_sale_id = max_sale_id_result.id if max_sale_id_result.id is not None else 0
        else:
            max_sale_id = 0

        sales = self.get_item_sales(item, max_sale_id)
        return sales

    def get_alliance_users(self, alliance_id):
        # Get the top 100 alliances
        url = self.api_url(self.alliance_users, alliance_id=alliance_id)

        r = self.call(url, True)
        try:
            root = ElementTree.fromstring(r.text)
            users = etree_to_dict(root)['AllianceService']['ListUsers']['Users']['User']
        except UnboundLocalError as e:
            print('UnboundLocalError --------------------------------------------------------------------------')
            print(e)
            print('--------------------------------------------------------------------------------------------')
            print(r.text)
            print('--------------------------------------------------------------------------------------------')
            raise
        except Exception as e:
            print('--------------------------------------------------------------------------------------------')
            print(e)
            print('--------------------------------------------------------------------------------------------')
            print(r.text)
            print('--------------------------------------------------------------------------------------------')
            raise

        return self._users_from_xml(users)

    def get_top_users(self):
        # Get the top 100 players
        url = self.api_url(self.ladder_users)

        r = self.call(url, True)
        root = ElementTree.fromstring(r.text)
        users = etree_to_dict(root)['LadderService']['ListUsersByRanking']['Users']['User']

        return self._users_from_xml(users)

    @staticmethod
    def _users_from_xml(users):
        if not isinstance(users, list):
            users = [users]
        return {
            int(x['@Id']): {
                'name': x['@Name'],
                'trophies': int(x['@Trophy']),
                'alliance_id': int(x['@AllianceId']),
                'last_login_at': x['@LastLoginDate'],
                'alliance_name': x.get('@AllianceName'),
                'alliance_sprite_id': int(x['@AllianceSpriteId']),
            }
            for x in users
        }

    def parse_items(self, item_list_string):
        items = [i.split('x') for i in item_list_string.split('|')]
        o = [
            {
                'count': int(i[1]),
                'type': 'Item',
                'object': self.item_map[int(i[0])],
            }
            for i in items
        ]
        return o

    @staticmethod
    def parse_costs(cost_list_string):
        costs = [i.split(':') for i in cost_list_string.split('|')]
        o = [
            {'currency': c[0], 'price': int(c[1])}
            for c in costs
        ]
        return o

    def parse_cargo(self, item_list_string, cost_list_string):
        items = self.parse_items(item_list_string)
        prices = self.parse_costs(cost_list_string)
        cargo = [self._format_daily_offer('Cargo', [i], p) for i, p in zip(items, prices)]
        return cargo

    def get_settings(self):
        url = self.api_url(self.setting, server='http://api.pixelstarships.com')
        r = self.call(url)
        try:
            root = ElementTree.fromstring(r.text)
        except ParseError:
            # Servers are always supposed to return something valid, but don't always
            url = self.api_url(self.setting, server='http://api2.pixelstarships.com')
            r = self.call(url)
            root = ElementTree.fromstring(r.text)

        settings = root[0][0].attrib
        fixed_url = self.api_url(self.setting, server='http://' + settings['ProductionServer'])

        if fixed_url != url:
            r = self.call(fixed_url)
            root = ElementTree.fromstring(r.text)
            settings = root[0][0].attrib

        return settings

    def get_prestige_data(self, char_id):
        to_url = self.api_url(self.char_prestige_to, char_id=char_id)
        r = self.call(to_url)
        root = ElementTree.fromstring(r.text)
        prestiges = dict_get(
            etree_to_dict(root), 'CharacterService', 'PrestigeCharacterTo', 'Prestiges', 'Prestige'
        ) or []
        if not isinstance(prestiges, list):
            prestiges = list((prestiges,))
        p_to = list(set(
            tuple(sorted([int(x['@CharacterDesignId1']), int(x['@CharacterDesignId2'])]))
            for x in prestiges
        ))

        # Determine which chars to group
        temp_to = p_to
        grouped_to = defaultdict(list)
        while len(temp_to):
            c = Counter([x for y in temp_to for x in y])
            [(most_id, _)] = c.most_common(1)
            # find all the pairs with the id
            new_to = []

            for pair in temp_to:
                if most_id == pair[0]:
                    grouped_to[most_id].append(pair[1])
                elif most_id == pair[1]:
                    grouped_to[most_id].append(pair[0])
                else:
                    new_to.append(pair)

            temp_to = new_to

        from_url = self.api_url(self.char_prestige_from, char_id=char_id)
        r = self.call(from_url)
        root = ElementTree.fromstring(r.text)
        prestiges = dict_get(
            etree_to_dict(root), 'CharacterService', 'PrestigeCharacterFrom', 'Prestiges', 'Prestige'
        ) or []
        p_from = [[int(x['@CharacterDesignId2']), int(x['@ToCharacterDesignId'])] for x in prestiges]

        grouped_from = defaultdict(list)
        for r in p_from:
            grouped_from[r[1]].append(r[0])

        all_ids = list(set([i for prestige in p_to for i in prestige] + [i for prestige in p_from for i in prestige] + [char_id]))
        all_chars = [self.char_map[i] for i in all_ids]

        return {
            'to': grouped_to,
            'from': grouped_from,
            'chars': all_chars,
            'expires_at': datetime.datetime.now() + datetime.timedelta(minutes=1)
        }

    @staticmethod
    def _format_daily_offer(desc, items, cost=None, details=None, expires=None):
        return {
            'description': desc,
            'objects': items,
            'cost': cost,
            'details': details,
            'expires': expires,
        }

    @staticmethod
    def _format_object(count, type_str, object_str):
        return {
            'count': count,
            'type': type_str,
            'object': object_str,
        }

    @staticmethod
    def _format_price(amount, currency):
        return {
            'price': amount,
            'currency': currency,
        }

    type_name_field = {
        'ship': 'ShipDesignName',
        'room': 'RoomName',
        'char': 'CharacterDesignName',
        'item': 'ItemDesignName',
        'collection': 'CollectionDesignId',
    }

    def get_changes(self):
        sql = """
            SELECT *
            FROM (
                    SELECT DISTINCT ON (c.id)
                        c.id,
                        c.type,
                        c.type_id,
                        c.data,
                        c.created_at,
                        o.data as old_data
                    FROM record c
                        LEFT JOIN record o ON o.type = c.type AND o.type_id = c.type_id AND o.current = FALSE
                    WHERE c.current = TRUE
                        AND (o.id IS NOT NULL
                            OR c.created_at > '2018-10-8 4:00')
                        AND c.type IN ('item', 'ship', 'char', 'room')
                    ORDER BY c.id, o.created_at DESC
                ) AS sub
            ORDER BY created_at DESC
            LIMIT 500
        """

        result = db.session.execute(sql).fetchall()
        changes = []

        for record in result:
            record_data = ElementTree.fromstring(record['data']).attrib
            sprite = self.get_record_sprite(record['type'], record['type_id'])

            change = {
                'type': record['type'],
                'id': record['type_id'],
                'name': record_data[self.type_name_field[record['type']]],
                'changed_at': record['created_at'],
                'data': record['data'],
                'old_data': record['old_data'],
                'change_type': 'Changed' if record['old_data'] else 'New',
                'sprite': sprite
            }

            # if change's a Character, get all infos of the crew
            if record['type'] == 'char':
                change['char'] = self.char_map[record['type_id']]

            changes.append(change)

        return changes

    def get_dailies(self):
        # Get settings service data, sales, motd...
        url = self.api_url(self.setting)
        r = self.call(url)
        root = ElementTree.fromstring(r.text)
        d = etree_to_dict(root)['SettingService']['GetLatestSetting']['Setting']
        offers = [
            self._format_daily_offer(
                'Shop',
                [self._format_object(
                    1,
                    d['@LimitedCatalogType'],
                    self.get_object(d['@LimitedCatalogType'], int(d['@LimitedCatalogArgument']))
                )],
                self._format_price(d['@LimitedCatalogCurrencyAmount'], d['@LimitedCatalogCurrencyType']),
                [
                    '{} left'.format(d['@LimitedCatalogQuantity']),
                    '{} max'.format(d['@LimitedCatalogMaxTotal']),
                ],
                d['@LimitedCatalogExpiryDate']
            ),
            self._format_daily_offer(
                'Mineral Crew',
                [self._format_object(1, 'Character', self.get_object('Character', int(d['@CommonCrewId'])))],
            ),
            self._format_daily_offer(
                'Starbux Crew',
                [self._format_object(1, 'Character', self.get_object('Character', int(d['@HeroCrewId'])))],
            ),
            self._format_daily_offer(
                'Reward',
                [self._format_object(
                    int(d['@DailyRewardArgument']),
                    'Currency',
                    self._format_price(int(d['@DailyRewardArgument']), d['@DailyRewardType'])
                )] + self.parse_items(d['@DailyItemRewards']),
            ),
        ] + self.parse_cargo(d['@CargoItems'], d['@CargoPrices'])
        dailes = {
            'news': {
                'news': d['@News'],
                'news_date': d['@NewsUpdateDate'],
                'maintenance': d['@MaintenanceMessage'],
                'tournament_news': d['@TournamentNews'],
            },
            'offers': offers,
        }
        return dailes

    def get_object(self, object_type, oid, reload_on_err=True):
        try:
            if object_type == 'Item':
                return self.item_map[oid]
            if object_type == 'Character':
                return self.char_map[oid]
            if object_type == 'Room':
                return self.room_map[oid]
            if object_type == 'Ship':
                return self.ship_map[oid]
        except KeyError:
            print('KeyErrors')
            # Happens when there's new things, reload
            if reload_on_err:
                self._item_map = None
                self._char_map = None
                self._item_map = None
                self._ship_map = None
                return self.get_object(object_type, oid, False)
            else:
                raise

    def get_record_sprite(self, record_type, record_id, reload_on_error=True):
        try:
            if record_type == 'item':
                return self.item_map[record_id]['sprite']
            if record_type == 'char':
                return self.char_map[record_id]['sprite']
            if record_type == 'room':
                return self.room_map[record_id]['sprite']
            if record_type == 'ship':
                return self.ship_map[record_id]['mini_ship_sprite']
        except KeyError:
            # Happens when there's new things, reload
            if reload_on_error:
                self._item_map = None
                self._char_map = None
                self._room_map = None
                self._ship_map = None
                return self.get_record_sprite(record_type, record_id, False)
            else:
                raise

    def get_device_token(self, device_key, device_checksum):
        url = (
            self.server + '/UserService/DeviceLogin8'
            '?deviceKey={}'
            '&isJailBroken=false'
            '&checksum={}'
            '&deviceType=DeviceTypeMac'
            '&languagekey=en'
            '&advertisingKey=%22%22'.format(device_key, device_checksum)
        )

        r = requests.post(url)
        root = ElementTree.fromstring(r.text)

        return root.find('UserLogin').attrib['accessToken']


def etree_to_dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def printd(d):
    for k, v in d.items():
        print(k, ':\t', v)
