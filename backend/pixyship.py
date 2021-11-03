import datetime
from collections import defaultdict, Counter
from operator import itemgetter
from xml.etree import ElementTree

from sqlalchemy import desc

from config import CONFIG
from db import db
from models import Player, Record, Listing, Alliance
from pixelstarshipsapi import PixelStarshipsApi
from utils import float_range, int_range, Singleton


class Pixyship(metaclass=Singleton):
    PSS_SPRITES_URL = 'https://pixelstarships.s3.amazonaws.com/{}.png'

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

    COLLECTION_ABILITY_MAP = {
        'EmpSkill': 'EMP Discharge',
        'SharpShooterSkill': 'Sharpshooter',
        'ResurrectSkill': 'Resurrection',
        'BloodThirstSkill': 'Vampirism',
        'MedicalSkill': 'Combat Medic',
        'FreezeAttackSkill': 'Cryo Field',
        'InstantKillSkill': 'Headshot',
        'None': 'None'
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

    TYPE_PSS_API_NAME_FIELD = {
        'ship': 'ShipDesignName',
        'room': 'RoomName',
        'char': 'CharacterDesignName',
        'item': 'ItemDesignName',
        'collection': 'CollectionDesignId',
        'sprite': 'SpriteKey',
    }

    DEFAULT_EXPIRATION_DURATION = 60 * 60 * 1  # 1 hours

    EQUIPMENT_SLOTS = ['Head', 'Body', 'Leg', 'Weapon', 'Accessory', 'Pet']

    SLOT_MAP = {
        'None': None,
        'EquipmentHead': 'Head',
        'EquipmentWeapon': 'Weapon',
        'EquipmentBody': 'Body',
        'EquipmentLeg': 'Leg',
        'EquipmentAccessory': 'Accessory',
        'EquipmentPet': 'Pet',
        'MineralPack': 'Mineral Pack',
        'GasPack': 'Gas Pack',
        'InstantPrize': 'Instant Prize',
        'InstantTraining': 'Instant Training',
        'ReducePrestige': 'Reduce Prestige',
        'ReduceFatigue': 'Reduce Fatigue',
        'ResetTraining': 'Reset Training',
        'AIBook': 'AI Book',
        'FillMineralStorage': 'Fill Mineral Storage',
        'FillGasStorage': 'Fill Gas Storage',
        'SpeedUpConstruction': 'SpeedUp Construction',
    }

    ROOM_TYPE_MAP = {
        'Wall': 'Armor',
    }

    ENHANCE_MAP = {
        'FireResistance': 'Fire Resistance',
        'FreezeAttackSkill': 'Freeze',
        'None': None
    }

    RESEARCH_TYPE_MAP = {
        'CrewLevelUpCost': 'Crew LevelUp Cost',
        'ConcurrentConstruction': 'Concurrent Construction',
        'TradeCapacity': 'Trade',
        'ModuleCapacity': 'Module',
        'StickerCapacity': 'Sticker',
        'AmmoSalvageCapacity': 'Ammo Recycling',
        'CollectAll': 'Collector',
        'ItemRecycling': 'Item Recycling',
        'BoostGauge': 'Boost Gauge',
        'None': None
    }

    # Daily IAP mask (see https://github.com/PieInTheSky-Inc/YaDc)
    IAP_NAMES = {
        500: 'Clip',
        1200: 'Roll',
        2500: 'Stash',
        6500: 'Case',
        14000: 'Vault'
    }

    # 0 - Rock?
    # 1 - Pirate/Dark
    # 2 - Fed/Blue
    # 3 - Qtari/Gold
    # 4 - Visiri/Red
    # 5 - UFO/Green
    # 6 - Starbase
    RACES = {
        1: "Pirate",
        2: "Federation",
        3: "Qtarian",
        4: "Visiri",
        5: "Gray",
    }

    MODULE_ENHANCEMENT_MAP = {
        'Turret': 'Attack'
    }

    MODULE_BONUS_RATIO_MAP = {
        'Turret': 100
    }

    MANUFACTURE_CAPACITY_MAP = {
        'Shield': 'Restore'
    }

    MANUFACTURE_CAPACITY_RATIO_MAP = {
        'Shield': 100
    }

    def __init__(self):
        self._changes = None
        self._characters = None
        self._collections = None
        self._dailies = None
        self._items = None
        self._prestiges = {}
        self._researches = None
        self._prices = {}
        self._rooms = None
        self._ships = None
        self._sprites = None
        self._rooms_sprites = None
        self._upgrades = None
        self._rooms_by_name = None
        self._pixel_starships_api = None
        self.__data_expiration = {}

    @property
    def pixel_starships_api(self):
        if not self._pixel_starships_api or self.expired('api'):
            self._pixel_starships_api = PixelStarshipsApi()
            self.expire_at('api', 60 * 60 * 12)  # 12h

        return self._pixel_starships_api

    @property
    def sprites(self):
        if not self._sprites or self.expired('sprite'):
            self._sprites = self._get_sprites_from_db()
            self.expire_at('sprite', self.DEFAULT_EXPIRATION_DURATION)

        return self._sprites

    @property
    def rooms_sprites(self):
        if not self._rooms_sprites or self.expired('room_sprite'):
            self._rooms_sprites = self._get_room_sprites_from_db()
            self.expire_at('room_sprite', self.DEFAULT_EXPIRATION_DURATION)

        return self._rooms_sprites

    @property
    def prices(self):
        if not self._prices or self.expired('prices'):
            self._prices = self._get_prices_from_db()
            self.expire_at('prices', self.DEFAULT_EXPIRATION_DURATION)

        return self._prices

    @property
    def ships(self):
        if not self._ships or self.expired('ship'):
            self._ships = self._get_ships_from_db()
            self.expire_at('ship', self.DEFAULT_EXPIRATION_DURATION)

        return self._ships

    @property
    def rooms(self):
        if not self._rooms or self.expired('room'):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at('room', self.DEFAULT_EXPIRATION_DURATION)

        return self._rooms

    @property
    def rooms_by_name(self):
        if not self._rooms_by_name or self.expired('room'):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at('room', self.DEFAULT_EXPIRATION_DURATION)

        return self._rooms_by_name

    @property
    def researches(self):
        if not self._researches or self.expired('room'):
            self._researches = self._get_researches_from_db()
            self.expire_at('research', self.DEFAULT_EXPIRATION_DURATION)

        return self._researches

    @property
    def upgrades(self):
        if not self._upgrades or self.expired('room'):
            self._rooms, self._upgrades, self._rooms_by_name = self._get_rooms_from_db()
            self.expire_at('room', self.DEFAULT_EXPIRATION_DURATION)

        return self._upgrades

    @property
    def characters(self):
        if not self._characters or self.expired('char'):
            self._characters = self._get_characters_from_db()

            if self._characters:
                self.expire_at('char', self.DEFAULT_EXPIRATION_DURATION)
                self.fill_char_collection_data()

        return self._characters

    @property
    def collections(self):
        if not self._collections or self.expired('collection'):
            self._collections = self._get_collections_from_db()

            if self._collections:
                self.expire_at('collection', self.DEFAULT_EXPIRATION_DURATION)
                self.fill_char_collection_data()

        return self._collections

    @property
    def items(self):
        if not self._items or self.expired('item'):
            self._items = self._get_items_from_db()
            self.expire_at('item', self.DEFAULT_EXPIRATION_DURATION)

        return self._items

    @property
    def dailies(self):
        if not self._dailies or self.expired('daily'):
            self._dailies = self._get_dailies_from_api()
            self.expire_at('daily', 60 * 5)

        return self._dailies

    @property
    def changes(self):
        if not self._changes or self.expired('change'):
            self._changes = self.get_changes_from_db()
            self.expire_at('change', 60 * 5)

        return self._changes

    def expired(self, key):
        """Check if cached data is expired."""

        if key not in self.__data_expiration:
            return True

        data_expiration = self.__data_expiration[key]
        if not data_expiration:
            return True

        return datetime.datetime.utcnow().timestamp() - data_expiration > 0

    def expire_at(self, key, secs):
        """Set expiration duration date."""

        self.__data_expiration[key] = datetime.datetime.utcnow().timestamp() + secs

    def get_object(self, object_type, oid, reload_on_err=True):
        """Get PixyShip object from given PSS API type (LimitedCatalogType for example)."""

        try:
            if object_type == 'Item':
                return self.items[oid]
            if object_type == 'Character':
                return self.characters[oid]
            if object_type == 'Room':
                return self.rooms[oid]
            if object_type == 'Ship':
                return self.ships[oid]
            if object_type == 'Research':
                return self.researches[oid]
        except KeyError:
            print('KeyErrors')
            # Happens when there's new things, reload
            if reload_on_err:
                self._items = None
                self._characters = None
                self._items = None
                self._ships = None
                self._researches = None
                return self.get_object(object_type, oid, False)
            else:
                raise

    def fill_char_collection_data(self):
        """Updata char data with collection."""

        if self.characters and self.collections:

            # update crew with collection data
            for char in self._characters.values():
                if char['collection']:
                    char['collection_sprite'] = self.collections[char['collection']]['icon_sprite']
                    char['collection_name'] = self.collections[char['collection']]['name']

            # collection with crews
            for collection_id, collection in self._collections.items():
                collection['chars'] = [char for char in self.characters.values() if char['collection'] == collection_id]

    def get_sprite_infos(self, sprite_id):
        """Get sprite infos from given id."""

        if not sprite_id:
            return {}

        if isinstance(sprite_id, str):
            sprite_id = int(sprite_id)

        if not isinstance(sprite_id, int):
            return {}

        sprite = self.sprites.get(sprite_id)
        if not sprite:
            return {}

        return {
            'source': sprite['image_file'],
            'x': sprite['x'],
            'y': sprite['y'],
            'width': sprite['width'],
            'height': sprite['height'],
        }

    def is_room_upgradeable(self, room_design_id, ship_design_id):
        """Check if room is upgradeable."""

        upgrade_id = self.upgrades.get(room_design_id)
        if not upgrade_id:
            return False

        req_ship_level = self.rooms[upgrade_id]['min_ship_level']
        ship_level = self.ships[ship_design_id]['level']

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

    def compute_total_armor_effects(self, rooms, layout):
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
        if room['type'] == 'Armor':
            return room['capacity']

        return 0

    def interiorize(self, room_id, ship_id):
        """Convert rooms to the correct interior depending on ship race."""

        room = self.get_object('Room', room_id)

        if room['type'] in ('Armor', 'Lift'):
            ship = self.get_object('Ship', ship_id)

            if room['sprite']['source'] in self.RACE_SPECIFIC_SPRITE_MAP:
                # make a new sprite in a new room to keep from overwriting original data
                room = room.copy()
                sprite = room['sprite'].copy()

                sprite['source'] = self.RACE_SPECIFIC_SPRITE_MAP[room['sprite']['source']][ship['race']]
                room['sprite'] = sprite

        return room

    def get_exterior_sprite(self, room_id, ship_id):
        """Retrieve exterior sprite if existing"""

        ship = self.get_object('Ship', ship_id)
        exterior_sprite = None

        for _, room_sprite in self.rooms_sprites.items():
            if room_sprite['room_id'] == room_id \
                    and room_sprite['race'] == ship['race'] \
                    and room_sprite['type'] == 'Exterior':
                exterior_sprite = self.get_sprite_infos(room_sprite['sprite_id'])

        return exterior_sprite

    @staticmethod
    def find_user_id(search_name):
        """Given a name return the user_id from database. This should only be an exact match."""

        result = Player.query.filter(Player.name.ilike(search_name)).limit(1).first()
        if result:
            return result.id

        return None

    def get_upgrade_room(self, room_design_id):
        """Get the target upgrade room."""

        upgrade_id = self.upgrades[room_design_id]
        if upgrade_id:
            return self.rooms[upgrade_id]

        return None

    def _get_sprites_from_api(self):
        """Get sprites from API."""

        sprites = self.pixel_starships_api.get_sprites()

        return {
            int(sprite['SpriteId']): {
                'image_file': int(sprite['ImageFileId']),
                'x': int(sprite['X']),
                'y': int(sprite['Y']),
                'width': int(sprite['Width']),
                'height': int(sprite['Height']),
                'sprite_key': sprite['SpriteKey'],
            }
            for sprite in sprites
        }

    def _get_sprites_from_db(self):
        """Load sprites from database."""

        records = Record.query.filter_by(type='sprite', current=True).all()

        sprites = {}
        for record in records:
            sprite = self.pixel_starships_api.parse_sprite_node(ElementTree.fromstring(record.data))

            sprites[record.type_id] = {
                'image_file': int(sprite['ImageFileId']),
                'x': int(sprite['X']),
                'y': int(sprite['Y']),
                'width': int(sprite['Width']),
                'height': int(sprite['Height']),
                'sprite_key': sprite['SpriteKey'],
            }

        return sprites

    def update_sprites(self):
        """Update data and save records."""

        sprites = self.pixel_starships_api.get_sprites()

        for sprite in sprites:
            record_id = sprite['SpriteId']
            Record.update_data('sprite', record_id, sprite['pixyship_xml_element'])

    def _get_room_sprites_from_api(self):
        """Get room sprites from API."""

        rooms_sprites = self.pixel_starships_api.get_rooms_sprites()

        return {
            int(room_sprite['RoomDesignSpriteId']): {
                'room_id': int(room_sprite['RoomDesignId']),
                'race': int(room_sprite['RaceId']),
                'sprite_id': int(room_sprite['SpriteId']),
                'type': room_sprite['RoomSpriteType'],
            }
            for room_sprite in rooms_sprites
        }

    def _get_room_sprites_from_db(self):
        """Load sprites from database."""

        records = Record.query.filter_by(type='room_sprite', current=True).all()

        room_sprites = {}
        for record in records:
            room_sprite = self.pixel_starships_api.parse_room_sprite_node(ElementTree.fromstring(record.data))

            room_sprites[record.type_id] = {
                'room_id': int(room_sprite['RoomDesignId']),
                'race': int(room_sprite['RaceId']),
                'sprite_id': int(room_sprite['SpriteId']),
                'type': room_sprite['RoomSpriteType'],
            }

        return room_sprites

    def update_room_sprites(self):
        """Update data and save records."""

        room_sprites = self.pixel_starships_api.get_rooms_sprites()

        for room_sprite in room_sprites:
            record_id = room_sprite['RoomDesignSpriteId']
            Record.update_data('room_sprite', record_id, room_sprite['pixyship_xml_element'])

    @staticmethod
    def _get_prices_from_db():
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
    def get_item_prices_from_db(item_id):
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

    @staticmethod
    def get_item_last_sales_from_db(item_id, limit):
        """Get last sales from database."""

        sql = """
            SELECT sale_at, amount, currency, price, user_name as buyer_name, seller_name, id
            FROM listing
            WHERE item_id = :item_id
                AND amount > 0
                AND user_name IS NOT NULL
                AND seller_name IS NOT NULL
            ORDER BY sale_at::DATE DESC
            LIMIT :limit
        """
        result = db.session.execute(sql, {'item_id': item_id, 'limit': limit}).fetchall()
        last_sales = []

        for row in result:
            last_sales.append({
                'id': int(row[6]),
                'date': str(row[0]),
                'quantity': row[1],
                'currency': row[2],
                'price': row[3],
                'buyer': row[4],
                'seller': row[5],
            })

        return last_sales

    def update_ships(self):
        """Get ships from API and save them in database."""

        ships = self.pixel_starships_api.get_ships()

        for ship in ships:
            record_id = ship['ShipDesignId']
            Record.update_data('ship', record_id, ship['pixyship_xml_element'])

    def _get_ships_from_db(self):
        """Load ships from database."""

        records = Record.query.filter_by(type='ship', current=True).all()

        ships = {}
        for record in records:
            ship = self.pixel_starships_api.parse_ship_node(ElementTree.fromstring(record.data))
            starbux_cost, mineral_cost, items_cost = self._parse_ship_unlock_costs(ship['MineralCost'], ship['StarbuxCost'], ship['UnlockCost'])

            ships[record.type_id] = {
                'id': record.type_id,
                'name': ship['ShipDesignName'],
                'description': ship['ShipDescription'],
                'level': int(ship['ShipLevel']),
                'hp': int(ship['Hp']),
                'repair_time': int(ship['RepairTime']),
                'exterior_sprite': self.get_sprite_infos(int(ship['ExteriorSpriteId'])),
                'interior_sprite': self.get_sprite_infos(int(ship['InteriorSpriteId'])),
                'logo_sprite': self.get_sprite_infos(int(ship['LogoSpriteId'])),
                'mini_ship_sprite': self.get_sprite_infos(int(ship['MiniShipSpriteId'])),
                'frame_sprite': self.get_sprite_infos(int(ship['RoomFrameSpriteId'])),
                'left_door_sprite': self.get_sprite_infos(int(ship['DoorFrameLeftSpriteId'])),
                'right_door_sprite': self.get_sprite_infos(int(ship['DoorFrameRightSpriteId'])),
                'rows': int(ship['Rows']),
                'columns': int(ship['Columns']),
                'race': int(ship['RaceId']),
                'mask': ship['Mask'],
                'mineral_cost': mineral_cost,
                'starbux_cost': starbux_cost,
                'items_cost': items_cost,
                'mineral_capacity': ship['MineralCapacity'],
                'gas_capacity': ship['GasCapacity'],
                'equipment_capacity': ship['EquipmentCapacity'],
                'ship_type': ship['ShipType'],
            }

        return ships

    def update_researches(self):
        """Update data and save records."""

        researches = self.pixel_starships_api.get_researches()

        for research in researches:
            record_id = research['ResearchDesignId']
            Record.update_data('research', record_id, research['pixyship_xml_element'])

    def _get_researches_from_db(self):
        """Load researches from database."""

        records = Record.query.filter_by(type='research', current=True).all()

        researches = {}
        for record in records:
            research = self.pixel_starships_api.parse_research_node(ElementTree.fromstring(record.data))
            researches[record.type_id] = {
                **research,
                'id': record.type_id,
                'name': research['ResearchName'],
                'description': research['ResearchDescription'],
                'gas_cost': int(research['GasCost']),
                'starbux_cost': int(research['StarbuxCost']),
                'lab_level': int(research['RequiredLabLevel']),
                'research_seconds': int(research['ResearchTime']),
                'logo_sprite': self.get_sprite_infos(research['LogoSpriteId']),
                'sprite': self.get_sprite_infos(research['ImageSpriteId']),
                'required_research_id': int(research['RequiredResearchDesignId']),
                'research_type': self.RESEARCH_TYPE_MAP.get(research['ResearchDesignType'], research['ResearchDesignType'])
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

    def update_rooms(self):
        """Get rooms from API and save them in database."""

        rooms = self.pixel_starships_api.get_rooms()

        for room in rooms:
            record_id = room['RoomDesignId']
            Record.update_data('room', record_id, room['pixyship_xml_element'], ['AvailabilityMask'])

    def _get_rooms_from_db(self):
        """Load rooms from database."""

        records = Record.query.filter_by(type='room', current=True).all()

        rooms = {}
        for record in records:
            room = self.pixel_starships_api.parse_room_node(ElementTree.fromstring(record.data))
            missile_design = room['MissileDesign']

            room_price, room_price_currency = self._parse_price_from_pricestring(room['PriceString'])
            room_type = self.ROOM_TYPE_MAP.get(room['RoomType'], room['RoomType'])

            rooms[record.type_id] = {
                'id': record.type_id,
                'name': room['RoomName'],
                'short_name': room['RoomShortName'],
                'type': room_type,
                'level': int(room['Level']),
                'capacity': int(room['Capacity']),
                'height': int(room['Rows']),
                'width': int(room['Columns']),
                'sprite': self.get_sprite_infos(int(room['ImageSpriteId'])),
                'construction_sprite': self.get_sprite_infos(int(room['ConstructionSpriteId'])),
                'power_use': int(room['MaxSystemPower']),
                'power_gen': int(room['MaxPowerGenerated']),
                'min_ship_level': int(room['MinShipLevel']),
                'upgrade_from_id': int(room['UpgradeFromRoomDesignId']),
                'defense': int(room['DefaultDefenceBonus']),
                'reload': int(room['ReloadTime']),
                'refill_cost': int(room['RefillUnitCost']),
                'show_frame': room_type not in ('Lift', 'Armor', 'Corridor'),
                'upgrade_cost': room_price,
                'upgrade_currency': room_price_currency,
                'upgrade_seconds': int(room['ConstructionTime']),
                'description': room['RoomDescription'],
                'enhancement_type': room['EnhancementType'],
                'manufacture_type': room['ManufactureType'],
                'manufacture_rate': float(room['ManufactureRate']),
                'manufacture_capacity': int(room['ManufactureCapacity']) / self.MANUFACTURE_CAPACITY_RATIO_MAP.get(room['RoomType'], 1),
                'manufacture_capacity_label': self.MANUFACTURE_CAPACITY_MAP.get(room['RoomType'], None),
                'cooldown_time': int(room['CooldownTime']),
                'requirement': self._parse_requirement(room['RequirementString']),
                'extension_grids': int(room.get('SupportedGridTypes', '0')) & 2 != 0,
                'has_weapon_stats': True if missile_design else False,
                'purchasable': True if 'AvailabilityMask' in room else False,
                'system_damage': float(missile_design['SystemDamage']) if missile_design else 0,
                'hull_damage': float(missile_design['HullDamage']) if missile_design else 0,
                'character_damage': float(missile_design['CharacterDamage']) if missile_design else 0,
                'shield_damage': float(missile_design['ShieldDamage']) if missile_design else 0,
                'direct_system_damage': float(missile_design['DirectSystemDamage']) if missile_design else 0,
                'volley': float(missile_design['Volley']) if missile_design else 0,
                'volley_delay': float(missile_design['VolleyDelay']) if missile_design else 0,
                'speed': float(missile_design['Speed']) if missile_design else 0,
                'fire_length': float(missile_design['FireLength']) if missile_design else 0,
                'emp_length': float(missile_design['EMPLength']) if missile_design else 0,
                'stun_length': float(missile_design['StunLength']) if missile_design else 0,
                'hull_percentage_damage': float(missile_design['HullPercentageDamage']) if missile_design else 0,
            }

        upgrades = {
            room['upgrade_from_id']: room_id for
            room_id, room in rooms.items()
        }

        rooms_by_name = {
            room['name']: room for
            room_id, room in rooms.items()
        }

        return rooms, upgrades, rooms_by_name

    def _parse_equipment_slots(self, char):
        """Determine equipments slots with char equipment mask."""

        equipment_mask = int(char['EquipmentMask'])
        output = [int(x) for x in '{:06b}'.format(equipment_mask)]
        slots = {self.EQUIPMENT_SLOTS[5 - i]: {} for i, b in enumerate(output) if b}

        return slots

    def update_characters(self):
        """Get crews from API and save them in database."""

        characters = self.pixel_starships_api.get_characters()

        for character in characters:
            record_id = character['CharacterDesignId']
            Record.update_data('char', record_id, character['pixyship_xml_element'])

    def _get_characters_from_db(self):
        """Load crews from database."""

        records = Record.query.filter_by(type='char', current=True).all()

        characters = {}
        for record in records:
            character_node = ElementTree.fromstring(record.data)
            character = self.pixel_starships_api.parse_character_node(character_node)

            characters[record.type_id] = {
                'name': character['CharacterDesignName'],
                'id': record.type_id,
                'sprite': self.get_sprite_infos(int(character['ProfileSpriteId'])),
                'head_sprite': self.get_sprite_infos(int(character['CharacterParts']['Head']['StandardSpriteId'])),
                'body_sprite': self.get_sprite_infos(int(character['CharacterParts']['Body']['StandardSpriteId'])),
                'leg_sprite': self.get_sprite_infos(int(character['CharacterParts']['Leg']['StandardSpriteId'])),
                'rarity': character['Rarity'].lower(),  # Sprites for gems are 1593. 1594
                'rarity_order': self.RARITY_MAP[character['Rarity']],
                'hp': int_range(character, 'Hp', 'FinalHp'),
                'pilot': float_range(character, 'Pilot', 'FinalPilot'),
                'attack': float_range(character, 'Attack', 'FinalAttack'),
                'repair': float_range(character, 'Repair', 'FinalRepair'),
                'weapon': float_range(character, 'Weapon', 'FinalWeapon'),
                'engine': float_range(character, 'Engine', 'FinalEngine'),
                'research': float_range(character, 'Research', 'FinalResearch'),
                'science': float_range(character, 'Science', 'FinalScience'),
                'ability': float_range(character, 'SpecialAbilityArgument', 'SpecialAbilityFinalArgument'),
                'special_ability': self.ABILITY_MAP.get(character['SpecialAbilityType'], {'name': ''})['name'],
                'ability_sprite':
                    self.get_sprite_infos(self.ABILITY_MAP.get(character['SpecialAbilityType'], {'sprite': 110})['sprite']),
                'fire_resist': int(character['FireResistance']),
                'resurrect': 0,
                'walk': int(character['WalkingSpeed']),
                'run': int(character['RunSpeed']),
                'training_limit': int(character['TrainingCapacity']),
                'progression_type': character['ProgressionType'],
                'equipment': self._parse_equipment_slots(character),
                'collection': int(character['CollectionDesignId']),
                'collection_sprite': None,
                'collection_name': '',
                'description': character['CharacterDesignDescription'],
            }

            # computed properties
            characters[record.type_id]['width'] = max(
                characters[record.type_id]['head_sprite']['width'],
                characters[record.type_id]['body_sprite']['width'],
                characters[record.type_id]['leg_sprite']['width']
            )

        return characters

    def update_collections(self):
        """Get collections from API and save them in database."""

        collections = self.pixel_starships_api.get_collections()

        for collection in collections:
            record_id = collection['CollectionDesignId']
            Record.update_data('collection', record_id, collection['pixyship_xml_element'])

    def _get_collections_from_db(self):
        """Load collections from database."""

        records = Record.query.filter_by(type='collection', current=True).all()

        collections = {}
        for record in records:
            collection_node = ElementTree.fromstring(record.data)
            collection = self.pixel_starships_api.parse_collection_node(collection_node)

            collection.update({
                'id': int(collection['CollectionDesignId']),
                'name': collection['CollectionName'],
                'min': int(collection['MinCombo']),
                'max': int(collection['MaxCombo']),
                'base_enhancement': int(collection['BaseEnhancementValue']),
                'sprite': self.get_sprite_infos(int(collection['SpriteId'])),
                'step_enhancement': int(collection['StepEnhancementValue']),
                'icon_sprite': self.get_sprite_infos(int(collection['IconSpriteId'])),
                'chars': [],
                'ability_name': self.COLLECTION_ABILITY_MAP[collection['EnhancementType']],
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
                # replace hack, 2021 easter event come with additional 'item:' prefix
                ingredient_item_id = ingredient[0].replace('item:', '')

                item = items.get(int(ingredient_item_id))

                if item:
                    line = {
                        'count': int(ingredient[1]),
                        'id': item['id'],
                        'name': item['name'],
                        'sprite': item['sprite'],
                        'rarity': item['rarity'],
                        'slot': item['slot'],
                        'type': item['type'],
                        'disp_enhancement': item['disp_enhancement'],
                        'bonus': item['bonus'],
                        'module_extra_disp_enhancement': item['module_extra_disp_enhancement'],
                        'module_extra_enhancement_bonus': item['module_extra_enhancement_bonus'],
                        'prices': item['prices'],
                        'recipe': Pixyship._parse_item_recipe(item['ingredients'], items),
                    }

                    recipe.append(line)

        return recipe

    def _parse_item_content(self, item_content_string, last_item, items):
        """Parse content infos from API."""

        content = []
        if item_content_string:
            content_items = item_content_string.split('|')
            for content_item in content_items:
                content_item_unpacked = content_item.split(':')
                content_item_type = content_item_unpacked[0]

                content_item_id_count_unpacked = content_item_unpacked[1].split('x')
                content_item_id = content_item_id_count_unpacked[0]

                line = {}

                # if change's a Character, get all infos of the crew
                if content_item_type == 'character':
                    try:
                        line['char'] = self.characters[content_item_id]
                    except KeyError:
                        continue

                # if change's a Item, get all infos of the item
                elif content_item_type == 'item':
                    try:
                        item = items.get(int(content_item_id))
                    except KeyError:
                        continue

                    line['item'] = {
                        'id': item['id'],
                        'name': item['name'],
                        'sprite': item['sprite'],
                        'rarity': item['rarity'],
                        'slot': item['slot'],
                        'type': item['type'],
                        'disp_enhancement': item['disp_enhancement'],
                        'bonus': item['bonus'],
                        'module_extra_disp_enhancement': item['module_extra_disp_enhancement'],
                        'module_extra_enhancement_bonus': item['module_extra_enhancement_bonus'],
                        'recipe': item['recipe'],
                        'prices': item['prices'],
                    }

                    # avoid infinite recursion when item reward can be the item itself
                    if last_item['id'] != item['id']:
                        line['item']['content'] = self._parse_item_content(item['content_string'], item, items)

                # Unknown type
                else:
                    continue

                content_item_count = 1
                if len(content_item_id_count_unpacked) > 1:
                    content_item_count = int(content_item_id_count_unpacked[1])

                line.update({
                    'count': content_item_count,
                    'id': content_item_id,
                    'type': content_item_type,
                })

                content.append(line)

        return content

    def _parse_ship_unlock_costs(self, mineral_cost_string, starbux_cost_string, unlock_cost_string):
        """Parse ship unlock cost infos from API."""

        starbux_cost = 0
        mineral_cost = 0
        items_cost = []

        if unlock_cost_string:
            costs = unlock_cost_string.split('|')
            for cost in costs:
                cost_type, cost_value = cost.split(':')

                if cost_type == 'starbux':
                    starbux_cost = int(cost_value)
                    continue

                if cost_type == 'mineral':
                    mineral_cost = int(cost_value)
                    continue

                if cost_type == 'item':
                    item = self.items.get(int(cost_value))

                    if item:
                        item_cost = {
                            'id': item['id'],
                            'name': item['name'],
                            'sprite': item['sprite'],
                            'rarity': item['rarity'],
                            'slot': item['slot'],
                            'type': item['type'],
                            'disp_enhancement': item['disp_enhancement'],
                            'bonus': item['bonus'],
                            'module_extra_disp_enhancement': item['module_extra_disp_enhancement'],
                            'module_extra_enhancement_bonus': item['module_extra_enhancement_bonus'],
                            'recipe': item['recipe'],
                            'content': item['content'],
                            'prices': item['prices'],
                        }

                        items_cost.append(item_cost)

                    continue
        else:
            # no UnlockCost, use MineralCost and StarbuxCost
            starbux_cost = int(starbux_cost_string)
            mineral_cost = int(mineral_cost_string)

        return starbux_cost, mineral_cost, items_cost

    def update_items(self):
        """Get items from API and save them in database."""

        items = self.pixel_starships_api.get_items()

        for item in items:
            record_id = item['ItemDesignId']
            Record.update_data('item', record_id, item['pixyship_xml_element'], ['FairPrice', 'MarketPrice'])

    def _get_items_from_db(self):
        """Get items from database."""

        records = Record.query.filter_by(type='item', current=True).all()

        items = {}
        for record in records:
            item_node = ElementTree.fromstring(record.data)
            item = self.pixel_starships_api.parse_item_node(item_node)

            number_of_rewards = 0
            if item['Content'] and float(item['ModuleArgument']) != 0:
                number_of_rewards = item['ModuleArgument']

            module_extra_enhancement = self._parse_module_extra_enhancement(item)

            items[record.type_id] = {
                'name': item['ItemDesignName'],
                'description': item['ItemDesignDescription'],
                'sprite': self.get_sprite_infos(int(item['ImageSpriteId'])),
                'logo_sprite': self.get_sprite_infos(int(item['LogoSpriteId'])),
                'slot': self.SLOT_MAP.get(item['ItemSubType'], item['ItemSubType']),
                'enhancement': item.get('EnhancementType').lower(),
                'disp_enhancement': self.ENHANCE_MAP.get(item['EnhancementType'], item['EnhancementType']),
                'bonus': float(item.get('EnhancementValue')),
                'module_extra_enhancement': module_extra_enhancement['enhancement'],
                'module_extra_disp_enhancement': module_extra_enhancement['disp_enhancement'],
                'module_extra_enhancement_bonus': module_extra_enhancement['bonus'],
                'type': item.get('ItemType'),
                'rarity': item.get('Rarity').lower(),
                'ingredients': item['Ingredients'],
                'content_string': item['Content'],
                'number_of_rewards': number_of_rewards,
                'market_price': int(item['MarketPrice']),
                'fair_price': int(item['FairPrice']),
                'prices': self.prices.get(int(item['ItemDesignId'])),
                'id': record.type_id,
                'saleable': (int(item['Flags']) & 1) != 0
            }

        # Second pass required for self references
        for item in items.values():
            item['recipe'] = self._parse_item_recipe(item['ingredients'], items)

        # Third pass required for self references
        for item in items.values():
            item['content'] = self._parse_item_content(item['content_string'], item, items)

        return items

    def get_top100_alliances_from_api(self):
        """Get the top 100 alliances."""

        alliances = self.pixel_starships_api.get_alliances()

        return {
            int(alliance['AllianceId']): {
                'name': alliance['AllianceName'],
            }
            for alliance in alliances
        }

    def get_sales_from_api(self, item_id):
        """Get market history of item."""

        # get max sale_id to retrieve only new sales
        max_sale_id_result = Listing.query \
            .filter(Listing.item_id == item_id) \
            .order_by(desc(Listing.id)) \
            .limit(1) \
            .first()

        if max_sale_id_result is not None:
            max_sale_id = max_sale_id_result.id if max_sale_id_result.id is not None else 0
        else:
            max_sale_id = 0

        sales = self.pixel_starships_api.get_sales(item_id, max_sale_id)
        return sales

    def get_alliance_users_from_api(self, alliance_id):
        """Get the top 100 alliances."""

        users = self.pixel_starships_api.get_alliance_users(alliance_id)
        return self._parse_users(users)

    def get_top100_users_from_api(self):
        """Get the top 100 players."""

        users = self.pixel_starships_api.get_users(1, 100)
        return self._parse_users(users)

    @staticmethod
    def _parse_users(users):
        """Create users dict from XML PSS API response."""

        # force users to be a list
        if not isinstance(users, list):
            users = [users]

        return {
            int(user['Id']): {
                'name': user['Name'],
                'trophies': int(user['Trophy']),
                'alliance_id': int(user['AllianceId']),
                'last_login_at': user['LastLoginDate'],
                'alliance_name': user.get('AllianceName'),
                'alliance_sprite_id': int(user['AllianceSpriteId']),
            }
            for user in users
        }

    def _get_prestige_to_from_api(self, character_id):
        """Get prestige paires and groups which create given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_to(character_id)

        # if only one unique prestige, add it in list
        if not isinstance(prestiges, list):
            prestiges = list((prestiges,))

        prestiges_to = list(
            set(
                tuple(
                    sorted([int(prestige['CharacterDesignId1']), int(prestige['CharacterDesignId2'])])
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

    def _get_prestige_from_from_api(self, character_id):
        """Get prestige paires and groups created with given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_from(character_id)
        prestiges_from = [[int(prestige['CharacterDesignId2']), int(prestige['ToCharacterDesignId'])] for prestige in prestiges]

        grouped_from = defaultdict(list)
        for response in prestiges_from:
            grouped_from[response[1]].append(response[0])

        return prestiges_from, grouped_from

    def get_prestiges_from_api(self, char_id):
        """Get all prestige combinaisons."""

        prestiges_to, grouped_to = self._get_prestige_to_from_api(char_id)
        prestiges_from, grouped_from = self._get_prestige_from_from_api(char_id)

        all_ids = list(set([i for prestige in prestiges_to for i in prestige] + [i for prestige in prestiges_from for i in prestige] + [char_id]))
        all_chars = [self.characters[i] for i in all_ids]

        return {
            'to': grouped_to,
            'from': grouped_from,
            'chars': all_chars,
            'expires_at': datetime.datetime.now() + datetime.timedelta(minutes=1)
        }

    def get_changes_from_db(self):
        """Get changes from database."""

        # retrieve minimum dates of each types
        min_changes_dates_sql = """
            SELECT type, MIN(created_at) + INTERVAL '1 day' AS min
            FROM record
            WHERE type IN ('item', 'ship', 'char', 'room', 'sprite')
            GROUP BY type
        """

        min_changes_dates_result = db.session.execute(min_changes_dates_sql).fetchall()

        min_changes_dates_conditions = []
        for min_changes_dates_record in min_changes_dates_result:
            if min_changes_dates_record['type'] == 'sprite':
                # only new
                condition = "(c.type = '{}' AND o.data IS NULL AND (o.id IS NOT NULL OR c.created_at > '{}'))".format(
                    min_changes_dates_record['type'],
                    min_changes_dates_record['min']
                )
            else:
                condition = "(c.type = '{}' AND (o.id IS NOT NULL OR c.created_at > '{}'))".format(
                    min_changes_dates_record['type'],
                    min_changes_dates_record['min']
                )
            min_changes_dates_conditions.append(condition)

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
                    WHERE
                        c.current = TRUE
                        AND ({})
                    ORDER BY c.id, o.created_at DESC
                ) AS sub
            ORDER BY created_at DESC
            LIMIT {}
        """.format(' OR '.join(min_changes_dates_conditions), CONFIG.get('CHANGES_MAX_ASSETS', 5000))

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
                change['char'] = self.characters[record['type_id']]

            # if change's a Item, get all infos of the item
            if record['type'] == 'item':
                item = self.items[record['type_id']]
                change['item'] = {
                    'id': item['id'],
                    'name': item['name'],
                    'sprite': item['sprite'],
                    'rarity': item['rarity'],
                    'slot': item['slot'],
                    'type': item['type'],
                    'disp_enhancement': item['disp_enhancement'],
                    'bonus': item['bonus'],
                    'module_extra_disp_enhancement': item['module_extra_disp_enhancement'],
                    'module_extra_enhancement_bonus': item['module_extra_enhancement_bonus'],
                    'recipe': item['recipe'],
                    'content': item['content'],
                    'prices': item['prices'],
                }

            changes.append(change)

        return changes

    def _format_daily_offer(self, description, sprite_id, items, cost=None, details=None, expires=None):
        return {
            'description': description,
            'sprite': self.get_sprite_infos(sprite_id),
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

    def _parse_requirement(self, requirement_string):
        """Split requirements into items."""

        if not requirement_string:
            return None

        requirement_type, id_and_amount = requirement_string.split(':')

        if '>=' in id_and_amount:
            requirement_id, requirement_count = id_and_amount.split('>=')
        else:
            requirement_id, requirement_count = id_and_amount.split('>')

        requirement_type = requirement_type.strip().capitalize()
        requirement_id = int(requirement_id.strip())
        requirement_count = int(requirement_count.strip())

        # in some case (example: Coal Factory), the amount needed is '> 0' not '>= 1'
        if requirement_count == 0:
            requirement_count = 1

        requirement_object = {
            'count': requirement_count,
            'type': requirement_type,
            'object': self.get_object(requirement_type, requirement_id),
        }

        return requirement_object

    def _parse_daily_cargo(self, item_list_string, cost_list_string):
        """Split daily cargo data into prices and items."""

        splitted_items = [i.split('x') for i in item_list_string.split('|')]
        items = [
            {
                'count': int(item[1]),
                'type': 'Item',
                'object': self.items[int(item[0])],
            }
            for item in splitted_items
        ]

        splitted_prices = [i.split(':') for i in cost_list_string.split('|')]
        prices = []
        for splitted_price in splitted_prices:
            price = {
                'currency': splitted_price[0]
            }

            amount = splitted_price[1].split('x')
            if len(amount) > 1:
                item_id = int(amount[0])
                price['price'] = item_id
                price['count'] = amount[1]
                price['object'] = self.items[item_id]
            else:
                price['price'] = int(splitted_price[1])

            prices.append(price)

        cargo = [self._format_daily_offer('Cargo', None, [item], price) for item, price in zip(items, prices)]
        return cargo

    def _parse_daily_items(self, item_list_string):
        items_split = [i.split('x') for i in item_list_string.split('|')]

        items = [
            {
                'count': int(item[1]),
                'type': 'Item',
                'object': self.items[int(item[0])],
            }
            for item in items_split
        ]

        return items

    def _get_dailies_from_api(self):
        """Get settings service data, sales, motd from API."""

        data = self.pixel_starships_api.get_dailies()
        offers = {
            'shop': self._format_daily_offer(
                'Shop',
                592,
                [
                    self._format_daily_object(
                        1,
                        data['LimitedCatalogType'],
                        self.get_object(data['LimitedCatalogType'], int(data['LimitedCatalogArgument']))
                    )
                ],
                self._format_daily_price(data['LimitedCatalogCurrencyAmount'], data['LimitedCatalogCurrencyType']),
                {
                    'left': data['LimitedCatalogQuantity'],
                    'max': data['LimitedCatalogMaxTotal'],
                },
                data['LimitedCatalogExpiryDate']
            ),

            'blueCargo': {
                'sprite': self.get_sprite_infos(11880),
                'items': [
                    self._format_daily_offer(
                        'Mineral Crew',
                        None,
                        [self._format_daily_object(1, 'Character', self.get_object('Character', int(data['CommonCrewId'])))],
                    ),
                    self._format_daily_offer(
                        'Starbux Crew',
                        None,
                        [self._format_daily_object(1, 'Character', self.get_object('Character', int(data['HeroCrewId'])))],
                    )
                ],
            },

            'greenCargo': {
                'sprite': self.get_sprite_infos(11881),
                'items': self._parse_daily_cargo(data['CargoItems'], data['CargoPrices']),
            },

            'dailyRewards': self._format_daily_offer(
                'Reward',
                2326,
                [
                    self._format_daily_object(
                        int(data['DailyRewardArgument']),
                        'Currency',
                        self._format_daily_price(int(data['DailyRewardArgument']), data['DailyRewardType'])
                    )
                ] + self._parse_daily_items(data['DailyItemRewards']),
            ),

            'sale': self._format_daily_offer(
                'Sale',
                11006,
                [
                    self._format_daily_object(
                        1,
                        data['SaleType'],
                        self.get_object(data['SaleType'], int(data['SaleArgument']))
                    )
                ],
                {
                    'options': self._format_daily_sale_options(int(data['SaleItemMask']))
                }
            )
        }

        dailies = {
            'stardate': self.pixel_starships_api.get_stardate(),
            'news': {
                'news': data['News'],
                'news_date': data['NewsUpdateDate'],
                'maintenance': self.pixel_starships_api.maintenance_message,  # not anymore available with the new API endpoint
                'tournament_news': data['TournamentNews'],
                'sprite': self.get_sprite_infos(data['NewsSpriteId']),
            },
            'offers': offers,
        }

        return dailies

    def get_record_sprite(self, record_type, record_id, reload_on_error=True):
        """Get sprite date for the given record ID."""

        try:
            if record_type == 'item':
                return self.items[record_id]['sprite']
            if record_type == 'char':
                return self.characters[record_id]['sprite']
            if record_type == 'room':
                return self.rooms[record_id]['sprite']
            if record_type == 'ship':
                return self.ships[record_id]['mini_ship_sprite']
            if record_type == 'sprite':
                return self.get_sprite_infos(record_id)
        except KeyError:
            # happens when there's new things, reload
            if reload_on_error:
                self._items = None
                self._characters = None
                self._rooms = None
                self._ships = None
                return self.get_record_sprite(record_type, record_id, False)
            else:
                raise

    def get_player_data(self, search: str = None):
        """Retrieve all players data or players found by given search."""

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
                'alliance_sprite': self.get_sprite_infos(player.sprite_id),
            }
            for player in results
        ]

    def get_ship_data(self, player_name):
        """Get user and ship data from API."""

        ship, user, rooms, stickers, upgrades = self.summarize_ship(player_name)

        if user:
            data = {
                'rooms': rooms,
                'user': user,
                'ship': ship,
                'stickers': stickers,
                'upgrades': upgrades,
                'status': 'found'
            }

            data['user']['confirmed'] = True
            data = self._limit_ship_data(data)
        else:
            data = {
                'status': 'not found'
            }

        response = {
            'data': data,
            'status': 'success'
        }

        return response

    @staticmethod
    def _limit_ship_data(data):
        """Remove ship data that shouldn't be visible to others."""

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
            r.pop('defense')

        return data

    def summarize_ship(self, player_name):
        """Get ship, user, rooms and upgrade from given player name."""

        user_id = self.find_user_id(player_name)

        if not user_id:
            return None, None, None, None, None

        inspect_ship = self.pixel_starships_api.inspect_ship(user_id)

        # only seen on admin players so far
        if not inspect_ship:
            return None, None, None, None, None

        upgrades = []
        user_data = inspect_ship['User']
        more_user_data = self.pixel_starships_api.search_users(user_data['Name'], True)[0]
        ship_data = inspect_ship['Ship']

        user = dict(
            id=user_data['Id'],
            name=user_data['Name'],
            sprite=self.get_sprite_infos(int(user_data['IconSpriteId'])),
            alliance_name=user_data.get('AllianceName'),
            alliance_membership=user_data.get('AllianceMembership'),
            alliance_join_date=more_user_data.get('AllianceJoinDate'),
            alliance_sprite=self.get_sprite_infos(int(user_data.get('AllianceSpriteId'))),
            trophies=int(user_data['Trophy']),
            last_date=user_data['LastAlertDate'],
            pvpattack_wins=int(more_user_data['PVPAttackWins']),
            pvpattack_losses=int(more_user_data['PVPAttackLosses']),
            pvpattack_draws=int(more_user_data['PVPAttackDraws']),
            pvpattack_ratio=self._compute_pvp_ratio(int(more_user_data['PVPAttackWins']), int(more_user_data['PVPAttackLosses']),
                                                    int(more_user_data['PVPAttackDraws'])),
            pvpdefence_draws=int(more_user_data['PVPDefenceDraws']),
            pvpdefence_wins=int(more_user_data['PVPDefenceWins']),
            pvpdefence_losses=int(more_user_data['PVPDefenceLosses']),
            pvpdefence_ratio=self._compute_pvp_ratio(int(more_user_data['PVPDefenceWins']), int(more_user_data['PVPDefenceLosses']),
                                                     int(more_user_data['PVPDefenceDraws'])),
            highest_trophy=int(more_user_data['HighestTrophy']),
            crew_donated=int(more_user_data['CrewDonated']),
            crew_received=int(more_user_data['CrewReceived']),
            creation_date=more_user_data['CreationDate'],
            race=self.RACES.get(int(ship_data['OriginalRaceId']), 'Unknown'),
            last_login_date=more_user_data['LastLoginDate'],
        )

        ship_id = int(ship_data['ShipDesignId'])
        immunity_date = ship_data['ImmunityDate']

        rooms = []
        for room_data in ship_data['Rooms']:
            room = dict(
                self.interiorize(int(room_data['RoomDesignId']), ship_id),
                design_id=int(room_data['RoomDesignId']),
                id=int(room_data['RoomId']),
                row=int(room_data['Row']),
                column=int(room_data['Column']),
                construction=bool(room_data['ConstructionStartDate']),
                upgradable=self.is_room_upgradeable(int(room_data['RoomDesignId']), ship_id),
            )

            room['exterior_sprite'] = self.get_exterior_sprite(int(room_data['RoomDesignId']), ship_id)

            if room['upgradable']:
                upgrade_room = self.get_upgrade_room(room['design_id'])
                if upgrade_room:
                    cost = upgrade_room['upgrade_cost']
                    upgrades.append(
                        dict(
                            description=room['name'],
                            amount=cost,
                            currency=upgrade_room['upgrade_currency'],
                            seconds=upgrade_room['upgrade_seconds'])
                    )

            rooms.append(room)

        ship = dict(
            self.ships[ship_id],
            power_use=sum([room['power_use'] for room in rooms]),
            power_gen=sum([room['power_gen'] for room in rooms]),
            shield=sum([room['capacity'] for room in rooms if room['type'] == 'Shield']),
            immunity_date=immunity_date,
            hue=ship_data['HueValue'],
            saturation=ship_data['SaturationValue'],
            brightness=ship_data['BrightnessValue'],
        )

        stickers = self._parse_ship_stickers(ship_data)

        layout = self.generate_layout(rooms, ship)
        self.compute_total_armor_effects(rooms, layout)

        return ship, user, rooms, stickers, sorted(upgrades, key=itemgetter('amount'))

    @staticmethod
    def get_tournament_infos():
        utc_now = datetime.datetime.utcnow()
        first_day_next_month = (utc_now.date().replace(day=1) + datetime.timedelta(days=32)).replace(day=1)
        tournament_start = first_day_next_month - datetime.timedelta(days=7)
        tournament_start_time = datetime.datetime(tournament_start.year, tournament_start.month, tournament_start.day)

        tournament_left_delta = tournament_start_time - utc_now
        tournament_left_seconds = tournament_left_delta.days * 24 * 3600 + tournament_left_delta.seconds
        tournament_left_minutes, tournament_left_seconds = divmod(tournament_left_seconds, 60)
        tournament_left_hours, tournament_left_minutes = divmod(tournament_left_minutes, 60)
        tournament_left_days, tournament_left_hours = divmod(tournament_left_hours, 24)
        tournament_left_weeks, tournament_left_days = divmod(tournament_left_days, 7)

        tournament_left_formatted = ''
        if tournament_left_weeks > 0:
            tournament_left_formatted += '{}w'.format(tournament_left_weeks)

        if tournament_left_days > 0:
            tournament_left_formatted += ' {}d'.format(tournament_left_days)

        if tournament_left_hours > 0:
            tournament_left_formatted += ' {}h'.format(tournament_left_hours)

        if tournament_left_minutes > 0:
            tournament_left_formatted += ' {}m'.format(tournament_left_minutes)

        infos = {
            'start': tournament_start,
            'end': first_day_next_month,
            'left': tournament_left_formatted.strip(),
            'started': tournament_left_delta.total_seconds() < 0
        }

        return infos

    def _parse_ship_stickers(self, ship_data):
        stickers_string = ship_data['StickerString']

        if not stickers_string:
            return None

        stickers = []

        for sticker_string in stickers_string.split('|'):
            item_id = int(sticker_string.split('@')[0])
            item = self.items[item_id]
            coords = sticker_string.split('@')[1].split('-')

            sticker = {
                'sprite': item['logo_sprite'],
                'x': coords[0],
                'y': coords[1],
                'size': coords[2],
            }

            stickers.append(sticker)

        return stickers

    def _format_daily_sale_options(self, sale_item_mask):
        """"From flag determine Sale options."""

        result = []
        options = self.pixel_starships_api.parse_sale_item_mask(sale_item_mask)

        for option in options:
            name = self.IAP_NAMES[option]
            result.append({'name': name, 'value': option})

        return result

    def get_researches_and_ship_min_level(self):
        """Retrieve research and min ship level of the needed lab."""

        researches = self.researches

        # get lab room and its min ship level
        for research in researches.values():
            # TODO: don't use the name but the lab level
            lab_name = 'Laboratory Lv{}'.format(research['lab_level'])
            if lab_name in self.rooms_by_name:
                room = self.rooms_by_name[lab_name]
                research['min_ship_level'] = room['min_ship_level']

        return researches

    @staticmethod
    def _compute_pvp_ratio(wins, losses, draws):
        """Compute PVP ratio, same formula as Dolores Bot."""

        ratio = 0.0
        battles = wins + losses + draws

        if battles > 0:
            ratio = (wins + .5 * draws) / battles
            ratio *= 100

        return round(ratio, 2)

    def _parse_module_extra_enhancement(self, item):
        """Parse module extra enhancement from a given item."""

        enhancement = self.MODULE_ENHANCEMENT_MAP.get(item['ModuleType'], None)
        disp_enhancement = self.ENHANCE_MAP.get(enhancement, enhancement)

        bonus = None
        if float(item['ModuleArgument']) != 0:
            bonus = float(item['ModuleArgument']) / self.MODULE_BONUS_RATIO_MAP.get(item['ModuleType'], 1)

        return {
            'enhancement': enhancement,
            'disp_enhancement': disp_enhancement,
            'bonus': bonus
        }
