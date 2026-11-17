import datetime
import hashlib
import random
import re
import uuid
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

import requests
from flask import current_app
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.api_errors import TOKEN_EXPIRED_REGEX
from app.constants import API_URLS, IAP_OPTIONS_MASK_LOOKUP, PSS_START_DATE
from app.ext import cache
from app.ext.db import db
from app.models import Device
from app.utils.pss import api_sleep, convert_datetime_to_iso

# (connect, read) timeouts in seconds for PSS API calls, so a hanging call can't block a worker forever
REQUEST_TIMEOUT = (10, 60)

# retry connection errors and transient server errors, with an exponential backoff (2s, 4s, 8s)
REQUEST_RETRY = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=(502, 503, 504),
    allowed_methods=frozenset({"GET"}),
    raise_on_status=False,
)

_http_session: requests.Session | None = None


def get_http_session() -> requests.Session:
    """Get the process-wide HTTP session, created lazily (after a worker fork), to reuse connections."""
    global _http_session  # noqa: PLW0603

    if _http_session is None:
        session = requests.Session()
        session.mount("https://", HTTPAdapter(max_retries=REQUEST_RETRY))
        session.mount("http://", HTTPAdapter(max_retries=REQUEST_RETRY))
        _http_session = session

    return _http_session


class PixelStarshipsApi:
    """Manage Pixel Starships API."""

    def __init__(self) -> None:
        if current_app.config.get("USE_STAGING_API"):
            self._main_pixelstarships_api_url = API_URLS.get("STAGING")
            # force staging URL and not get automatic ProductionServer from API
            self._forced_pixelstarships_api_url = API_URLS.get("STAGING")
        else:
            self._main_pixelstarships_api_url = API_URLS.get("MAIN")
            self._forced_pixelstarships_api_url = current_app.config.get("FORCED_PIXELSTARSHIPS_API_URL")

        # random first device, so processes started together spread their calls over devices
        self._device_next_index: int | None = None
        self._devices: list[Device] | None = None
        self._api_settings: dict = self.get_api_settings()

        if not self._forced_pixelstarships_api_url:
            self.server: str = self._api_settings["ProductionServer"]
        else:
            o = urlparse(self._forced_pixelstarships_api_url)
            if o.hostname is None:
                msg = f"Invalid URL: {self._forced_pixelstarships_api_url}"
                raise ValueError(msg)

            self.server = o.hostname

    @property
    def maintenance_message(self) -> str:
        """Get maintenance message from API."""
        return self._api_settings["MaintenanceMessage"]

    @property
    def devices(self) -> list[Device]:
        """Get generated devices."""
        if not self._devices:
            self._devices = self.get_devices()

        return self._devices

    def get_devices(self) -> list[Device]:
        """Get generated devices from database."""
        devices = Device.query.all()
        if len(devices) < current_app.config["MIN_DEVICES"]:
            for _x in range(current_app.config["MIN_DEVICES"] - len(devices)):
                utc_now = datetime.datetime.now(tz=datetime.UTC)
                client_datetime = utc_now.strftime("%Y-%m-%dT%H:%M:%S")

                device_key, device_checksum = self.generate_device_key_checksum(client_datetime)
                new_device = Device(
                    key=device_key,
                    client_datetime=client_datetime,
                    checksum=device_checksum,
                )
                db.session.add(new_device)

            db.session.commit()
            devices = Device.query.all()

        return devices

    # don't cache empty settings (parsing error, maintenance...), it would break every API call for 12 hours
    @cache.cached(timeout=60 * 60 * 12, key_prefix="api_settings", response_filter=bool)
    def get_api_settings(self) -> dict:
        """Get last game settings from API."""
        params = {"languageKey": "en", "deviceType": "DeviceTypeAndroid"}

        # Determine the appropriate URL to use
        url = (
            self._forced_pixelstarships_api_url
            if self._forced_pixelstarships_api_url
            else self._main_pixelstarships_api_url
        )
        settings = self.fetch_settings(url, params)  # type: ignore[arg-type]

        # If the server has changed, fetch the settings again
        if "ProductionServer" in settings and url != f"https://{settings['ProductionServer']}":
            settings = self.fetch_settings(f"https://{settings['ProductionServer']}", params)

        return settings

    def fetch_settings(self, url: str, params: dict) -> dict:
        """Fetch settings from the given URL."""
        endpoint = urljoin(url, "SettingService/GetLatestVersion3")
        response = self.call(endpoint, params=params)
        root = ET.fromstring(response.text)
        setting_element = root.find(".//Setting")

        if setting_element is None:
            current_app.logger.error("Error when parsing response: %s", response.text)
            return {}

        return setting_element.attrib

    def call(
        self, endpoint: str, params: dict, need_token: bool = False, force_token_generation: bool = False
    ) -> Response:
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
            device.renew_token()
            params["accessToken"] = device.get_token()
            response = self.get_response(endpoint, params)

        if response.encoding is None:
            response.encoding = "utf-8"

        return response

    @staticmethod
    def get_response(endpoint: str, params: dict) -> Response:
        """Get response from API, connection errors and transient server errors are retried by the session."""
        return get_http_session().get(endpoint, params=params, timeout=REQUEST_TIMEOUT)

    @staticmethod
    def create_device_key() -> str:
        """Generate random device key."""
        return str(uuid.uuid4())

    def generate_device_key_checksum(self, client_datetime: str) -> tuple[str, str]:
        """Generate new device key/checksum."""
        device_key = self.create_device_key()
        device_type = "DeviceTypeAndroid"
        checksum_key = current_app.config["DEVICE_LOGIN_CHECKSUM_KEY"]

        device_checksum = hashlib.md5(
            f"{device_key}{client_datetime}{device_type}{checksum_key}".encode(),
        ).hexdigest()

        return device_key, device_checksum

    def get_device(self) -> Device:
        """Get the next device."""
        devices = self.devices

        index = random.randrange(len(devices)) if self._device_next_index is None else self._device_next_index
        if index >= len(devices):
            index = 0

        device = devices[index]
        self._device_next_index = index + 1

        device = db.session.merge(device)
        db.session.refresh(device)

        return device

    def get_device_token(self, device_key: str, client_datetime: str, device_checksum: str) -> tuple[str, str] | None:
        """Get device (access_token, user_id) from API for the given generated device."""
        # Convert client_datetime str in ISO
        client_datetime_str = convert_datetime_to_iso(client_datetime)

        device_type = "DeviceTypeAndroid"

        # Prepare the request data for DeviceLogin17
        data = {
            "DeviceType": device_type,
            "DeviceKey": device_key,
            "ClientDateTime": client_datetime_str,
            "Checksum": device_checksum,
            "IsJailBroken": "false",
            "Signal": "false",
            "LanguageKey": "en",
            "AdvertisingKey": "",
            "AccessToken": "00000000-0000-0000-0000-000000000000",
            "RefreshToken": "",
            "UserDeviceInfo": {
                "OsVersion": "AD12",
                "OSBuild": "0",
                "DeviceName": "AD123",
                "Locale": "en",
                "ClientBuild": "17180",
                "ClientVersion": "0.999.43",
            },
        }

        # Prepare URI parameters
        uri_params = {
            "AccessToken": "00000000-0000-0000-0000-000000000000",
            "AdvertisingKey": "",
            "Checksum": device_checksum,
            "ClientDateTime": client_datetime_str,
            "DeviceKey": device_key,
            "DeviceType": device_type,
            "IsJailBroken": "false",
            "LanguageKey": "en",
            "Signal": "false",
        }

        endpoint = f"https://{self.server}/UserService/DeviceLogin17"
        headers = {
            "User-Agent": "UnityPlayer/2021.3.33f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)",
            "Content-Type": "application/json",
        }

        response = get_http_session().post(
            endpoint, headers=headers, json=data, params=uri_params, timeout=REQUEST_TIMEOUT
        )

        root = ET.fromstring(response.content.decode("utf-8"))
        user_login_node = root.find(".//UserLogin")

        if user_login_node is None:
            current_app.logger.error("Error when parsing response: %s", response.text)
            return None

        access_token = user_login_node.attrib.get("accessToken")
        user_id = user_login_node.attrib.get("UserId")

        if not access_token or not user_id:
            current_app.logger.error("Missing accessToken or UserId in response: %s", response.text)
            return None

        return access_token, user_id

    def get_nodes(
        self, service_path: str, params: dict, container_path: str, need_token: bool = False, required: bool = False
    ) -> list[Element]:
        """Call the PSS API and return the children of the container node, empty if the container is missing."""
        endpoint = f"https://{self.server}/{service_path}"
        response = self.call(endpoint, params=params, need_token=need_token)
        container = ET.fromstring(response.text).find(container_path)

        if container is None:
            if required:
                current_app.logger.error("Error when parsing response: %s", response.text)
            return []

        return list(container)

    def get_entities(
        self,
        service_path: str,
        params: dict,
        container_path: str,
        parse: Callable[[Element], dict] | None = None,
        need_token: bool = False,
    ) -> list[dict]:
        """Get entities from the PSS API, parsed from the container children, with their raw XML node."""
        parse = parse or self.parse_node
        nodes = self.get_nodes(service_path, params, container_path, need_token=need_token)
        return [self.add_xml_element(parse(node), node) for node in nodes]

    def design_params(self, version_setting: str) -> dict:
        """Get the parameters of a design list call, for the given version in API settings."""
        return {
            "designVersion": self._api_settings[version_setting],
            "languageKey": "en",
        }

    @staticmethod
    def parse_node(node: Element) -> dict[str, Any]:
        """Extract data from XML node attributes."""
        return dict(node.attrib)

    @staticmethod
    def add_xml_element(data: dict, node: Element) -> dict:
        """Add the raw XML node to the parsed data (custom field)."""
        data["pixyship_xml_element"] = node
        return data

    def inspect_ship(self, user_id: int) -> dict[str, dict]:
        """Get player ship data from API."""
        params = {
            "userId": user_id,
            "designVersion": self._api_settings["ShipDesignVersion"],
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/ShipService/InspectShip2"
        response = self.call(endpoint, params=params, need_token=True, force_token_generation=True)
        root = ET.fromstring(response.text)

        user_node = root.find(".//User")
        ship_node = root.find(".//Ship")

        if user_node is None or ship_node is None:
            error_msg = "Missing required User or Ship element in XML"
            raise ValueError(error_msg)

        inspect_ship: dict = {
            "User": self.add_xml_element(self.parse_node(user_node), user_node),
            "Ship": self.add_xml_element(self.parse_node(ship_node), ship_node),
        }

        rooms_node = root.find(".//Rooms")
        inspect_ship["Ship"]["Rooms"] = (
            [] if rooms_node is None else [self.add_xml_element(self.parse_node(node), node) for node in rooms_node]
        )

        return inspect_ship

    def ship_details(self, user_id: int) -> tuple[dict, dict]:
        """Get player ship details from API."""
        params = {
            "UserId": user_id,
        }

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/PublicService/GetShipDetails"
        response = self.call(endpoint, params=params, need_token=True)
        root = ET.fromstring(response.text)

        ship_node = root.find(".//Ship")
        user_node = root.find(".//User")

        if ship_node is None or user_node is None:
            error_msg = "Missing required Ship or User element in XML"
            raise ValueError(error_msg)

        ship = self.add_xml_element(self.parse_node(ship_node), ship_node)
        user = self.add_xml_element(self.parse_node(user_node), user_node)

        return ship, user

    def ship_room_details(self, user_id: int) -> list:
        """Get player ship room details from API."""
        return self.get_entities("PublicService/GetShipRoomDetails", {"UserId": user_id}, ".//Rooms", need_token=True)

    def search_users(self, user_name: str, exact_match: bool = False) -> list:
        """Search players by name from API."""
        if not exact_match:
            return self.get_entities("UserService/SearchUsers", {"searchstring": user_name}, ".//Users")

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/UserService/SearchUsers"
        response = self.call(endpoint, params={"searchstring": user_name})
        root = ET.fromstring(response.text)

        # compare in Python, an XPath [@Name='...'] predicate can't express names containing both ' and "
        user_node = next((node for node in root.iter("User") if node.get("Name") == user_name), None)
        if user_node is None:
            return []

        return [self.add_xml_element(self.parse_node(user_node), user_node)]

    def get_dailies(self) -> dict:
        """Get dailies from settings service from API."""
        params = {"languageKey": "en", "deviceType": "DeviceTypeAndroid"}

        # retrieve data as XML from Pixel Starships API
        endpoint = f"https://{self.server}/LiveOpsService/GetTodayLiveOps2"
        response = self.call(endpoint, params=params)
        root = ET.fromstring(response.text)

        dailies_node = root.find(".//LiveOps")

        if dailies_node is None:
            error_msg = "Missing required LiveOps element in XML"
            raise ValueError(error_msg)

        return self.add_xml_element(self.parse_node(dailies_node), dailies_node)

    def get_sprites(self) -> list:
        """Get sprites from API."""
        params = {
            "designVersion": self._api_settings["FileVersion"],
            "deviceType": "DeviceTypeAndroid",
        }
        return self.get_entities("FileService/ListSprites", params, ".//Sprites")

    def get_rooms_sprites(self) -> list:
        """Get rooms sprites from API."""
        params = {"designVersion": self._api_settings["RoomDesignSpriteVersion"]}
        return self.get_entities("RoomDesignSpriteService/ListRoomDesignSprites", params, ".//RoomDesignSprites")

    def get_skinsets(self) -> list:
        """Get skinsets from API."""
        return self.get_entities("UserService/ListSkinsets2", self.design_params("SkinSetVersion"), ".//SkinSets")

    def get_skins(self) -> list:
        """Get skins from API."""
        return self.get_entities("UserService/ListSkins2", self.design_params("SkinVersion"), ".//Skins")

    def get_ships(self) -> list:
        """Get ships designs from API."""
        return self.get_entities(
            "ShipService/ListAllShipDesigns2", self.design_params("ShipDesignVersion"), ".//ShipDesigns"
        )

    def get_researches(self) -> list:
        """Get research designs from API."""
        return self.get_entities(
            "ResearchService/ListAllResearchDesigns2", self.design_params("ResearchDesignVersion"), ".//ResearchDesigns"
        )

    def get_rooms(self) -> list:
        """Get room designs from API."""
        # availability of rooms, by root room design id
        rooms_purchase: dict[str | None, dict] = {}
        for room_purchase in self.get_rooms_purchase():
            rooms_purchase.setdefault(room_purchase.get("RoomDesignId"), room_purchase)

        room_nodes = self.get_nodes(
            "RoomService/ListRoomDesigns2", self.design_params("RoomDesignSpriteVersion"), ".//RoomDesigns"
        )

        rooms = []
        for room_node in room_nodes:
            # if room purchase, add node to room node
            room_purchase = rooms_purchase.get(room_node.attrib.get("RootRoomDesignId"))
            if room_purchase:
                room_node.set("AvailabilityMask", room_purchase["AvailabilityMask"])

            rooms.append(self.add_xml_element(self.parse_room_node(room_node), room_node))

        return rooms

    @staticmethod
    def parse_room_node(room_node: Element) -> dict:
        """Extract room data from XML node."""
        room: dict[str, Any] = dict(room_node.attrib)

        missile_design_node = list(room_node.iter("MissileDesign"))
        if missile_design_node:
            room["MissileDesign"] = missile_design_node[0].attrib
        else:
            room["MissileDesign"] = None

        return room

    def get_missile_designs(self) -> list:
        """Get missile designs from API."""
        return self.get_entities(
            "RoomService/ListMissileDesigns", self.design_params("MissileDesignVersion"), ".//MissileDesigns"
        )

    def add_missile_design_nodes(self, nodes: list[Element], kind: str) -> list[Element]:
        """Add the missile design and the reload modifier of their item to craft or missile nodes.

        Nodes without missile design are skipped.
        """
        missile_designs: dict[str | None, dict] = {}
        for missile_design in self.get_missile_designs():
            missile_designs.setdefault(missile_design.get("MissileDesignId"), missile_design)

        item_designs: dict[str | None, dict] = {}
        for item_design in self.get_items():
            item_designs.setdefault(item_design.get("CraftDesignId"), item_design)

        complete_nodes = []
        for node in nodes:
            missile_design = missile_designs.get(node.attrib["MissileDesignId"])
            if not missile_design:
                current_app.logger.error(
                    "Cannot retrieve %s MissileDesign for MissileDesignId %s",
                    kind,
                    node.attrib["MissileDesignId"],
                )
                continue

            item_design = item_designs.get(node.attrib.get("CraftDesignId"))
            if item_design:
                node.set("ReloadModifier", item_design["ReloadModifier"])

            node.append(missile_design["pixyship_xml_element"])
            complete_nodes.append(node)

        return complete_nodes

    def get_crafts(self) -> list:
        """Get crafts designs from API."""
        craft_nodes = self.get_nodes(
            "RoomService/ListCraftDesigns", self.design_params("CraftDesignVersion"), ".//CraftDesigns"
        )

        return [
            self.add_xml_element(self.parse_craft_node(craft_node), craft_node)
            for craft_node in self.add_missile_design_nodes(craft_nodes, "craft")
        ]

    @staticmethod
    def parse_craft_node(craft_node: Element) -> dict:
        """Extract craft data from XML node."""
        craft: dict[str, Any] = dict(craft_node.attrib)

        missile_design_node = list(craft_node.iter("MissileDesign"))
        craft["MissileDesign"] = missile_design_node[0].attrib

        return craft

    def get_missiles(self) -> list:
        """Get missiles designs from API."""
        item_nodes = self.get_nodes(
            "ItemService/ListItemDesigns2", self.design_params("ItemDesignVersion"), ".//ItemDesigns"
        )
        missile_nodes = [item_node for item_node in item_nodes if item_node.attrib["ItemType"] == "Missile"]

        return [
            self.add_xml_element(self.parse_missile_node(missile_node), missile_node)
            for missile_node in self.add_missile_design_nodes(missile_nodes, "missile")
        ]

    @staticmethod
    def parse_missile_node(missile_node: Element) -> dict:
        """Extract missile data from XML node."""
        missile: dict[str, Any] = dict(missile_node.attrib)

        missile_design_node = list(missile_node.iter("MissileDesign"))
        missile["MissileDesign"] = missile_design_node[0].attrib

        return missile

    def get_rooms_purchase(self) -> list:
        """Get room designs purchase from API."""
        return self.get_entities(
            "RoomService/ListRoomDesignPurchase",
            self.design_params("RoomDesignPurchaseVersion"),
            ".//RoomDesignPurchases",
            parse=self.parse_room_node,
        )

    def get_characters(self) -> list:
        """Get character designs from API."""
        character_nodes = self.get_nodes(
            "CharacterService/ListAllCharacterDesigns2",
            self.design_params("CharacterDesignVersion"),
            ".//CharacterDesigns",
            required=True,
        )

        return [
            self.add_xml_element(self.parse_character_node(character_node), character_node)
            for character_node in character_nodes
        ]

    @staticmethod
    def parse_character_node(character_node: Element) -> dict:
        """Extract character data from XML node."""
        character: dict[str, Any] = dict(character_node.attrib)

        character_parts: dict[str, dict] = {}
        character["CharacterParts"] = character_parts
        character_part_nodes = character_node.find(".//CharacterParts")
        if character_part_nodes is not None:
            for character_part_node in character_part_nodes:
                character_part = character_part_node.attrib
                character_parts[character_part["CharacterPartType"]] = character_part

        return character

    def get_collections(self) -> list:
        """Get collection designs from API."""
        return self.get_entities(
            "CollectionService/ListAllCollectionDesigns",
            self.design_params("CollectionDesignVersion"),
            ".//CollectionDesigns",
        )

    def get_items(self) -> list:
        """Get item designs from API."""
        return self.get_entities(
            "ItemService/ListItemDesigns2", self.design_params("ItemDesignVersion"), ".//ItemDesigns"
        )

    def get_alliances(self, take: int = 100) -> list:
        """Get alliances from API, top 100 by default."""
        params = {
            "designVersion": self._api_settings["ItemDesignVersion"],
            "take": take,
        }
        return self.get_entities("AllianceService/ListAlliancesByRanking", params, ".//Alliances")

    @staticmethod
    def find_node_in_response(response_text: str, path: str) -> Element | None:
        """Find a node in an XML response, None if not found or if the response isn't XML (e.g. HTML 5xx page)."""
        try:
            return ET.fromstring(response_text).find(path)
        except ET.ParseError:
            return None

    def get_sales(self, item_id: int, max_sale_id: int = 0, take: int | None = None) -> list:
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

            current_app.logger.info("retrieve sales of %d from %d to %d", item_id, start, end)

            # retrieve data as XML from Pixel Starships API
            endpoint = f"https://{self.server}/MarketService/ListSalesByItemDesignId"
            response = self.call(endpoint, params=params)

            if response.status_code == 400:
                current_app.logger.error("Response in error: %s", response.text)
                errors += 1

                if errors == 3:
                    # three times the call is in errors, skip this item
                    # clear the sales to keep the max_sale_id correct for the next run
                    sales.clear()
                    break

                # too many request, wait a little, and try again
                api_sleep(30, force_sleep=True)
                continue

            # parse HTTP body as XML and find sales nodes
            sale_nodes = self.find_node_in_response(response.text, ".//Sales")

            # error when parsing the response
            if sale_nodes is None:
                current_app.logger.error("Error when parsing response: %s", response.text)
                errors += 1

                if errors == 3:
                    # three times the call is in errors, skip this item
                    # clear the sales to keep the max_sale_id correct for the next run
                    sales.clear()
                    break

                api_sleep(3, force_sleep=True)
                continue

            # no more sales available
            if sale_nodes is None or len(sale_nodes) == 0:
                break

            for sale_node in sale_nodes:
                sale_id_str = sale_node.get("SaleId")
                if sale_id_str is None:
                    continue
                sale_id = int(sale_id_str)
                sale = self.parse_node(sale_node)

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

    def get_market_messages(self, item_id: int) -> list:
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
            current_app.logger.error("Response in error: %s", response.text)

            # too many request, wait a little, and try again
            api_sleep(10, force_sleep=True)

            return []

        # parse HTTP body as XML and find market_messages nodes
        market_messsage_nodes = self.find_node_in_response(response.text, ".//Messages")

        # error when parsing the response
        if market_messsage_nodes is None:
            current_app.logger.error("Error when parsing response: %s", response.text)

            return []

        for market_message_node in market_messsage_nodes:
            market_message = self.parse_node(market_message_node)
            market_messages.append(market_message)

        return market_messages

    def get_alliance_users(self, alliance_id: int, skip: int = 0, take: int = 100) -> list:
        """Get alliance users from API, top 100 by default."""
        params = {"allianceId": alliance_id, "take": take, "skip": skip}
        return self.get_entities("AllianceService/ListUsers", params, ".//Users", need_token=True)

    def get_users(self, start: int = 1, end: int = 100) -> list:
        """Get users from API, top 100 by default."""
        params = {"from": start, "to": end}
        return self.get_entities("LadderService/ListUsersByRanking", params, ".//Users", need_token=True)

    def get_prestiges_character_to(self, character_id: int) -> list:
        """Get prestiges recipe creating given character from API (possibly none)."""
        params = {"characterDesignId": character_id}
        return self.get_entities("CharacterService/PrestigeCharacterTo", params, ".//Prestiges")

    def get_prestiges_character_from(self, character_id: int) -> list:
        """Get prestiges recipe created with given character from API (possibly none)."""
        params = {"characterDesignId": character_id}
        return self.get_entities("CharacterService/PrestigeCharacterFrom", params, ".//Prestiges")

    @staticmethod
    def get_stardate() -> int:
        """Compute Stardate."""
        utc_now = datetime.datetime.now(tz=datetime.UTC)
        today = datetime.date(utc_now.year, utc_now.month, utc_now.day)
        return (today - PSS_START_DATE).days

    @staticmethod
    def parse_sale_item_mask(equipment_mask: int) -> list:
        """From SaleItemMask determine Sale options."""
        output = [int(x) for x in f"{equipment_mask:05b}"]

        options = []
        for index, _value in enumerate(output):
            if index > 4:
                break
            options.append(IAP_OPTIONS_MASK_LOOKUP[4 - index])

        # reverse order
        options.reverse()

        return options

    def get_trainings(self) -> list:
        """Get trainings data from API."""
        return self.get_entities(
            "TrainingService/ListAllTrainingDesigns2", self.design_params("TrainingDesignVersion"), ".//TrainingDesigns"
        )

    def get_achievements(self) -> list:
        """Get achievements data from API."""
        return self.get_entities(
            "AchievementService/ListAchievementDesigns2",
            self.design_params("AchievementDesignVersion"),
            ".//AchievementDesigns",
        )

    def get_situations(self) -> list:
        """Get situations data from API."""
        return self.get_entities(
            "SituationService/ListSituationDesigns", self.design_params("SituationDesignVersion"), ".//SituationDesigns"
        )

    def get_promotions(self) -> list:
        """Get promotions data from API."""
        return self.get_entities(
            "PromotionService/ListAllPromotionDesigns2",
            self.design_params("PromotionDesignVersion"),
            ".//PromotionDesigns",
        )

    def get_star_system_markers(self) -> list:
        """Get Star System Markers data from API."""
        return self.get_entities(
            "GalaxyService/ListStarSystemMarkers", {"languageKey": "en"}, ".//StarSystemMarkers", need_token=True
        )
