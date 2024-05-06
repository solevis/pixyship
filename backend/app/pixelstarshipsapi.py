import datetime
import hashlib
import random
import re
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

import requests
from flask import current_app

from app.api_errors import TOKEN_EXPIRED_REGEX
from app.constants import API_URLS, IAP_OPTIONS_MASK_LOOKUP, PSS_START_DATE
from app.ext import cache
from app.ext.db import db
from app.models import Device
from app.utils.pss import api_sleep


class PixelStarshipsApi:
    """
    Manage Pixel Starships API.
    TODO: migrate to pssapi library.
    """

    def __init__(self):
        if current_app.config.get("USE_STAGING_API"):
            self._main_pixelstarships_api_url = API_URLS.get("STAGING")
            # force staging URL and not get automatic ProductionServer from API
            self._forced_pixelstarships_api_url = API_URLS.get("STAGING")
        else:
            self._main_pixelstarships_api_url = API_URLS.get("MAIN")
            self._forced_pixelstarships_api_url = current_app.config.get("FORCED_PIXELSTARSHIPS_API_URL")

        self._device_next_index = 0
        self._devices = None

        self._api_settings = self.get_api_settings()

        if not self._forced_pixelstarships_api_url:
            self.server = self._api_settings["ProductionServer"]
        else:
            o = urlparse(self._forced_pixelstarships_api_url)
            self.server = o.hostname

    @property
    def maintenance_message(self):
        return self._api_settings["MaintenanceMessage"]

    @property
    def devices(self):
        if not self._devices:
            self._devices = self.get_devices()

        return self._devices

    def get_devices(self):
        """Get generated devices from database."""

        devices = Device.query.all()
        if len(devices) < current_app.config["MIN_DEVICES"]:
            for _x in range(0, current_app.config["MIN_DEVICES"] - len(devices)):
                utc_now = datetime.datetime.utcnow()
                client_datetime = utc_now.strftime("%Y-%m-%dT%H:%M:%S")

                device_key, device_checksum = self.generate_device(client_datetime)
                new_device = Device(
                    key=device_key,
                    client_datetime=client_datetime,
                    checksum=device_checksum,
                )
                db.session.add(new_device)

            db.session.commit()
            devices = Device.query.all()

        return devices

    @cache.cached(timeout=60 * 60 * 12, key_prefix="api_settings")
    def get_api_settings(self):
        """Get last game settings from API."""

        params = {"languageKey": "en", "deviceType": "DeviceTypeAndroid"}

        if self._forced_pixelstarships_api_url:
            # call API with forced URL
            endpoint = urljoin(self._forced_pixelstarships_api_url, "SettingService/GetLatestVersion3")
            response = self.call(endpoint, params=params)
            root = ElementTree.fromstring(response.text)
            setting_element = root.find(".//Setting")
            if setting_element is None:
                current_app.logger.error(f"Error when parsing response: {response.text}")
                return {}
            settings = setting_element.attrib

            return settings

        # call API with classic URL, in case of error, try with alternative
        endpoint = urljoin(self._main_pixelstarships_api_url, "SettingService/GetLatestVersion3")
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        setting_element = root.find(".//Setting")
        if setting_element is None:
            current_app.logger.error(f"Error when parsing response: {response.text}")
            return {}

        settings = setting_element.attrib
        fixed_endpoint = urljoin(
            f'https://{settings["ProductionServer"]}',
            "SettingService/GetLatestVersion3",
        )

        if fixed_endpoint != endpoint:
            response = self.call(fixed_endpoint, params=params)
            root = ElementTree.fromstring(response.text)
            settings = root.find(".//Setting").attrib

        return settings

    def api_url(self, path: tuple[str, str], server: str | None = None, **params):
        """Compute endpoint URL with parameters."""

        # if url need version, get it from settings (retrieved from API)
        if path[1]:
            params["version"] = self._api_settings[path[1]] if hasattr(self, "settings") else 1

        return (server or self.server) + path[0].format(**params)

    def call(self, endpoint, params, need_token=False, force_token_generation=False):
        """Make a PSS API call."""

        device = None
        token = None

        # don't use SAVY_PUBLIC_API_TOKEN on staging (it doesn't work)
        if current_app.config.get("USE_STAGING_API"):
            force_token_generation = True

        if need_token and (not current_app.config["SAVY_PUBLIC_API_TOKEN"] or force_token_generation):
            # protected endpoint, add device access token...
            device = self.get_device()
            token = device.get_token()
        elif current_app.config["SAVY_PUBLIC_API_TOKEN"]:
            # ...otherwise use Savy provided token if present
            token = current_app.config["SAVY_PUBLIC_API_TOKEN"]

        if token:
            params["accessToken"] = token

        response = self.get_response(endpoint, params)

        # expired token, regenerate tokens and retry
        if device and re.compile(TOKEN_EXPIRED_REGEX).search(response.text):
            device.cycle_token()
            params["accessToken"] = device.get_token()
            response = self.get_response(endpoint, params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    @staticmethod
    def get_response(endpoint, params):
        """Get response from API."""

        try:
            response = requests.get(endpoint, params=params)
        except requests.exceptions.ConnectionError as e:
            current_app.logger.info(f"Connection error, retry: {e}")
            api_sleep(10, force_sleep=True)
            response = requests.get(endpoint, params=params)

        return response

    @staticmethod
    def create_device_key():
        """Generate random device key."""

        sequence = "0123456789abcdef"
        return "".join(
            random.choice(sequence)
            + random.choice("26ae")
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence)
            + random.choice(sequence),
        )

    def generate_device(self, client_datetime):
        """Generate new device key/checksum."""

        device_key = self.create_device_key()
        device_type = "DeviceTypeMac"
        checksum_key = current_app.config["DEVICE_LOGIN_CHECKSUM_KEY"]

        device_checksum = hashlib.md5(
            f"{device_key}{client_datetime}{device_type}{checksum_key}savysoda".encode(),
        ).hexdigest()

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

    def get_device_token(self, device_key, client_datetime, device_checksum):
        """Get device token from API for the given generated device."""

        params = {
            "deviceKey": device_key,
            "checksum": device_checksum,
            "isJailBroken": "false",
            "deviceType": "DeviceTypeMac",
            "languagekey": "en",
            "advertisingKey": '""',
            "clientDateTime": client_datetime,
        }

        endpoint = f"https://{self.server}/UserService/DeviceLogin11"
        response = requests.post(endpoint, params=params)

        root = ElementTree.fromstring(response.content.decode("utf-8"))
        user_login_node = root.find(".//UserLogin")

        if user_login_node is None:
            current_app.logger.error(f"Error when parsing response: {response.text}")
            return None

        return user_login_node.attrib["accessToken"]

    def inspect_ship(self, user_id):
        """Get player ship data from API."""

        params = {
            "userId": user_id,
            "designVersion": self._api_settings["ShipDesignVersion"],
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ShipService/InspectShip2"
        response = self.call(endpoint, params=params, need_token=True, force_token_generation=True)
        root = ElementTree.fromstring(response.text)

        inspect_ship = {
            "User": root.find(".//User").attrib.copy(),
            "Ship": root.find(".//Ship").attrib.copy(),
        }

        inspect_ship["User"]["pixyship_xml_element"] = root.find(".//User")
        inspect_ship["Ship"]["pixyship_xml_element"] = root.find(".//Ship")

        # get rooms
        rooms_node = root.find(".//Rooms")
        inspect_ship["Ship"]["Rooms"] = []
        for room_node in rooms_node:
            room = room_node.attrib.copy()
            room["pixyship_xml_element"] = room_node
            inspect_ship["Ship"]["Rooms"].append(room)

        return inspect_ship

    def ship_details(self, user_id):
        """Get player ship details from API."""

        params = {
            "UserId": user_id,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/PublicService/GetShipDetails"
        response = self.call(endpoint, params=params, need_token=True)
        root = ElementTree.fromstring(response.text)

        ship_node = root.find(".//Ship")
        ship = ship_node.attrib.copy()
        ship["pixyship_xml_element"] = ship_node

        user_node = root.find(".//User")
        user = user_node.attrib.copy()
        user["pixyship_xml_element"] = user_node

        return ship, user

    def ship_room_details(self, user_id):
        """Get player ship room details from API."""

        params = {
            "UserId": user_id,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/PublicService/GetShipRoomDetails"
        response = self.call(endpoint, params=params, need_token=True)
        root = ElementTree.fromstring(response.text)

        ship_room_details_node = root.find(".//Rooms")
        ship_room_details = []
        for room_node in ship_room_details_node:
            room = room_node.attrib.copy()
            room["pixyship_xml_element"] = room_node
            ship_room_details.append(room)

        return ship_room_details

    def search_users(self, user_name, exact_match=False):
        """Get player ship data from API."""

        params = {
            "searchstring": user_name,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/UserService/SearchUsers"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        users = []

        if exact_match:
            user_node = root.find(f".//User[@Name={user_name!r}]")

            if user_node:
                user = self.parse_user_node(user_node)
                user["pixyship_xml_element"] = user_node  # custom field, return raw XML data too
                users.append(user)
        else:
            users_node = root.find(".//Users")
            for user_node in users_node:
                user = self.parse_user_node(user_node)

                user["pixyship_xml_element"] = user_node  # custom field, return raw XML data too
                users.append(user)

        return users

    @staticmethod
    def parse_user_node(user_node):
        """Extract user data from XML node."""

        return user_node.attrib

    def get_dailies(self):
        """Get dailies from settings service from API."""

        params = {"languageKey": "en", "deviceType": "DeviceTypeAndroid"}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/LiveOpsService/GetTodayLiveOps2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        dailies_node = root.find(".//LiveOps")

        dailies = dailies_node.attrib.copy()
        dailies["pixyship_xml_element"] = dailies_node  # custom field, return raw XML data too

        return dailies

    def get_sprites(self):
        """Get sprites from API."""

        params = {
            "designVersion": self._api_settings["FileVersion"],
            "deviceType": "DeviceTypeAndroid",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/FileService/ListSprites"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        sprites = []
        sprite_nodes = root.find(".//Sprites")

        for sprite_node in sprite_nodes:
            sprite = self.parse_sprite_node(sprite_node)
            sprite["pixyship_xml_element"] = sprite_node  # custom field, return raw XML data too
            sprites.append(sprite)

        return sprites

    @staticmethod
    def parse_sprite_node(sprite_node):
        """Extract character data from XML node."""

        return sprite_node.attrib.copy()

    def get_rooms_sprites(self):
        """Get rooms sprites from API."""

        params = {"designVersion": self._api_settings["RoomDesignSpriteVersion"]}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/RoomDesignSpriteService/ListRoomDesignSprites"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms_sprites = []
        room_sprites_nodes = root.find(".//RoomDesignSprites")

        for room_sprites_node in room_sprites_nodes:
            room_sprites = self.parse_room_sprite_node(room_sprites_node)
            room_sprites["pixyship_xml_element"] = room_sprites_node  # custom field, return raw XML data too
            rooms_sprites.append(room_sprites)

        return rooms_sprites

    @staticmethod
    def parse_room_sprite_node(room_sprite_node):
        """Extract room sprite data from XML node."""

        return room_sprite_node.attrib.copy()

    def get_skinsets(self):
        """Get skinsets from API."""

        params = {
            "designVersion": self._api_settings["SkinSetVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/UserService/ListSkinsets2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        skinsets = []
        skinset_nodes = root.find(".//SkinSets")

        for skinset_node in skinset_nodes:
            skinset = self.parse_skinset_node(skinset_node)
            skinset["pixyship_xml_element"] = skinset_node

            skinsets.append(skinset)

        return skinsets

    def get_skins(self):
        """Get skins from API."""

        params = {
            "designVersion": self._api_settings["SkinVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/UserService/ListSkins2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        skins = []
        skin_nodes = root.find(".//Skins")

        for skinset_node in skin_nodes:
            skin = self.parse_skin_node(skinset_node)
            skin["pixyship_xml_element"] = skinset_node

            skins.append(skin)

        return skins

    @staticmethod
    def parse_skinset_node(skinset_node):
        """Extract skinset data from XML node."""

        return skinset_node.attrib.copy()

    @staticmethod
    def parse_skin_node(skin_node):
        """Extract skin data from XML node."""

        return skin_node.attrib.copy()

    def get_ships(self):
        """Get ships designs from API."""

        params = {
            "designVersion": self._api_settings["ShipDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ShipService/ListAllShipDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        ships = []
        ship_nodes = root.find(".//ShipDesigns")

        for ship_node in ship_nodes:
            ship = self.parse_ship_node(ship_node)
            ship["pixyship_xml_element"] = ship_node  # custom field, return raw XML data too
            ships.append(ship)

        return ships

    @staticmethod
    def parse_ship_node(ship_node):
        """Extract character data from XML node."""

        return ship_node.attrib.copy()

    def get_researches(self):
        """Get research designs from API."""

        params = {
            "designVersion": self._api_settings["ResearchDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ResearchService/ListAllResearchDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        researches = []
        research_nodes = root.find(".//ResearchDesigns")

        for research_node in research_nodes:
            research = self.parse_research_node(research_node)
            research["pixyship_xml_element"] = research_node  # custom field, return raw XML data too
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
            "designVersion": self._api_settings["RoomDesignSpriteVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/RoomService/ListRoomDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms = []
        room_nodes = root.find(".//RoomDesigns")

        for room_node in room_nodes:
            # if room purchase, add node to room node
            room_purchase = next(
                (
                    room_purchase
                    for room_purchase in rooms_purchase
                    if room_purchase["RoomDesignId"] == room_node.attrib["RootRoomDesignId"]
                ),
                None,
            )

            if room_purchase:
                room_node.set("AvailabilityMask", room_purchase["AvailabilityMask"])

            room = self.parse_room_node(room_node)

            room["pixyship_xml_element"] = room_node  # custom field, return raw XML data too
            rooms.append(room)

        return rooms

    @staticmethod
    def parse_room_node(room_node):
        """Extract room data from XML node."""

        room = room_node.attrib.copy()

        missile_design_node = list(room_node.iter("MissileDesign"))
        if missile_design_node:
            room["MissileDesign"] = missile_design_node[0].attrib
        else:
            room["MissileDesign"] = None

        return room

    def get_missile_designs(self):
        """Get missile designs from API."""

        params = {
            "designVersion": self._api_settings["MissileDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/RoomService/ListMissileDesigns"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        missile_designs = []
        missile_design_nodes = root.find(".//MissileDesigns")

        for missile_design_node in missile_design_nodes:
            missile_design = self.parse_missile_design_node(missile_design_node)

            missile_design["pixyship_xml_element"] = missile_design_node  # custom field, return raw XML data too
            missile_designs.append(missile_design)

        return missile_designs

    @staticmethod
    def parse_missile_design_node(missile_design_node):
        """Extract missile design data from XML node."""

        missile_design = missile_design_node.attrib.copy()
        return missile_design

    def get_crafts(self):
        """Get crafts designs from API."""

        # get missile designs
        missile_designs = self.get_missile_designs()

        # get item designs
        item_designs = self.get_items()

        params = {
            "designVersion": self._api_settings["CraftDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/RoomService/ListCraftDesigns"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        crafts = []
        craft_nodes = root.find(".//CraftDesigns")

        for craft_node in craft_nodes:
            missile_design = next(
                (
                    missile_design
                    for missile_design in missile_designs
                    if missile_design["MissileDesignId"] == craft_node.attrib["MissileDesignId"]
                ),
                None,
            )

            if not missile_design:
                current_app.logger.error(
                    "Cannot retrieve craft MissileDesign for MissileDesignId {}".format(
                        craft_node.attrib["MissileDesignId"],
                    ),
                )
                continue

            item_design = next(
                (
                    item_design
                    for item_design in item_designs
                    if item_design["CraftDesignId"] == craft_node.attrib["CraftDesignId"]
                ),
                None,
            )

            if item_design:
                craft_node.set("ReloadModifier", item_design["ReloadModifier"])

            craft_node.append(missile_design["pixyship_xml_element"])
            craft = self.parse_craft_node(craft_node)

            craft["pixyship_xml_element"] = craft_node  # custom field, return raw XML data too
            crafts.append(craft)

        return crafts

    @staticmethod
    def parse_craft_node(craft_node):
        """Extract craft data from XML node."""

        craft = craft_node.attrib.copy()

        missile_design_node = list(craft_node.iter("MissileDesign"))
        craft["MissileDesign"] = missile_design_node[0].attrib

        return craft

    def get_missiles(self):
        """Get missiles designs from API."""

        # get room purchase
        missile_designs = self.get_missile_designs()

        # get item designs
        item_designs = self.get_items()

        params = {
            "designVersion": self._api_settings["ItemDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ItemService/ListItemDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        missiles = []
        item_nodes = root.find(".//ItemDesigns")

        for item_node in item_nodes:
            if item_node.attrib["ItemType"] != "Missile":
                continue

            missile_design = next(
                (
                    missile_design
                    for missile_design in missile_designs
                    if missile_design["MissileDesignId"] == item_node.attrib["MissileDesignId"]
                ),
                None,
            )

            if not missile_design:
                current_app.logger.error(
                    "Cannot retrieve missile MissileDesign for MissileDesignId {}".format(
                        item_node.attrib["MissileDesignId"],
                    ),
                )
                continue

            item_design = next(
                (
                    item_design
                    for item_design in item_designs
                    if item_design["CraftDesignId"] == item_node.attrib["CraftDesignId"]
                ),
                None,
            )

            if item_design:
                item_node.set("ReloadModifier", item_design["ReloadModifier"])

            item_node.append(missile_design["pixyship_xml_element"])
            missile = self.parse_missile_node(item_node)

            missile["pixyship_xml_element"] = item_node  # custom field, return raw XML data too
            missiles.append(missile)

        return missiles

    @staticmethod
    def parse_missile_node(missile_node):
        """Extract missile data from XML node."""

        missile = missile_node.attrib.copy()

        missile_design_node = list(missile_node.iter("MissileDesign"))
        missile["MissileDesign"] = missile_design_node[0].attrib

        return missile

    def get_rooms_purchase(self):
        """Get room designs from API."""

        params = {
            "designVersion": self._api_settings["RoomDesignPurchaseVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/RoomService/ListRoomDesignPurchase"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        rooms_purchase = []
        room_purchase_nodes = root.find(".//RoomDesignPurchases")

        for room_purchase_node in room_purchase_nodes:
            room_purchase = self.parse_room_node(room_purchase_node)
            room_purchase["pixyship_xml_element"] = room_purchase_node  # custom field, return raw XML data too
            rooms_purchase.append(room_purchase)

        return rooms_purchase

    @staticmethod
    def parse_room_purchase_node(room_purchase_node):
        """Extract room purchase data from XML node."""

        return room_purchase_node.attrib.copy()

    def get_characters(self):
        """Get character designs from API."""

        params = {
            "designVersion": self._api_settings["CharacterDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/CharacterService/ListAllCharacterDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        characters = []
        character_nodes = root.find(".//CharacterDesigns")

        for character_node in character_nodes:
            character = self.parse_character_node(character_node)
            character["pixyship_xml_element"] = character_node  # custom field, return raw XML data too
            characters.append(character)

        return characters

    @staticmethod
    def parse_character_node(character_node):
        """Extract character data from XML node."""

        character = character_node.attrib.copy()

        character["CharacterParts"] = {}
        character_part_nodes = character_node.find(".//CharacterParts")
        for character_part_node in character_part_nodes:
            character_part = character_part_node.attrib
            character["CharacterParts"][character_part["CharacterPartType"]] = character_part

        return character

    def get_collections(self):
        """Get collection designs from API."""

        params = {
            "designVersion": self._api_settings["CollectionDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/CollectionService/ListAllCollectionDesigns"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        collections = []
        collection_nodes = root.find(".//CollectionDesigns")

        for collection_node in collection_nodes:
            collection = self.parse_collection_node(collection_node)
            collection["pixyship_xml_element"] = collection_node  # custom field, return raw XML data too
            collections.append(collection)

        return collections

    @staticmethod
    def parse_collection_node(collection_node):
        """Extract collection data from XML node."""

        return collection_node.attrib.copy()

    def get_items(self):
        """Get item designs from API."""

        params = {
            "designVersion": self._api_settings["ItemDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ItemService/ListItemDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        items = []
        item_nodes = root.find(".//ItemDesigns")

        for item_node in item_nodes:
            item = self.parse_item_node(item_node)
            item["pixyship_xml_element"] = item_node  # custom field, return raw XML data too
            items.append(item)

        return items

    @staticmethod
    def parse_item_node(item_node):
        """Extract item data from XML node."""

        return item_node.attrib.copy()

    def get_alliances(self, take=100):
        """Get alliances from API, top 100 by default."""

        params = {
            "designVersion": self._api_settings["ItemDesignVersion"],
            "take": take,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/AllianceService/ListAlliancesByRanking"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        alliances = []
        alliance_nodes = root.find(".//Alliances")

        for alliance_node in alliance_nodes:
            alliance = self.parse_alliance_node(alliance_node)
            alliance["pixyship_xml_element"] = alliance_node  # custom field, return raw XML data too
            alliances.append(alliance)

        return alliances

    @staticmethod
    def parse_alliance_node(alliance_node):
        """Extract alliance data from XML node."""

        return alliance_node.attrib.copy()

    def get_sales(self, item_id, max_sale_id=0, take=None):
        """Download sales for given item from PSS API."""

        sales = []

        # offset, API returns sales only 20 by 20
        start = 0
        end = 20

        count = 0
        errors = 0
        max_sale_id_reached = False
        while "sale_id from API not equal to given max_sale_id":
            params = {
                "itemDesignId": item_id,
                "saleStatus": "Sold",
                "from": start,
                "to": end,
            }

            current_app.logger.info(f"retrieve sales of {item_id} from {start} to {end}")

            # retrieve data as XML from Pixel Starships API
            endpoint = f"https://{self.server}/MarketService/ListSalesByItemDesignId"
            response = self.call(endpoint, params=params)

            if response.status_code == 400:
                current_app.logger.error(f"Response in error: {response.text}")
                errors += 1

                if errors == 3:
                    # three times the call is in errors, skip this item
                    # clear the sales to keep the max_sale_id correct for the next run
                    sales.clear()
                    break

                # too many request, wait a little, and try again
                api_sleep(30, force_sleep=True)
                continue

            root = ElementTree.fromstring(response.text)

            # parse HTTP body as XML and find sales nodes
            sale_nodes = root.find(".//Sales")

            # error when parsing the response
            if sale_nodes is None:
                current_app.logger.error(f"Error when parsing response: {response.text}")
                errors += 1

                if errors == 3:
                    # three times the call is in errors, skip this item
                    # clear the sales to keep the max_sale_id correct for the next run
                    sales.clear()
                    break

                api_sleep(3, force_sleep=True)
                continue

            # no more sales available
            if len(sale_nodes) == 0:
                break

            for sale_node in sale_nodes:
                sale_id = int(sale_node.get("SaleId"))
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

            api_sleep(3, force_sleep=True)

        return sales

    @staticmethod
    def parse_sale_node(sale_node):
        """Extract sale data from XML node."""

        return sale_node.attrib.copy()

    def get_market_messages(self, item_id):
        """Download market messages for given item from PSS API."""

        market_messages = []

        params = {
            "itemDesignId": item_id,
            "currencyType": "Unknown",
            "itemSubType": "None",
            "rarity": "None",
            "userId": 0,
            "skip": 0,
            "take": 999999,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/MessageService/ListActiveMarketplaceMessages5"
        response = self.call(endpoint, params=params, need_token=True, force_token_generation=True)

        if response.status_code == 400:
            current_app.logger.error(f"Response in error: {response.text}")

            # too many request, wait a little, and try again
            api_sleep(10, force_sleep=True)

            return []

        root = ElementTree.fromstring(response.text)

        # parse HTTP body as XML and find market_messages nodes
        market_messsage_nodes = root.find(".//Messages")

        # error when parsing the response
        if market_messsage_nodes is None:
            current_app.logger.error(f"Error when parsing response: {response.text}")

            return []

        for market_message_node in market_messsage_nodes:
            market_message = self.parse_market_message_node(market_message_node)
            market_messages.append(market_message)

        return market_messages

    @staticmethod
    def parse_market_message_node(message_node):
        """Extract sale data from XML node."""

        return message_node.attrib.copy()

    def get_alliance_users(self, alliance_id, skip=0, take=100):
        """Get alliance users from API, top 100 by default."""

        params = {"allianceId": alliance_id, "take": take, "skip": skip}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/AllianceService/ListUsers"
        response = self.call(endpoint, params=params, need_token=True)
        root = ElementTree.fromstring(response.text)

        users = []
        user_nodes = root.find(".//Users")

        for user_node in user_nodes:
            user = self.parse_user_node(user_node)
            user["pixyship_xml_element"] = user_node  # custom field, return raw XML data too
            users.append(user)

        return users

    def get_users(self, start=1, end=100):
        """Get users from API, top 100 by default."""

        params = {"from": start, "to": end}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/LadderService/ListUsersByRanking"
        response = self.call(endpoint, params=params, need_token=True)
        root = ElementTree.fromstring(response.text)

        users = []
        user_nodes = root.find(".//Users")

        for user_node in user_nodes:
            user = self.parse_user_node(user_node)
            user["pixyship_xml_element"] = user_node  # custom field, return raw XML data too
            users.append(user)

        return users

    def get_prestiges_character_to(self, character_id):
        """Get prestiges recipe creating given character from API."""

        params = {"characterDesignId": character_id}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/CharacterService/PrestigeCharacterTo"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        prestiges = []
        prestige_nodes = root.find(".//Prestiges")

        # it's possible to don't have prestiges for the given character
        if prestige_nodes:
            for prestige_node in prestige_nodes:
                prestige = self.parse_prestige_node(prestige_node)
                prestige["pixyship_xml_element"] = prestige_node  # custom field, return raw XML data too
                prestiges.append(prestige)

        return prestiges

    def get_prestiges_character_from(self, character_id):
        """Get prestiges recipe created with given character from API."""

        params = {"characterDesignId": character_id}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/CharacterService/PrestigeCharacterFrom"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        prestiges = []
        prestige_nodes = root.find(".//Prestiges")

        # it's possible to don't have prestiges for the given character
        if prestige_nodes:
            for prestige_node in prestige_nodes:
                prestige = self.parse_prestige_node(prestige_node)
                prestige["pixyship_xml_element"] = prestige_node  # custom field, return raw XML data too
                prestiges.append(prestige)

        return prestiges

    @staticmethod
    def parse_prestige_node(prestige_node):
        """Extract prestige data from XML node."""

        return prestige_node.attrib.copy()

    @staticmethod
    def get_stardate():
        """Compute Stardate."""

        utc_now = datetime.datetime.utcnow()
        today = datetime.date(utc_now.year, utc_now.month, utc_now.day)
        return (today - PSS_START_DATE).days

    @staticmethod
    def parse_sale_item_mask(sale_item_mask):
        """ "From SaleItemMask determine Sale options."""

        equipment_mask = int(sale_item_mask)
        output = [int(x) for x in f"{equipment_mask:05b}"]

        options = []
        for index, _value in enumerate(output):
            if index > 4:
                break
            options.append(IAP_OPTIONS_MASK_LOOKUP[4 - index])

        # reverse order
        options.reverse()

        return options

    def get_trainings(self):
        """Get trainings data from API."""

        params = {
            "designVersion": self._api_settings["TrainingDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/TrainingService/ListAllTrainingDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        trainings = []
        training_nodes = root.find(".//TrainingDesigns")

        if training_nodes:
            for training_node in training_nodes:
                training = self.parse_training_node(training_node)
                training["pixyship_xml_element"] = training_node  # custom field, return raw XML data too
                trainings.append(training)

        return trainings

    @staticmethod
    def parse_training_node(training_node):
        """Extract training data from XML node."""

        return training_node.attrib.copy()

    def get_achievements(self):
        """Get achievements data from API."""

        params = {
            "designVersion": self._api_settings["AchievementDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/AchievementService/ListAchievementDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        achievements = []
        achievement_nodes = root.find(".//AchievementDesigns")

        if achievement_nodes:
            for achievement_node in achievement_nodes:
                achievement = self.parse_achievement_node(achievement_node)
                achievement["pixyship_xml_element"] = achievement_node  # custom field, return raw XML data too
                achievements.append(achievement)

        return achievements

    @staticmethod
    def parse_achievement_node(achievement_node):
        """Extract achievement data from XML node."""

        return achievement_node.attrib.copy()

    def get_situations(self):
        """Get situations data from API."""

        params = {
            "designVersion": self._api_settings["SituationDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/SituationService/ListSituationDesigns"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        situations = []
        situation_nodes = root.find(".//SituationDesigns")

        if situation_nodes:
            for situation_node in situation_nodes:
                situation = self.parse_situation_node(situation_node)
                situation["pixyship_xml_element"] = situation_node  # custom field, return raw XML data too
                situations.append(situation)

        return situations

    @staticmethod
    def parse_situation_node(situation_node):
        """Extract situation data from XML node."""

        return situation_node.attrib.copy()

    def get_promotions(self):
        """Get promotions data from API."""

        params = {
            "designVersion": self._api_settings["PromotionDesignVersion"],
            "languageKey": "en",
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/PromotionService/ListAllPromotionDesigns2"
        response = self.call(endpoint, params=params)
        root = ElementTree.fromstring(response.text)

        promotions = []
        promotion_nodes = root.find(".//PromotionDesigns")

        if promotion_nodes:
            for promotion_node in promotion_nodes:
                promotion = self.parse_situation_node(promotion_node)
                promotion["pixyship_xml_element"] = promotion_node  # custom field, return raw XML data too
                promotions.append(promotion)

        return promotions

    @staticmethod
    def parse_promotion_node(promotion_node):
        """Extract promotion data from XML node."""

        return promotion_node.attrib.copy()

    def get_star_system_markers(self):
        """Get Star System Markers data from API."""

        params = {"languageKey": "en"}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/GalaxyService/ListStarSystemMarkers"
        response = self.call(endpoint, params=params, need_token=True)
        root = ElementTree.fromstring(response.text)

        markers = []
        markers_nodes = root.find(".//StarSystemMarkers")

        if markers_nodes:
            for marker_node in markers_nodes:
                marker = self.parse_star_system_marker_node(marker_node)
                marker["pixyship_xml_element"] = marker_node  # custom field, return raw XML data too
                markers.append(marker)

        return markers

    @staticmethod
    def parse_star_system_marker_node(marker_node):
        """Extract Star System Marker data from XML node."""

        return marker_node.attrib.copy()
