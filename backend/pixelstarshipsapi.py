import datetime
import hashlib
import random
import re
from typing import Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import requests

from api_errors import TOKEN_EXPIRED_REGEX
from db import db
from models import Device


class PixelStarshipsApi:
    """Manage Pixel Starships API."""

    MIN_DEVICES = 10
    PSS_START_DATE = datetime.date(year=2016, month=1, day=6)

    IAP_OPTIONS_MASK_LOOKUP = [
        500,
        1200,
        2500,
        6500,
        14000
    ]

    def __init__(self):
        self.__api_settings = self.get_api_settings()
        self.server = self.__api_settings['ProductionServer']
        self._device_next_index = 0
        self._devices = None

    @property
    def devices(self):
        if not self._devices:
            self._devices = self.get_devices()

        return self._devices

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

    def get_api_settings(self):
        """Get last game settings from API."""

        params = {
            'languageKey': 'en',
            'deviceType': 'DeviceTypeAndroid'
        }

        try:
            # call API with classic URL, in case of error, try with alternative
            endpoint = 'https://api.pixelstarships.com/SettingService/getlatestversion3'
            response = self.call(endpoint, params=params)
            root = ElementTree.fromstring(response.text)
        except ParseError:
            # servers are always supposed to return something valid, but don't always
            endpoint = 'https://api2.pixelstarships.com/SettingService/getlatestversion3'
            response = self.call(endpoint, params=params)
            root = ElementTree.fromstring(response.text)

        settings = root.find(".//Setting").attrib
        fixed_endpoint = f'https://{settings["ProductionServer"]}/SettingService/getlatestversion3'

        if fixed_endpoint != endpoint:
            response = self.call(fixed_endpoint, params=params)
            root = ElementTree.fromstring(response.text)
            settings = root.find(".//Setting").attrib

        return settings

    def api_url(self, path: Tuple[str, str], server: str = None, **params):
        """Compute endpoint URL with parameters."""

        # if url need version, get it from settings (retrieved from API)
        if path[1]:
            params['version'] = self.__api_settings[path[1]] if hasattr(self, 'settings') else 1

        return (server or self.server) + path[0].format(**params)

    def call(self, endpoint, params, access=False):
        """Make a PSS API call."""

        # protected endpoint, add device access token
        device = None
        if access:
            device = self.get_device()
            params['accessToken'] = device.get_token()

        response = requests.get(endpoint, params=params)

        # expired token, regenerate tokens and retry
        if device and re.compile(TOKEN_EXPIRED_REGEX).search(response.text):
            device.cycle_token()
            params['accessToken'] = device.get_token()
            response = requests.get(endpoint, params=params)

        if response.encoding is None:
            response.encoding = 'utf-8'

        return response

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

    def generate_device(self):
        """Generate new device key/checksum."""

        device_key = self.create_device_key()
        device_checksum = hashlib.md5((device_key + 'DeviceTypeMac' + 'savysoda').encode('utf-8')).hexdigest()

        return device_key, device_checksum

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

    def get_device_token(self, device_key, device_checksum):
        """Get device token from API for the given generated device."""

        params = {
            'deviceKey': device_key,
            'checksum': device_checksum,
            'isJailBroken': 'false',
            'deviceType': 'DeviceTypeMac',
            'languagekey': 'en',
            'advertisingKey': '""',
        }

        endpoint = f'https://{self.server}/UserService/DeviceLogin8'
        response = requests.post(endpoint, params=params)

        root = ElementTree.fromstring(response.content.decode('utf-8'))
        user_login_node = root.find('.//UserLogin')

        return user_login_node.attrib['accessToken']

    def inspect_ship(self, user_id):
        """Get player ship data from API."""

        params = {
            'userId': user_id,
            'version': self.__api_settings['ShipDesignVersion']
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/ShipService/InspectShip2'
        response = self.call(endpoint, params=params, access=True)
        root = ElementTree.fromstring(response.text)

        inspect_ship = {
            'User': root.find('.//User').attrib.copy(),
            'Ship': root.find('.//Ship').attrib.copy()
        }

        inspect_ship['User']['pixyship_xml_element'] = root.find('.//User')
        inspect_ship['Ship']['pixyship_xml_element'] = root.find('.//Ship')

        # get rooms
        rooms_node = root.find('.//Rooms')
        inspect_ship['Ship']['Rooms'] = []
        for room_node in rooms_node:
            room = room_node.attrib.copy()
            room['pixyship_xml_element'] = room_node
            inspect_ship['Ship']['Rooms'].append(room)

        return inspect_ship

    def search_users(self, user_name, exact_match = False):
        """Get player ship data from API."""

        params = {
            'searchstring': user_name,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/UserService/SearchUsers'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        users = []

        if exact_match:
            user_node = root.find('.//User[@Name="{}"]'.format(user_name))

            user = self.parse_user_node(user_node)

            user['pixyship_xml_element'] = user_node  # custom field, return raw XML data too
            users.append(user)
        else:
            users_node = root.find('.//User')

            for user_node in users_node:
                user = self.parse_user_node(user_node)

                user['pixyship_xml_element'] = user_node  # custom field, return raw XML data too
                users.append(user)

        return users

    @staticmethod
    def parse_user_node(user_node):
        """Extract user data from XML node."""

        return user_node.attrib

    def get_dailies(self):
        """Get dailies from settings service from API."""

        params = {
            'languageKey': 'en',
            'deviceType': 'DeviceTypeAndroid'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/SettingService/getlatestversion3'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        dailies_node = root.find('.//Setting')

        dailies = dailies_node.attrib.copy()
        dailies['pixyship_xml_element'] = dailies_node  # custom field, return raw XML data too

        return dailies

    def get_sprites(self):
        """Get sprites from API."""

        params = {
            'version': self.__api_settings['FileVersion'],
            'deviceType': 'DeviceTypeAndroid'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/FileService/ListSprites'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        sprites = []
        sprite_nodes = root.find('.//Sprites')

        for sprite_node in sprite_nodes:
            sprite = self.parse_sprite_node(sprite_node)
            sprite['pixyship_xml_element'] = sprite_node  # custom field, return raw XML data too
            sprites.append(sprite)

        return sprites

    @staticmethod
    def parse_sprite_node(sprite_node):
        """Extract character data from XML node."""

        return sprite_node.attrib

    def get_rooms_sprites(self):
        """Get rooms sprites from API."""

        params = {
            'version': self.__api_settings['RoomDesignSpriteVersion']
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/RoomDesignSpriteService/ListRoomDesignSprites'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms_sprites = []
        room_sprites_nodes = root.find('.//RoomDesignSprites')

        for room_sprites_node in room_sprites_nodes:
            room_sprites = self.parse_room_sprite_node(room_sprites_node)
            room_sprites['pixyship_xml_element'] = room_sprites_node  # custom field, return raw XML data too
            rooms_sprites.append(room_sprites)

        return rooms_sprites

    @staticmethod
    def parse_room_sprite_node(room_sprite_node):
        """Extract room sprite data from XML node."""

        return room_sprite_node.attrib

    def get_ships(self):
        """Get ships designs from API."""

        params = {
            'version': self.__api_settings['ShipDesignVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/ShipService/ListAllShipDesigns2'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        ships = []
        ship_nodes = root.find('.//ShipDesigns')

        for ship_node in ship_nodes:
            ship = self.parse_ship_node(ship_node)
            ship['pixyship_xml_element'] = ship_node  # custom field, return raw XML data too
            ships.append(ship)

        return ships

    @staticmethod
    def parse_ship_node(ship_node):
        """Extract character data from XML node."""

        return ship_node.attrib.copy()

    def get_researches(self):
        """Get research designs from API."""

        params = {
            'version': self.__api_settings['ResearchDesignVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/ResearchService/ListAllResearchDesigns2'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        researches = []
        research_nodes = root.find('.//ResearchDesigns')

        for research_node in research_nodes:
            research = self.parse_research_node(research_node)
            research['pixyship_xml_element'] = research_node  # custom field, return raw XML data too
            researches.append(research)

        return researches

    @staticmethod
    def parse_research_node(research_node):
        """Extract research data from XML node."""

        return research_node.attrib.copy()

    def get_rooms(self):
        """Get room designs from API."""

        # get room purchase
        rooms_purchase = self.get_rooms_purchase()

        params = {
            'version': self.__api_settings['RoomDesignSpriteVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/RoomService/ListRoomDesigns2'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms = []
        room_nodes = root.find('.//RoomDesigns')

        for room_node in room_nodes:
            # if room purchase, add node to room node
            room_purchase = next(
                (room_purchase for room_purchase in rooms_purchase if room_purchase['RoomDesignId'] == room_node.attrib['RootRoomDesignId']),
                None
            )
            if room_purchase:
                room_node.set('AvailabilityMask', room_purchase['AvailabilityMask'])

            room = self.parse_room_node(room_node)

            room['pixyship_xml_element'] = room_node  # custom field, return raw XML data too
            rooms.append(room)

        return rooms

    @staticmethod
    def parse_room_node(room_node):
        """Extract room data from XML node."""

        room = room_node.attrib.copy()

        missile_design_node = list(room_node.iter('MissileDesign'))
        if missile_design_node:
            room['MissileDesign'] = missile_design_node[0].attrib
        else:
            room['MissileDesign'] = None

        return room

    def get_rooms_purchase(self):
        """Get room designs from API."""

        params = {
            'version': self.__api_settings['RoomDesignPurchaseVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/RoomService/ListRoomDesignPurchase'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms_purchase = []
        room_purchase_nodes = root.find('.//RoomDesignPurchases')

        for room_purchase_node in room_purchase_nodes:
            room_purchase = self.parse_room_node(room_purchase_node)
            room_purchase['pixyship_xml_element'] = room_purchase_node  # custom field, return raw XML data too
            rooms_purchase.append(room_purchase)

        return rooms_purchase

    @staticmethod
    def parse_room_purchase_node(room_purchase_node):
        """Extract room purchase data from XML node."""

        return room_purchase_node.attrib.copy()

    def get_characters(self):
        """Get character designs from API."""

        params = {
            'version': self.__api_settings['CharacterDesignVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/CharacterService/ListAllCharacterDesigns2'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        characters = []
        character_nodes = root.find('.//CharacterDesigns')

        for character_node in character_nodes:
            character = self.parse_character_node(character_node)
            character['pixyship_xml_element'] = character_node  # custom field, return raw XML data too
            characters.append(character)

        return characters

    @staticmethod
    def parse_character_node(character_node):
        """Extract character data from XML node."""

        character = character_node.attrib.copy()

        character['CharacterParts'] = {}
        character_part_nodes = character_node.find('.//CharacterParts')
        for character_part_node in character_part_nodes:
            character_part = character_part_node.attrib
            character['CharacterParts'][character_part['CharacterPartType']] = character_part

        return character

    def get_collections(self):
        """Get collection designs from API."""

        params = {
            'version': self.__api_settings['CollectionDesignVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/CollectionService/ListAllCollectionDesigns'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        collections = []
        collection_nodes = root.find('.//CollectionDesigns')

        for collection_node in collection_nodes:
            collection = self.parse_collection_node(collection_node)
            collection['pixyship_xml_element'] = collection_node  # custom field, return raw XML data too
            collections.append(collection)

        return collections

    @staticmethod
    def parse_collection_node(collection_node):
        """Extract collection data from XML node."""

        return collection_node.attrib.copy()

    def get_items(self):
        """Get item designs from API."""

        params = {
            'version': self.__api_settings['ItemDesignVersion'],
            'languageKey': 'en'
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/ItemService/ListItemDesigns2'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        items = []
        item_nodes = root.find('.//ItemDesigns')

        for item_node in item_nodes:
            item = self.parse_item_node(item_node)
            item['pixyship_xml_element'] = item_node  # custom field, return raw XML data too
            items.append(item)

        return items

    @staticmethod
    def parse_item_node(item_node):
        """Extract item data from XML node."""

        return item_node.attrib.copy()

    def get_alliances(self, take=100):
        """Get alliances from API, top 100 by default."""

        params = {
            'version': self.__api_settings['ItemDesignVersion'],
            'take': take
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/AllianceService/ListAlliancesByRanking'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        alliances = []
        alliance_nodes = root.find('.//Alliances')

        for alliance_node in alliance_nodes:
            alliance = self.parse_alliance_node(alliance_node)
            alliance['pixyship_xml_element'] = alliance_node  # custom field, return raw XML data too
            alliances.append(alliance)

        return alliances

    @staticmethod
    def parse_alliance_node(alliance_node):
        """Extract alliance data from XML node."""

        return alliance_node.attrib.copy()

    def get_sales(self, item_id, max_sale_id=0, take=None):
        """Download sales for given item from PSS API."""

        sales = []

        # offset, API returns sales only by 20 by 20
        start = 0
        end = 20

        count = 0
        max_sale_id_reached = False
        while "sale_id from API not equal to given max_sale_id":

            params = {
                'itemDesignId': item_id,
                'saleStatus': 'Sold',
                'from': start,
                'to': end
            }

            # retrieve data as XML from Pixel Starships API
            endpoint = f'https://{self.server}/MarketService/ListSalesByItemDesignId'
            response = self.call(endpoint, params=params)
            root = ElementTree.fromstring(response.text)

            # parse HTTP body as XML and find sales nodes
            sale_nodes = root.find('.//Sales')

            # no more sales available
            if len(sale_nodes) == 0:
                break

            for sale_node in sale_nodes:
                sale_id = int(sale_node.get('SaleId'))
                sale = self.parse_sale_node(sale_node)

                if sale_id > max_sale_id:
                    sales.append(sale)
                else:
                    max_sale_id_reached = True
                    break

                count += 1
                if take and take == count:
                    max_sale_id_reached = True
                    break

            if max_sale_id_reached:
                break

            # next page
            start += 20
            end += 20

        return sales

    @staticmethod
    def parse_sale_node(sale_node):
        """Extract sale data from XML node."""

        return sale_node.attrib.copy()

    def get_alliance_users(self, alliance_id, skip=0, take=100):
        """Get alliance users from API, top 100 by default."""

        params = {
            'allianceId': alliance_id,
            'take': take,
            'skip': skip
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/AllianceService/ListUsers'
        response = self.call(endpoint, params=params, access=True)
        root = ElementTree.fromstring(response.text)

        users = []
        user_nodes = root.find('.//Users')

        for user_node in user_nodes:
            user = self.parse_user_node(user_node)
            user['pixyship_xml_element'] = user_node  # custom field, return raw XML data too
            users.append(user)

        return users

    def get_users(self, start=1, end=100):
        """Get users from API, top 100 by default."""

        params = {
            'from': start,
            'to': end
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/LadderService/ListUsersByRanking'
        response = self.call(endpoint, params=params, access=True)
        root = ElementTree.fromstring(response.text)

        users = []
        user_nodes = root.find('.//Users')

        for user_node in user_nodes:
            user = self.parse_user_node(user_node)
            user['pixyship_xml_element'] = user_node  # custom field, return raw XML data too
            users.append(user)

        return users

    @staticmethod
    def parse_user_node(user_node):
        """Extract user data from XML node."""

        return user_node.attrib.copy()

    def get_prestiges_character_to(self, character_id):
        """Get prestiges recipe creating given character from API."""

        params = {
            'characterDesignId': character_id
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/CharacterService/PrestigeCharacterTo'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        prestiges = []
        prestige_nodes = root.find('.//Prestiges')

        # it's possible to don't have prestiges for the given character
        if prestige_nodes:
            for prestige_node in prestige_nodes:
                prestige = self.parse_prestige_node(prestige_node)
                prestige['pixyship_xml_element'] = prestige_node  # custom field, return raw XML data too
                prestiges.append(prestige)

        return prestiges

    def get_prestiges_character_from(self, character_id):
        """Get prestiges recipe created with given character from API."""

        params = {
            'characterDesignId': character_id
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f'https://{self.server}/CharacterService/PrestigeCharacterFrom'
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        prestiges = []
        prestige_nodes = root.find('.//Prestiges')

        # it's possible to don't have prestiges for the given character
        if prestige_nodes:
            for prestige_node in prestige_nodes:
                prestige = self.parse_prestige_node(prestige_node)
                prestige['pixyship_xml_element'] = prestige_node  # custom field, return raw XML data too
                prestiges.append(prestige)

        return prestiges

    @staticmethod
    def parse_prestige_node(prestige_node):
        """Extract prestige data from XML node."""

        return prestige_node.attrib.copy()

    def get_stardate(self):
        """Compute Stardate."""

        utc_now = datetime.datetime.utcnow()
        today = datetime.date(utc_now.year, utc_now.month, utc_now.day)
        return (today - self.PSS_START_DATE).days

    def parse_sale_item_mask(self, sale_item_mask):
        """"From SaleItemMask determine Sale options."""

        equipment_mask = int(sale_item_mask)
        output = [int(x) for x in '{:05b}'.format(equipment_mask)]
        options = [self.IAP_OPTIONS_MASK_LOOKUP[4 - i] for i, b in enumerate(output) if b]

        # reverse order
        options.reverse()

        return options
