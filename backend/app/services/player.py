from flask import current_app

from app.constants import RACE_SPECIFIC_SPRITE_MAP, RACES
from app.ext import db
from app.models import Alliance, Player
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService
from app.utils.pss import compute_pvp_ratio


class PlayerService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()

    def get_ship_data(self, player_name):
        """Get user and ship data from API."""

        ship, user, rooms, stickers = self.summarize_ship(player_name)

        data = None
        if user:
            data = {
                "rooms": rooms,
                "user": user,
                "ship": ship,
                "stickers": stickers,
                "status": "found",
            }

        return data

    def summarize_ship(self, player_name):
        """Get ship, user, rooms and upgrade from given player name."""

        user_id = self.find_user_id(player_name)
        if not user_id:
            current_app.logger.error("Cannot find user %s", player_name)
            return None, None, None, None

        ship_data, user_data = self.pixel_starships_api.ship_details(user_id)
        if not ship_data or not user_data:
            current_app.logger.error("Cannot find ship data for user %s", player_name)
            return None, None, None, None

        room_data = self.pixel_starships_api.ship_room_details(user_id)
        if not room_data:
            current_app.logger.error("Cannot find room data for user %s", player_name)
            return None, None, None, None

        user = dict(
            id=user_data["Id"],
            name=user_data["Name"],
            sprite=self.sprite_service.get_sprite_infos(int(user_data["IconSpriteId"])),
            alliance_name=user_data.get("AllianceName"),
            alliance_membership=user_data.get("AllianceMembership"),
            alliance_sprite=self.sprite_service.get_sprite_infos(int(user_data.get("AllianceSpriteId"))),
            trophies=int(user_data["Trophy"]),
            last_date=user_data["LastAlertDate"],
            race=RACES.get(int(ship_data["OriginalRaceId"]), RACES.get(0)),
        )

        searched_users = self.pixel_starships_api.search_users(user_data["Name"], True)
        if searched_users:
            more_user_data = searched_users[0]

            user["alliance_join_date"] = more_user_data.get("AllianceJoinDate")
            user["pvpattack_wins"] = int(more_user_data["PVPAttackWins"])
            user["pvpattack_losses"] = int(more_user_data["PVPAttackLosses"])
            user["pvpattack_draws"] = int(more_user_data["PVPAttackDraws"])
            user["pvpattack_ratio"] = compute_pvp_ratio(
                int(more_user_data["PVPAttackWins"]),
                int(more_user_data["PVPAttackLosses"]),
                int(more_user_data["PVPAttackDraws"]),
            )
            user["pvpdefence_draws"] = int(more_user_data["PVPDefenceDraws"])
            user["pvpdefence_wins"] = int(more_user_data["PVPDefenceWins"])
            user["pvpdefence_losses"] = int(more_user_data["PVPDefenceLosses"])
            user["pvpdefence_ratio"] = compute_pvp_ratio(
                int(more_user_data["PVPDefenceWins"]),
                int(more_user_data["PVPDefenceLosses"]),
                int(more_user_data["PVPDefenceDraws"]),
            )
            user["highest_trophy"] = int(more_user_data["HighestTrophy"])
            user["crew_donated"] = int(more_user_data["CrewDonated"])
            user["crew_received"] = int(more_user_data["CrewReceived"])
            user["creation_date"] = more_user_data["CreationDate"]
            user["last_login_date"] = more_user_data["LastLoginDate"]
        else:
            user["alliance_join_date"] = None
            user["pvpattack_wins"] = None
            user["pvpattack_losses"] = None
            user["pvpattack_draws"] = None
            user["pvpattack_ratio"] = None
            user["pvpdefence_draws"] = None
            user["pvpdefence_wins"] = None
            user["pvpdefence_losses"] = None
            user["pvpdefence_ratio"] = None
            user["highest_trophy"] = None
            user["crew_donated"] = None
            user["crew_received"] = None
            user["creation_date"] = None
            user["last_login_date"] = None

        ship_id = int(ship_data["ShipDesignId"])

        rooms = []
        for current_room_data in room_data:
            room = dict(
                self.convert_room_sprite_to_race_sprite(int(current_room_data["RoomDesignId"]), ship_id),
                design_id=int(current_room_data["RoomDesignId"]),
                row=int(current_room_data["Row"]),
                column=int(current_room_data["Column"]),
                construction=bool(current_room_data["ConstructionStartDate"]),
            )

            room["exterior_sprite"] = self.get_exterior_sprite(int(current_room_data["RoomDesignId"]), ship_id)

            rooms.append(room)

        ship = dict(
            self.ship_service.ships[ship_id],
            hue=ship_data["HueValue"],
            saturation=ship_data["SaturationValue"],
            brightness=ship_data["BrightnessValue"],
        )

        stickers = self.parse_ship_stickers(ship_data)

        return ship, user, rooms, stickers

    @staticmethod
    def find_user_id(search_name):
        """Given a name return the user_id from database. This should only be an exact match."""

        result = Player.query.filter(Player.name.ilike(search_name)).limit(1).first()
        if result:
            return result.id

        return None

    def parse_ship_stickers(self, ship_data):
        stickers_string = ship_data["StickerString"]

        if not stickers_string:
            return None

        stickers = []

        for sticker_string in stickers_string.split("|"):
            item_id = int(sticker_string.split("@")[0])
            item = self.item_service.items[item_id]
            coords = sticker_string.split("@")[1].split("-")

            sticker = {
                "sprite": item["logo_sprite"],
                "x": coords[0],
                "y": coords[1],
                "size": coords[2],
            }

            stickers.append(sticker)

        return stickers

    def convert_room_sprite_to_race_sprite(self, room_id, ship_id):
        """Convert rooms to the correct interior depending on ship race."""

        room = self.room_service.rooms[room_id]

        if room["type"] in ("Armor", "Lift"):
            ship = self.ship_service.ships[ship_id]

            if room["sprite"]["source"] in RACE_SPECIFIC_SPRITE_MAP:
                # make a new sprite in a new room to keep from overwriting original data
                room = room.copy()
                sprite = room["sprite"].copy()

                sprite["source"] = RACE_SPECIFIC_SPRITE_MAP[room["sprite"]["source"]][ship["race_id"]]
                room["sprite"] = sprite

        return room

    def get_exterior_sprite(self, room_id, ship_id):
        """Retrieve exterior sprite if existing"""

        ship = self.ship_service.ships[ship_id]
        exterior_sprite = None

        for skin in self.skin_service.skins.values():
            if (
                skin["root_id"] == room_id
                and skin["race_id"] == ship["race_id"]
                and skin["skin_type"] == "RoomSkin"
                and skin["sprite_type"] == "Exterior"
            ):
                exterior_sprite = skin["sprite"]

        return exterior_sprite

    def get_top100_alliances_from_api(self):
        """Get the top 100 alliances."""

        alliances = self.pixel_starships_api.get_alliances()

        return {
            int(alliance["AllianceId"]): {
                "name": alliance["AllianceName"],
            }
            for alliance in alliances
        }

    def get_alliance_users_from_api(self, alliance_id):
        """Get the top 100 alliances."""

        users = self.pixel_starships_api.get_alliance_users(alliance_id)
        return self.parse_users(users)

    def get_top100_users_from_api(self):
        """Get the top 100 players."""

        users = self.pixel_starships_api.get_users(1, 100)
        return self.parse_users(users)

    @staticmethod
    def parse_users(users):
        """Create users dict from XML PSS API response."""

        # force users to be a list
        if not isinstance(users, list):
            users = [users]

        return {
            int(user["Id"]): {
                "name": user["Name"],
                "trophies": int(user["Trophy"]),
                "alliance_id": int(user["AllianceId"]),
                "last_login_at": user["LastLoginDate"],
                "alliance_name": user.get("AllianceName"),
                "alliance_sprite_id": int(user["AllianceSpriteId"]),
            }
            for user in users
            if user["UserType"] != "UserTypeDisabled"
        }

    def get_player_data(self, search: str = None):
        """Retrieve all players data or players found by given search."""

        query = db.session.query(
            Player.name,
            Player.trophies,
            Alliance.name.label("alliance_name"),
            Alliance.sprite_id,
        ).outerjoin(Alliance, Alliance.id == Player.alliance_id)

        if search:
            query = query.filter(Player.name.ilike("%" + search + "%"))

        query = query.order_by(Player.trophies.desc()).limit(100)

        results = query.all()
        return [
            {
                "name": row[0],
                "lower": row[0].lower(),
                "trophies": row[1],
                "alliance": row[2],
                "alliance_sprite": self.sprite_service.get_sprite_infos(row[3]),
            }
            for row in results
        ]
