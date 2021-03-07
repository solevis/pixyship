import datetime
import hashlib
import random
import re
from collections import defaultdict, Counter
from typing import Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import requests
from sqlalchemy import desc

from api_errors import TOKEN_EXPIRED_REGEX
from config import CONFIG
from db import db
from models import Device, Player, Record, Listing
from utils import etree_to_dict, dict_get, float_range, int_range


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PixelStarshipsApi(metaclass=Singleton):
    MIN_DEVICES = 10
    PSS_SPRITES_URL = 'https://pixelstarships.s3.amazonaws.com/{}.png'
    PSS_API_DEFAULT_URL = 'http://api.pixelstarships.com'

    # A map to find the correct interior for a given race's ship
    # This fails for some rock ship cause this isn't actually how it works
    RACE_SPECIFIC_SPRITE_MAP = {
        83: [83, 84, 83, 82, 1302, 561, 3134],  # basic lifts
        1532: [1532, 1534, 1532, 1533, 1536, 1535, 3163],  # endgame lifts
        871: [871, 872, 871, 869, 870, 873, 3135],  # armors
    }

    ABILITY_MAP = {
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

    RARITY_MAP = {
        'Legendary': 7,
        'Special': 6,
        'Hero': 5,
        'Epic': 4,
        'Unique': 3,
        'Elite': 2,
        'Common': 1,
    }

    RARITY_COLOR = {
        'Common': 'grey',
        'Elite': 'white',
        'Unique': 'blue',
        'Epic': 'purple',
        'Hero': 'gold',
        'Special': 'gold',
        'Legendary': 'gold',
    }

    SETTING_URL = ('/SettingService/getlatestversion3?languagekey=en&deviceType=DeviceTypeAndroid', None)
    INSPECT_SHIP_URL = ('/ShipService/InspectShip2?userId={user_id}&version={version}', 'ShipDesignVersion')
    LIST_SPRITES_URL = ('/FileService/ListSprites?version={version}', 'FileVersion')
    SHIP_DESIGNS_URL = ('/ShipService/ListAllShipDesigns2?languageKey=en&version={version}', 'ShipDesignVersion')
    ROOM_DESIGNS_URL = ('/RoomService/ListRoomDesigns2?languageKey=en&version={version}', 'RoomDesignVersion')
    CHAR_DESIGNS_URL = (
        '/CharacterService/ListAllCharacterDesigns2?languageKey=en&version={version}',
        'CharacterDesignVersion'
    )
    ITEM_DESIGNS_URL = ('/ItemService/ListItemDesigns2?languageKey=en&version={version}', 'ItemDesignVersion')
    ALLIANCES_BY_RANKING_URL = ('/AllianceService/ListAlliancesByRanking?take=100', '')
    ALLIANCE_USERRS_URL = ('/AllianceService/ListUsers?allianceId={alliance_id}&skip=0&take=100', '')
    USERS_BY_RANKING_URL = ('/LadderService/ListUsersByRanking?from=1&to=100', '')
    PRESTIGE_TO_URL = ('/CharacterService/PrestigeCharacterTo?characterDesignId={char_id}', '')
    PRESTIGE_FROM_URL = ('/CharacterService/PrestigeCharacterFrom?characterDesignId={char_id}', '')
    COLLECTION_DESIGNS_URL = ('/CollectionService/ListAllCollectionDesigns?version={version}', 'CollectionDesignVersion')
    RESEARCH_DESIGN_URL = ('/ResearchService/ListAllResearchDesigns2', None)
    MARKET_URL = ('/MarketService/ListSalesByItemDesignId?itemDesignId={item_design_id}&saleStatus={sale_status}&from={start}&to={end}', None)

    TYPE_PSS_API_NAME_FIELD = {
        'ship': 'ShipDesignName',
        'room': 'RoomName',
        'char': 'CharacterDesignName',
        'item': 'ItemDesignName',
        'collection': 'CollectionDesignId',
    }

    DEFAULT_EXPIRATION_DURATION = 60 * 60 * 6  # 6 hours

    EQUIPMENT_SLOTS = ['Head', 'Body', 'Leg', 'Hand', 'Accessory']

    SLOT_MAP = {
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

    ENHANCE_MAP = {
        'FireResistance': 'Fire Resistance',
        'None': None
    }

    # 0 - Rock?
    # 1 - Pirate/Dark
    # 2 - Fed/Blue
    # 3 - Qtari/Gold
    # 4 - Visiri/Red
    # 5 - UFO/Green
    # 6 - Starbase

    def __init__(self):
        self._change_data = None
        self._char_map = None
        self._collection_map = None
        self._daily_data = None
        self._device_next_index = 0
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

    @property
    def devices(self):
        if not self._devices:
            self._devices = self.get_devices()

        return self._devices

    @property
    def sprite_map(self):
        if not self._sprite_map or self.expired('sprite'):
            self._sprite_map = self._load_sprite_map()
            self.expire_at('sprite', self.DEFAULT_EXPIRATION_DURATION)

        return self._sprite_map

    @property
    def prices(self):
        if not self._prices or self.expired('prices'):
            self._prices = self._load_prices()
            self.expire_at('prices', self.DEFAULT_EXPIRATION_DURATION)

        return self._prices

    @property
    def ship_map(self):
        if not self._ship_map or self.expired('ship'):
            self._ship_map = self._load_ship_map()
            self.expire_at('ship', self.DEFAULT_EXPIRATION_DURATION)

        return self._ship_map

    @property
    def room_map(self):
        if not self._room_map or self.expired('room'):
            self._room_map, self._upgrade_map = self._load_room_map()
            self.expire_at('room', self.DEFAULT_EXPIRATION_DURATION)

        return self._room_map

    @property
    def research_map(self):
        if not self._research_map or self.expired('room'):
            self._research_map = self._load_research_map()
            self.expire_at('research', self.DEFAULT_EXPIRATION_DURATION)

        return self._research_map

    @property
    def upgrade_map(self):
        if not self._upgrade_map or self.expired('room'):
            self._room_map, self._upgrade_map = self._load_room_map()
            self.expire_at('room', self.DEFAULT_EXPIRATION_DURATION)

        return self._upgrade_map

    @property
    def char_map(self):
        if not self._char_map or self.expired('char'):
            self._char_map = self._load_char_map()
            self.expire_at('char', self.DEFAULT_EXPIRATION_DURATION)
            self.fill_char_collection_data()

        return self._char_map

    @property
    def collection_map(self):
        if not self._collection_map or self.expired('collection'):
            self._collection_map = self._load_collection_map()
            self.expire_at('collection', self.DEFAULT_EXPIRATION_DURATION)
            self.fill_char_collection_data()

        return self._collection_map

    @property
    def item_map(self):
        if not self._item_map or self.expired('item'):
            self._item_map = self._load_item_map()
            self._item_name_map = {item['name']: item_id for item_id, item in self._item_map.items()}
            self.expire_at('item', self.DEFAULT_EXPIRATION_DURATION)

        return self._item_map

    @property
    def item_name_map(self):
        if not self._item_map or self.expired('item'):
            self._item_map = self._load_item_map()
            self._item_name_map = {item['name']: item_id for item_id, item in self._item_map.items()}
            self.expire_at('item', self.DEFAULT_EXPIRATION_DURATION)

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

    def api_url(self, path: Tuple[str, str], server: str = None, **params):
        """Compute endpoint URL with parameters."""

        # if url need version, get it from settings (retrieved from API)
        if path[1]:
            params['version'] = self.settings[path[1]] if hasattr(self, 'settings') else 1

        return (server or self.server) + path[0].format(**params)

    def expired(self, key):
        """Check if cached data is expired."""

        data_expiration = self.data_expiration[key]
        if not data_expiration:
            return True

        return datetime.datetime.utcnow().timestamp() - data_expiration > 0

    def expire_at(self, key, secs):
        """Set expiration duration date."""

        self.data_expiration[key] = datetime.datetime.utcnow().timestamp() + secs

    def get_devices(self):
        """Get generated devices from database."""

        devices = Device.query.all()
        if len(devices) < self.MIN_DEVICES:
            for x in range(0, self.MIN_DEVICES - len(devices)):
                device_key, device_checksum = self.generate_device()
                new_device = Device(key=device_key, checksum=device_checksum)
                db.session.add(new_device)

            db.session.commit()
            devices = Device.query.all()

        return devices

    def generate_device(self):
        """Generate new device key/checksum."""

        device_key = self.create_device_key()
        device_checksum = hashlib.md5((device_key + 'DeviceTypeMacsavysoda').encode('utf-8')).hexdigest()
        return device_key, device_checksum

    @staticmethod
    def create_device_key():
        """Generate random device key."""

        sequence = '0123456789abcdef'
        return ''.join(
            random.choice(sequence)
            + random.choice('26ae')
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
        )

    def get_device(self):
        """Get the next device."""

        devices = self.devices

        if self._device_next_index is None:
            self._device_next_index = random.randrange(len(self.devices))

        if self._device_next_index >= len(devices):
            self._device_next_index = 0

        device = devices[self._device_next_index]
        self._device_next_index += 1

        device = db.session.merge(device)
        db.session.refresh(device)

        return device

    def fill_char_collection_data(self):
        """Updata char data with collection."""

        if self.char_map and self.collection_map:

            # update crew with collection data
            for char in self._char_map.values():
                if char['collection']:
                    char['collection_sprite'] = self.collection_map[char['collection']]['icon_sprite']
                    char['collection_name'] = self.collection_map[char['collection']]['name']

            # collection with crews
            for collection_id, collection in self._collection_map.items():
                collection['chars'] = [char for char in self.char_map.values() if char['collection'] == collection_id]

    def get_sprite_data(self, sprite_id):
        """Get sprite infos from given id."""

        if not sprite_id:
            return {}

        if isinstance(sprite_id, str):
            sprite_id = int(sprite_id)

        if not isinstance(sprite_id, int):
            return {}

        sprite = self.sprite_map.get(sprite_id)
        if not sprite:
            return {}

        return {
            'source': sprite['image_file'],
            'x': sprite['x'],
            'y': sprite['y'],
            'width': sprite['width'],
            'height': sprite['height'],
        }

    def call(self, url, access=False):
        """Make a PSS API call."""

        final_url = url

        # protected endpoint, add device access token
        device = None
        if access:
            device = self.get_device()
            final_url = url + device.access_token_param()

        response = requests.get(final_url)

        # expired token, regenerate tokens and retry
        if device and re.compile(TOKEN_EXPIRED_REGEX).search(response.text):
            device.cycle_token()
            final_url = url + device.access_token_param()
            response = requests.get(final_url)

        if response.encoding is None:
            response.encoding = 'utf-8'

        return response

    def inspect_ship(self, user_id):
        """Get player ship data from API."""

        url = self.api_url(self.INSPECT_SHIP_URL, user_id=user_id)
        response = self.call(url, True)
        root = ElementTree.fromstring(response.text)

        return etree_to_dict(root)

    def is_room_upgradeable(self, room_design_id, ship_design_id):
        """Check if room is upgradeable."""

        upgrade_id = self.upgrade_map.get(room_design_id)
        if not upgrade_id:
            return False

        req_ship_level = self.room_map[upgrade_id]['min_ship_level']
        ship_level = self.ship_map[ship_design_id]['level']

        return req_ship_level <= ship_level

    @staticmethod
    def generate_layout(rooms, ship):
        """Compute ship layout matrix."""

        layout = [[0] * ship['columns'] for _ in range(ship['rows'])]

        for room in rooms:
            room_position_x = room['column']
            room_position_y = room['row']
            room_id = room['id']

            for x in range(room['width']):
                for y in range(room['height']):
                    layout[room_position_y + y][room_position_x + x] = room_id

        return layout

    def compuate_total_armor_effects(self, rooms, layout):
        """For each given rooms based on given layout, compute effective armor effects."""

        for room in rooms:
            room_armor = 0
            if room['power_gen'] + room['power_use'] > 0:
                # check left, right, top and bottom side
                room_position_x = room['column']
                room_position_y = room['row']
                room_width = room['width']
                room_height = room['height']

                for x in range(room_width):
                    room_armor += self.get_armor_capacity(layout, rooms, room_position_x + x, room_position_y - 1)
                    room_armor += self.get_armor_capacity(layout, rooms, room_position_x + x, room_position_y + room_height)

                for y in range(room_height):
                    room_armor += self.get_armor_capacity(layout, rooms, room_position_x - 1, room_position_y + y)
                    room_armor += self.get_armor_capacity(layout, rooms, room_position_x + room_width, room_position_y + y)

            room['armor'] = room_armor

    @staticmethod
    def get_armor_capacity(layout, rooms, x, y):
        """If room at given position is an armor, return armor capacity."""

        neighbor = layout[y][x]
        if not neighbor:
            return 0

        room = [r for r in rooms if r['id'] == neighbor][0]
        if room['type'] == 'Wall':
            return room['capacity']

        return 0

    def interiorize(self, room_id, ship_id):
        """Convert rooms to the correct interior depending on ship race."""

        room = self.get_object('Room', room_id)

        if room['type'] in ('Wall', 'Lift'):
            ship = self.get_object('Ship', ship_id)

            if room['sprite']['source'] in self.RACE_SPECIFIC_SPRITE_MAP:
                # make a new sprite in a new room to keep from overwriting original data
                room = room.copy()
                sprite = room['sprite'].copy()

                sprite['source'] = self.RACE_SPECIFIC_SPRITE_MAP[room['sprite']['source']][ship['race']]
                room['sprite'] = sprite

        return room

    @staticmethod
    def get_user_id(search_name):
        """Given a name return the user_id from database. This should only be an exact match."""

        result = Player.query.filter(Player.name.ilike(search_name)).limit(1).first()
        if result:
            return result.id

        return None

    def get_upgrade_room(self, room_design_id):
        """Get the target upgrade room."""

        upgrade_id = self.upgrade_map[room_design_id]
        if upgrade_id:
            return self.room_map[upgrade_id]

        return None

    def _load_sprite_map(self):
        """Get sprites from API."""

        url = self.api_url(self.LIST_SPRITES_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        sprites = etree_to_dict(root)['FileService']['ListSprites']['Sprites']['Sprite']
        return {
            int(sprite['@SpriteId']): {
                'image_file': int(sprite['@ImageFileId']),
                'x': int(sprite['@X']),
                'y': int(sprite['@Y']),
                'width': int(sprite['@Width']),
                'height': int(sprite['@Height']),
                'sprite_key': sprite['@SpriteKey'],
            }
            for sprite in sprites
        }

    @staticmethod
    def _load_prices():
        """Get all history market summary from database."""

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

        result = db.session.execute(sql).fetchall()
        prices = defaultdict(dict)
        for row in result:
            item_id = row[0]
            currency = row[1]
            prices[item_id][currency] = {
                'count': row[2],
                'p25': row[3],
                'p50': row[4],
                'p75': row[5],
            }

        return prices

    @staticmethod
    def get_item_prices(item_id):
        """Get item history market from database."""

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
        result = db.session.execute(sql, {'item_id': item_id}).fetchall()
        prices = defaultdict(lambda: defaultdict(dict))

        for row in result:
            currency = row[2]
            sale_date = str(row[3])
            prices[currency][sale_date] = {
                'count': row[4],
                'p25': row[5],
                'p50': row[6],
                'p75': row[7],
            }

        data = {
            'id': item_id,
            'prices': prices,
        }

        return data

    def update_ship_data(self):
        """Get ships from API and save them in database."""

        url = self.api_url(self.SHIP_DESIGNS_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for ship_node in root[0][0]:
            record_id = ship_node.get('ShipDesignId')
            Record.update_data('ship', record_id, ship_node)

    def _load_ship_map(self):
        """Load ships from database."""

        records = Record.query.filter_by(type='ship', current=True).all()

        ships = {}
        for record in records:
            ship = ElementTree.fromstring(record.data).attrib
            ships[record.type_id] = {
                'id': record.type_id,
                'name': ship['ShipDesignName'],
                'description': ship['ShipDescription'],
                'level': int(ship['ShipLevel']),
                'hp': int(ship['Hp']),
                'repair_time': int(ship['RepairTime']),
                'exterior_sprite': self.get_sprite_data(int(ship['ExteriorSpriteId'])),
                'interior_sprite': self.get_sprite_data(int(ship['InteriorSpriteId'])),
                'logo_sprite': self.get_sprite_data(int(ship['LogoSpriteId'])),
                'mini_ship_sprite': self.get_sprite_data(int(ship['MiniShipSpriteId'])),
                'frame_sprite': self.get_sprite_data(int(ship['RoomFrameSpriteId'])),
                'left_door_sprite': self.get_sprite_data(int(ship['DoorFrameLeftSpriteId'])),
                'right_door_sprite': self.get_sprite_data(int(ship['DoorFrameRightSpriteId'])),
                'rows': int(ship['Rows']),
                'columns': int(ship['Columns']),
                'race': int(ship['RaceId']),
                'mask': ship['Mask'],
                'mineral_cost': ship['MineralCost'],
                'starbux_cost': ship['StarbuxCost'],
                'mineral_capacity': ship['MineralCapacity'],
                'gas_capacity': ship['GasCapacity'],
                'equipment_capacity': ship['EquipmentCapacity'],
                'ship_type': ship['ShipType'],
            }

        return ships

    def update_research_data(self):
        """Update data and save records."""

        url = self.api_url(self.RESEARCH_DESIGN_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for research_node in root[0][0]:
            record_id = research_node.get('ResearchDesignId')
            Record.update_data('research', record_id, research_node)

    def _load_research_map(self):
        """Load researches from database."""

        records = Record.query.filter_by(type='research', current=True).all()

        researches = {}
        for record in records:
            research = ElementTree.fromstring(record.data).attrib
            researches[record.type_id] = {
                **research,
                'id': record.type_id,
                'name': research['ResearchName'],
                'description': research['ResearchDescription'],
                'gas_cost': int(research['GasCost']),
                'starbux_cost': int(research['StarbuxCost']),
                'lab_level': int(research['RequiredLabLevel']),
                'research_seconds': int(research['ResearchTime']),
                'logo_sprite': self.get_sprite_data(research['LogoSpriteId']),
                'sprite': self.get_sprite_data(research['ImageSpriteId']),
                'required_research_id': int(research['RequiredResearchDesignId']),
                'research_type': research['ResearchDesignType']
            }

        for research in researches.values():
            research['required_research_name'] = (
                researches[research['required_research_id']]['name']
                if research['required_research_id']
                else ''
            )

        return researches

    @staticmethod
    def _parse_price_from_pricestring(pricestring):
        """Split amount and currency."""

        if not pricestring:
            return 0, None

        parts = pricestring.split(':')
        return int(parts[1]), parts[0]

    def update_room_data(self):
        """Get rooms from API and save them in database."""

        url = self.api_url(self.ROOM_DESIGNS_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for room_node in root[0][0]:
            record_id = room_node.get('RoomDesignId')
            Record.update_data('room', record_id, room_node)

    def _load_room_map(self):
        """Load rooms from database."""

        records = Record.query.filter_by(type='room', current=True).all()

        rooms = {}
        for record in records:
            room_node = ElementTree.fromstring(record.data)
            room = room_node.attrib

            missile_design_node = list(room_node.iter('MissileDesign'))
            missile_design = missile_design_node[0].attrib if missile_design_node else None

            rooms[record.type_id] = {
                'id': record.type_id,
                'name': room['RoomName'],
                'short_name': room['RoomShortName'],
                'type': room['RoomType'],
                'level': int(room['Level']),
                'capacity': int(room['Capacity']),
                'height': int(room['Rows']),
                'width': int(room['Columns']),
                'sprite': self.get_sprite_data(int(room['ImageSpriteId'])),
                'construction_sprite': self.get_sprite_data(int(room['ConstructionSpriteId'])),
                'power_use': int(room['MaxSystemPower']),
                'power_gen': int(room['MaxPowerGenerated']),
                'min_ship_level': int(room['MinShipLevel']),
                'upgrade_from_id': int(room['UpgradeFromRoomDesignId']),
                'defense': int(room['DefaultDefenceBonus']),
                'reload': int(room['ReloadTime']),
                'refill_cost': int(room['RefillUnitCost']),
                'show_frame': room['RoomType'] not in ('Lift', 'Wall', 'Corridor'),
                'upgrade_cost': self._parse_price_from_pricestring(room['PriceString'])[0],
                'upgrade_currency': self._parse_price_from_pricestring(room['PriceString'])[1],
                'upgrade_seconds': int(room['ConstructionTime']),
                'description': room['RoomDescription'],
                'system_damage': float(missile_design['SystemDamage']) if missile_design else 0,
                'hull_damage': float(missile_design['HullDamage']) if missile_design else 0,
                'character_damage': float(missile_design['CharacterDamage']) if missile_design else 0,
                'manufacture_type': room['ManufactureType'],
            }

        upgrades = {
            v['upgrade_from_id']: k for
            k, v in rooms.items()
        }

        return rooms, upgrades

    def _parse_equipment_slots(self, char):
        """Determine equipments slots with char equipment mask."""

        equipment_mask = int(char['EquipmentMask'])
        output = [int(x) for x in '{:05b}'.format(equipment_mask)]
        slots = {self.EQUIPMENT_SLOTS[4 - i]: {} for i, b in enumerate(output) if b}

        return slots

    def update_char_data(self):
        """Get crews from API and save them in database."""

        url = self.api_url(self.CHAR_DESIGNS_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for char_node in root[0][0]:
            record_id = char_node.get('CharacterDesignId')
            Record.update_data('char', record_id, char_node)

    def _load_char_map(self):
        """Load crews from database."""

        records = Record.query.filter_by(type='char', current=True).all()

        chars = {}
        for record in records:
            char_node = ElementTree.fromstring(record.data)
            char = char_node.attrib
            chars[record.type_id] = {
                'name': char['CharacterDesignName'],
                'id': record.type_id,
                'sprite': self.get_sprite_data(int(char['ProfileSpriteId'])),
                'head_sprite': self.get_sprite_data(int(char_node[0][0].attrib['StandardSpriteId'])),
                'body_sprite': self.get_sprite_data(int(char_node[0][1].attrib['StandardSpriteId'])),
                'leg_sprite': self.get_sprite_data(int(char_node[0][2].attrib['StandardSpriteId'])),
                'rarity': char['Rarity'].lower(),  # Sprites for gems are 1593. 1594
                'rarity_order': self.RARITY_MAP[char['Rarity']],
                'hp': int_range(char, 'Hp', 'FinalHp'),
                'pilot': float_range(char, 'Pilot', 'FinalPilot'),
                'attack': float_range(char, 'Attack', 'FinalAttack'),
                'repair': float_range(char, 'Repair', 'FinalRepair'),
                'weapon': float_range(char, 'Weapon', 'FinalWeapon'),
                'shield': float_range(char, 'Shield', 'FinalShield'),
                'engine': float_range(char, 'Engine', 'FinalEngine'),
                'research': float_range(char, 'Research', 'FinalResearch'),
                'science': float_range(char, 'Science', 'FinalScience'),
                'ability': float_range(char, 'SpecialAbilityArgument', 'SpecialAbilityFinalArgument'),
                'special_ability': self.ABILITY_MAP.get(char['SpecialAbilityType'], {'name': ''})['name'],
                'ability_sprite':
                    self.get_sprite_data(self.ABILITY_MAP.get(char['SpecialAbilityType'], {'sprite': 110})['sprite']),
                'fire_resist': int(char['FireResistance']),
                'resurrect': 0,
                'walk': int(char['WalkingSpeed']),
                'run': int(char['RunSpeed']),
                'training_limit': int(char['TrainingCapacity']),
                'progression_type': char['ProgressionType'],
                'equipment': self._parse_equipment_slots(char),
                'collection': int(char['CollectionDesignId']),
                'collection_sprite': None,
                'collection_name': '',
            }

            # computed properties
            chars[record.type_id]['width'] = max(chars[record.type_id]['head_sprite']['width'], chars[record.type_id]['body_sprite']['width'],
                                                 chars[record.type_id]['leg_sprite']['width'])

        return chars

    def update_collection_data(self):
        """Get collections from API and save them in database."""

        url = self.api_url(self.COLLECTION_DESIGNS_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for collection_node in root[0][0]:
            record_id = collection_node.get('CollectionDesignId')
            Record.update_data('collection', record_id, collection_node)

    def _load_collection_map(self):
        """Load collections from database."""

        records = Record.query.filter_by(type='collection', current=True).all()

        collections = {}
        for record in records:
            collection = ElementTree.fromstring(record.data).attrib
            collection.update({
                'name': collection['CollectionName'],
                'min': int(collection['MinCombo']),
                'max': int(collection['MaxCombo']),
                'base_enhancement': int(collection['BaseEnhancementValue']),
                'sprite': self.get_sprite_data(int(collection['SpriteId'])),
                'step_enhancement': int(collection['StepEnhancementValue']),
                'icon_sprite': self.get_sprite_data(int(collection['IconSpriteId'])),
                'chars': [],
            })
            collections[record.type_id] = collection

        return collections

    @staticmethod
    def _parse_item_recipe(item_list_string, items):
        """Parse recipe infos from API."""

        recipe = []
        if item_list_string:
            ingredients = [i.split('x') for i in item_list_string.split('|')]
            for ingredient in ingredients:
                item = items.get(int(ingredient[0]))
                if item:
                    line = {
                        'count': int(ingredient[1]),
                        'name': item['name'],
                        'sprite': item['sprite'],
                    }

                    recipe.append(line)

        return recipe

    def update_item_data(self):
        """Get items from API and save them in database."""

        url = self.api_url(self.ITEM_DESIGNS_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        for item_node in root[0][0]:
            record_id = item_node.get('ItemDesignId')
            Record.update_data('item', record_id, item_node, ['FairPrice', 'MarketPrice'])

    def _load_item_map(self):
        """Get items from database."""

        records = Record.query.filter_by(type='item', current=True).all()

        items = {}
        for record in records:
            data = ElementTree.fromstring(record.data).attrib
            items[record.type_id] = {
                'name': data['ItemDesignName'],
                'description': data['ItemDesignDescription'],
                'sprite': self.get_sprite_data(int(data['ImageSpriteId'])),
                'slot': self.SLOT_MAP.get(data['ItemSubType'], data['ItemSubType']),
                'enhancement': data.get('EnhancementType').lower(),
                'disp_enhancement': self.ENHANCE_MAP.get(data['EnhancementType'], data['EnhancementType']),
                'bonus': float(data.get('EnhancementValue')),
                'type': data.get('ItemType'),
                'rarity': data.get('Rarity').lower(),
                'ingredients': data['Ingredients'],
                'market_price': int(data['MarketPrice']),
                'fair_price': int(data['FairPrice']),
                'prices': self.prices.get(int(data['ItemDesignId'])),
                'id': record.type_id,
            }

        # Second pass required for self references
        for item in items.values():
            item['recipe'] = self._parse_item_recipe(item['ingredients'], items)

        return items

    def get_top100_alliances(self):
        """Get the top 100 alliances."""

        url = self.api_url(self.ALLIANCES_BY_RANKING_URL)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        alliances = etree_to_dict(root)['AllianceService']['ListAlliancesByRanking']['Alliances']['Alliance']

        return {
            int(alliance['@AllianceId']): {
                'name': alliance['@AllianceName'],
            }
            for alliance in alliances
        }

    def get_item_sales(self, item, max_sale_id=0):
        """Download sales for given item from PSS API."""

        sales = {}

        # offset, API returns sales only by 20 by 20
        start = 0
        end = 20

        max_sale_id_reached = False
        while "sale_id from API not equal to given max_sale_id":
            url = self.api_url(self.MARKET_URL,
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
        """Get market history of item."""

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
        """Get the top 100 alliances."""

        url = self.api_url(self.ALLIANCE_USERRS_URL, alliance_id=alliance_id)
        response = self.call(url, True)
        root = ElementTree.fromstring(response.text)

        users = etree_to_dict(root)['AllianceService']['ListUsers']['Users']['User']
        return self._parse_users(users)

    def get_top100_users(self):
        """Get the top 100 players."""

        url = self.api_url(self.USERS_BY_RANKING_URL)
        response = self.call(url, True)
        root = ElementTree.fromstring(response.text)

        users = etree_to_dict(root)['LadderService']['ListUsersByRanking']['Users']['User']
        return self._parse_users(users)

    @staticmethod
    def _parse_users(users):
        """Create users dict from XML PSS API response."""

        # force users to be a list
        if not isinstance(users, list):
            users = [users]

        return {
            int(user['@Id']): {
                'name': user['@Name'],
                'trophies': int(user['@Trophy']),
                'alliance_id': int(user['@AllianceId']),
                'last_login_at': user['@LastLoginDate'],
                'alliance_name': user.get('@AllianceName'),
                'alliance_sprite_id': int(user['@AllianceSpriteId']),
            }
            for user in users
        }

    def get_settings(self):
        """Get last game settings from API."""

        url = self.api_url(self.SETTING_URL, server='http://api.pixelstarships.com')
        response = self.call(url)
        try:
            root = ElementTree.fromstring(response.text)
        except ParseError:
            # servers are always supposed to return something valid, but don't always
            url = self.api_url(self.SETTING_URL, server='http://api2.pixelstarships.com')
            response = self.call(url)
            root = ElementTree.fromstring(response.text)

        settings = root[0][0].attrib
        fixed_url = self.api_url(self.SETTING_URL, server='http://' + settings['ProductionServer'])

        if fixed_url != url:
            response = self.call(fixed_url)
            root = ElementTree.fromstring(response.text)
            settings = root[0][0].attrib

        return settings

    def get_prestige_to_data(self, char_id):
        """Get prestige paires and groups which create given char_id."""

        url = self.api_url(self.PRESTIGE_TO_URL, char_id=char_id)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        # extract only useful data
        data = etree_to_dict(root)
        prestiges = dict_get(data, 'CharacterService', 'PrestigeCharacterTo', 'Prestiges', 'Prestige') or []

        # if only one unique prestige, add it in list
        if not isinstance(prestiges, list):
            prestiges = list((prestiges,))

        prestiges_to = list(
            set(
                tuple(
                    sorted([int(prestige['@CharacterDesignId1']), int(prestige['@CharacterDesignId2'])])
                )
                for prestige in prestiges
            )
        )

        # determine which crews to group
        temp_to = prestiges_to
        grouped_to = defaultdict(list)
        while len(temp_to):
            counter = Counter([x for y in temp_to for x in y])
            [(most_id, _)] = counter.most_common(1)

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

        return prestiges_to, grouped_to

    def get_prestige_from_data(self, char_id):
        """Get prestige paires and groups created with given char_id."""

        url = self.api_url(self.PRESTIGE_FROM_URL, char_id=char_id)
        response = self.call(url)
        root = ElementTree.fromstring(response.text)

        # extract only useful data
        data = etree_to_dict(root)
        prestiges = dict_get(data, 'CharacterService', 'PrestigeCharacterFrom', 'Prestiges', 'Prestige') or []

        prestiges_from = [[int(prestige['@CharacterDesignId2']), int(prestige['@ToCharacterDesignId'])] for prestige in prestiges]

        grouped_from = defaultdict(list)
        for response in prestiges_from:
            grouped_from[response[1]].append(response[0])

        return prestiges_from, grouped_from

    def get_prestige_data(self, char_id):
        """Get all prestige combinaisons."""

        prestiges_to, grouped_to = self.get_prestige_to_data(char_id)
        prestiges_from, grouped_from = self.get_prestige_from_data(char_id)

        all_ids = list(set([i for prestige in prestiges_to for i in prestige] + [i for prestige in prestiges_from for i in prestige] + [char_id]))
        all_chars = [self.char_map[i] for i in all_ids]

        return {
            'to': grouped_to,
            'from': grouped_from,
            'chars': all_chars,
            'expires_at': datetime.datetime.now() + datetime.timedelta(minutes=1)
        }

    def get_changes(self):
        """Get changes from database."""

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
                'name': record_data[self.TYPE_PSS_API_NAME_FIELD[record['type']]],
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

    @staticmethod
    def _format_daily_offer(description, items, cost=None, details=None, expires=None):
        return {
            'description': description,
            'objects': items,
            'cost': cost,
            'details': details,
            'expires': expires,
        }

    @staticmethod
    def _format_daily_object(count, type_str, object_str):
        return {
            'count': count,
            'type': type_str,
            'object': object_str,
        }

    @staticmethod
    def _format_daily_price(amount, currency):
        return {
            'price': amount,
            'currency': currency,
        }

    def _parse_daily_cargo(self, item_list_string, cost_list_string):
        """Split daily cargo data into prices and items."""

        splitted_items = [i.split('x') for i in item_list_string.split('|')]
        items = [
            {
                'count': int(item[1]),
                'type': 'Item',
                'object': self.item_map[int(item[0])],
            }
            for item in splitted_items
        ]

        splitted_prices = [i.split(':') for i in cost_list_string.split('|')]
        prices = [
            {
                'currency': price[0],
                'price': int(price[1])
            }
            for price in splitted_prices
        ]

        cargo = [self._format_daily_offer('Cargo', [item], price) for item, price in zip(items, prices)]
        return cargo

    def _parse_daily_items(self, item_list_string):
        items_split = [i.split('x') for i in item_list_string.split('|')]

        items = [
            {
                'count': int(item[1]),
                'type': 'Item',
                'object': self.item_map[int(item[0])],
            }
            for item in items_split
        ]

        return items

    def get_dailies(self):
        """Get settings service data, sales, motd from API."""

        url = self.api_url(self.SETTING_URL)

        response = self.call(url)
        root = ElementTree.fromstring(response.text)
        data = etree_to_dict(root)['SettingService']['GetLatestSetting']['Setting']

        offers = [
            self._format_daily_offer(
                'Shop',
                [self._format_daily_object(
                    1,
                    data['@LimitedCatalogType'],
                    self.get_object(data['@LimitedCatalogType'], int(data['@LimitedCatalogArgument']))
                )],
                self._format_daily_price(data['@LimitedCatalogCurrencyAmount'], data['@LimitedCatalogCurrencyType']),
                [
                    '{} left'.format(data['@LimitedCatalogQuantity']),
                    '{} max'.format(data['@LimitedCatalogMaxTotal']),
                ],
                data['@LimitedCatalogExpiryDate']
            ),
            self._format_daily_offer(
                'Mineral Crew',
                [self._format_daily_object(1, 'Character', self.get_object('Character', int(data['@CommonCrewId'])))],
            ),
            self._format_daily_offer(
                'Starbux Crew',
                [self._format_daily_object(1, 'Character', self.get_object('Character', int(data['@HeroCrewId'])))],
            ),
            self._format_daily_offer(
                'Reward',
                [self._format_daily_object(
                    int(data['@DailyRewardArgument']),
                    'Currency',
                    self._format_daily_price(int(data['@DailyRewardArgument']), data['@DailyRewardType'])
                )] + self._parse_daily_items(data['@DailyItemRewards']),
            ),
        ] + self._parse_daily_cargo(data['@CargoItems'], data['@CargoPrices'])

        dailies = {
            'news': {
                'news': data['@News'],
                'news_date': data['@NewsUpdateDate'],
                'maintenance': data['@MaintenanceMessage'],
                'tournament_news': data['@TournamentNews'],
            },
            'offers': offers,
        }

        return dailies

    def get_object(self, object_type, oid, reload_on_err=True):
        """Get Pixyship object from given PSS API type (LimitedCatalogType for example)."""

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
        """Get sprite date for the given record ID."""

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
            # happens when there's new things, reload
            if reload_on_error:
                self._item_map = None
                self._char_map = None
                self._room_map = None
                self._ship_map = None
                return self.get_record_sprite(record_type, record_id, False)
            else:
                raise

    def get_device_token(self, device_key, device_checksum):
        """Get device token from API for the given generated device."""

        url = (
            self.server + '/UserService/DeviceLogin8'
            '?deviceKey={}'
            '&isJailBroken=false'
            '&checksum={}'
            '&deviceType=DeviceTypeMac'
            '&languagekey=en'
            '&advertisingKey=%22%22'.format(device_key, device_checksum)
        )

        response = requests.post(url)
        root = ElementTree.fromstring(response.text)

        return root.find('UserLogin').attrib['accessToken']
