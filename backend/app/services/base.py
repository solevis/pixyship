from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.achievement import AchievementService
    from app.services.changes import ChangesService
    from app.services.character import CharacterService
    from app.services.collection import CollectionService
    from app.services.craft import CraftService
    from app.services.daily_offer import DailyOfferService
    from app.services.item import ItemService
    from app.services.market import MarketService
    from app.services.missile import MissileService
    from app.services.pixyship import PixyShipService
    from app.services.player import PlayerService
    from app.services.prestige import PrestigeService
    from app.services.reasearch import ResearchService
    from app.services.record import RecordService
    from app.services.record_details import RecordDetailsService
    from app.services.room import RoomService
    from app.services.ship import ShipService
    from app.services.skin import SkinService
    from app.services.sprite import SpriteService
    from app.services.training import TrainingService


class BaseService(ABC):
    def __init__(self):
        self._record_service: RecordService | None = None
        self._sprite_service: SpriteService | None = None
        self._market_service: MarketService | None = None
        self._training_service: TrainingService | None = None
        self._skin_service: SkinService | None = None
        self._collection_service: CollectionService | None = None
        self._character_service: CharacterService | None = None
        self._item_service: ItemService | None = None
        self._research_service: ResearchService | None = None
        self._room_service: RoomService | None = None
        self._ship_service: ShipService | None = None
        self._achievement_service: AchievementService | None = None
        self._craft_service: CraftService | None = None
        self._pixyship_service: PixyShipService | None = None
        self._missile_service: MissileService | None = None
        self._prestige_service: PrestigeService | None = None
        self._changes_service: ChangesService | None = None
        self._record_details_service: RecordDetailsService | None = None
        self._daily_offer_service: DailyOfferService | None = None
        self._player_service: PlayerService | None = None

    @property
    def record_service(self):
        if not self._record_service:
            raise ValueError("record_service is not set")

        return self._record_service

    @record_service.setter
    def record_service(self, record_service):
        self._record_service = record_service

    @property
    def sprite_service(self):
        if not self._sprite_service:
            raise ValueError("sprite_service is not set")

        return self._sprite_service

    @sprite_service.setter
    def sprite_service(self, sprite_service):
        self._sprite_service = sprite_service

    @property
    def market_service(self):
        if not self._market_service:
            raise ValueError("market_service is not set")

        return self._market_service

    @market_service.setter
    def market_service(self, market_service):
        self._market_service = market_service

    @property
    def training_service(self):
        if not self._training_service:
            raise ValueError("training_service is not set")

        return self._training_service

    @training_service.setter
    def training_service(self, training_service):
        self._training_service = training_service

    @property
    def skin_service(self):
        if not self._skin_service:
            raise ValueError("skin_service is not set")

        return self._skin_service

    @skin_service.setter
    def skin_service(self, skin_service):
        self._skin_service = skin_service

    @property
    def collection_service(self):
        if not self._collection_service:
            raise ValueError("collection_service is not set")

        return self._collection_service

    @collection_service.setter
    def collection_service(self, collection_service):
        self._collection_service = collection_service

    @property
    def character_service(self):
        if not self._character_service:
            raise ValueError("character_service is not set")

        return self._character_service

    @character_service.setter
    def character_service(self, character_service):
        self._character_service = character_service

    @property
    def item_service(self):
        if not self._item_service:
            raise ValueError("item_service is not set")

        return self._item_service

    @item_service.setter
    def item_service(self, item_service):
        self._item_service = item_service

    @property
    def research_service(self):
        if not self._research_service:
            raise ValueError("research_service is not set")

        return self._research_service

    @research_service.setter
    def research_service(self, research_service):
        self._research_service = research_service

    @property
    def room_service(self):
        if not self._room_service:
            raise ValueError("room_service is not set")

        return self._room_service

    @room_service.setter
    def room_service(self, room_service):
        self._room_service = room_service

    @property
    def ship_service(self):
        if not self._ship_service:
            raise ValueError("ship_service is not set")

        return self._ship_service

    @ship_service.setter
    def ship_service(self, ship_service):
        self._ship_service = ship_service

    @property
    def achievement_service(self):
        if not self._achievement_service:
            raise ValueError("achievement_service is not set")

        return self._achievement_service

    @achievement_service.setter
    def achievement_service(self, achievement_service):
        self._achievement_service = achievement_service

    @property
    def craft_service(self):
        if not self._craft_service:
            raise ValueError("craft_service is not set")

        return self._craft_service

    @craft_service.setter
    def craft_service(self, craft_service):
        self._craft_service = craft_service

    @property
    def pixyship_service(self):
        if not self._pixyship_service:
            raise ValueError("pixyship_service is not set")

        return self._pixyship_service

    @pixyship_service.setter
    def pixyship_service(self, pixyship_service):
        self._pixyship_service = pixyship_service

    @property
    def missile_service(self):
        if not self._missile_service:
            raise ValueError("missile_service is not set")

        return self._missile_service

    @missile_service.setter
    def missile_service(self, missile_service):
        self._missile_service = missile_service

    @property
    def prestige_service(self):
        if not self._prestige_service:
            raise ValueError("prestige_service is not set")

        return self._prestige_service

    @prestige_service.setter
    def prestige_service(self, prestige_service):
        self._prestige_service = prestige_service

    @property
    def changes_service(self):
        if not self._changes_service:
            raise ValueError("changes_service is not set")

        return self._changes_service

    @changes_service.setter
    def changes_service(self, changes_service):
        self._changes_service = changes_service

    @property
    def record_details_service(self):
        if not self._record_details_service:
            raise ValueError("record_details_service is not set")

        return self._record_details_service

    @record_details_service.setter
    def record_details_service(self, record_details_service):
        self._record_details_service = record_details_service

    @property
    def daily_offer_service(self):
        if not self._daily_offer_service:
            raise ValueError("daily_offer_service is not set")

        return self._daily_offer_service

    @daily_offer_service.setter
    def daily_offer_service(self, daily_offer_service):
        self._daily_offer_service = daily_offer_service

    @property
    def player_service(self):
        if not self._player_service:
            raise ValueError("player_service is not set")

        return self._player_service

    @player_service.setter
    def player_service(self, player_service):
        self._player_service = player_service
