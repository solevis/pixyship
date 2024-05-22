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


class ServiceFactory:
    """Factory to create and get services."""

    @property
    def record_service(self) -> RecordService:
        """Get record service."""
        return RecordService()

    @property
    def sprite_service(self) -> SpriteService:
        """Get sprite service."""
        sprite_service = SpriteService()
        sprite_service.record_service = self.record_service

        return sprite_service

    @property
    def market_service(self) -> MarketService:
        """Get market service."""
        return MarketService()

    @property
    def training_service(self) -> TrainingService:
        """Get training service."""
        training_service = TrainingService()
        training_service.record_service = self.record_service
        training_service.sprite_service = self.sprite_service

        return training_service

    @property
    def skin_service(self) -> SkinService:
        """Get skin service."""
        skin_service = SkinService()
        skin_service.record_service = self.record_service
        skin_service.sprite_service = self.sprite_service

        return skin_service

    @property
    def collection_service(self) -> CollectionService:
        """Get collection service."""
        collection_service = CollectionService()
        collection_service.record_service = self.record_service
        collection_service.sprite_service = self.sprite_service
        collection_service.item_service = self.item_service
        collection_service.character_service = self.character_service

        return collection_service

    @property
    def character_service(self) -> CharacterService:
        """Get character service."""
        return CharacterService()

    @property
    def item_service(self) -> ItemService:
        """Get item service."""
        item_service = ItemService()
        item_service.record_service = self.record_service
        item_service.sprite_service = self.sprite_service
        item_service.market_service = self.market_service
        item_service.training_service = self.training_service
        item_service.skin_service = self.skin_service
        item_service.character_service = self.character_service

        return item_service

    @property
    def research_service(self) -> ResearchService:
        """Get research service."""
        research_service = ResearchService()
        research_service.record_service = self.record_service
        research_service.sprite_service = self.sprite_service
        research_service.room_service = self.room_service

        return research_service

    @property
    def room_service(self) -> RoomService:
        """Get room service."""
        room_service = RoomService()
        room_service.record_service = self.record_service
        room_service.sprite_service = self.sprite_service
        room_service.item_service = self.item_service
        room_service.research_service = self.research_service

        return room_service

    @property
    def ship_service(self) -> ShipService:
        """Get ship service."""
        ship_service = ShipService()
        ship_service.record_service = self.record_service
        ship_service.sprite_service = self.sprite_service
        ship_service.item_service = self.item_service
        ship_service.room_service = self.room_service

        return ship_service

    @property
    def achievement_service(self) -> AchievementService:
        """Get achievement service."""
        achievement_service = AchievementService()
        achievement_service.record_service = self.record_service
        achievement_service.sprite_service = self.sprite_service

        return achievement_service

    @property
    def craft_service(self) -> CraftService:
        """Get craft service."""
        craft_service = CraftService()
        craft_service.record_service = self.record_service
        craft_service.sprite_service = self.sprite_service

        return craft_service

    @property
    def pixyship_service(self) -> PixyShipService:
        """Get pixyship service."""
        pixyship_service = PixyShipService()
        pixyship_service.room_service = self.room_service
        pixyship_service.skin_service = self.skin_service
        pixyship_service.item_service = self.item_service
        pixyship_service.character_service = self.character_service

        return pixyship_service

    @property
    def missile_service(self) -> MissileService:
        """Get missile service."""
        missile_service = MissileService()
        missile_service.pixyship_service = self.pixyship_service
        missile_service.record_service = self.record_service
        missile_service.sprite_service = self.sprite_service

        return missile_service

    @property
    def prestige_service(self) -> PrestigeService:
        """Get prestige service."""
        prestige_service = PrestigeService()
        prestige_service.record_service = self.record_service
        prestige_service.character_service = self.character_service

        return prestige_service

    @property
    def changes_service(self) -> ChangesService:
        """Get changes service."""
        changes_service = ChangesService()
        changes_service.record_service = self.record_service
        changes_service.sprite_service = self.sprite_service
        changes_service.character_service = self.character_service
        changes_service.item_service = self.item_service

        return changes_service

    @property
    def record_details_service(self) -> RecordDetailsService:
        """Get record details service."""
        record_details_service = RecordDetailsService(
            item_service=self.item_service,
            ship_service=self.ship_service,
            character_service=self.character_service,
            skin_service=self.skin_service,
            achievement_service=self.achievement_service,
            collection_service=self.collection_service,
            craft_service=self.craft_service,
            missile_service=self.missile_service,
            research_service=self.research_service,
            room_service=self.room_service,
            sprite_service=self.sprite_service,
            training_service=self.training_service,
        )
        record_details_service.record_service = self.record_service

        return record_details_service

    @property
    def daily_offer_service(self) -> DailyOfferService:
        """Get daily offer service."""
        daily_offer_service = DailyOfferService()
        daily_offer_service.pixyship_service = self.pixyship_service
        daily_offer_service.record_service = self.record_service
        daily_offer_service.sprite_service = self.sprite_service
        daily_offer_service.item_service = self.item_service
        daily_offer_service.character_service = self.character_service
        daily_offer_service.record_details_service = self.record_details_service

        return daily_offer_service

    @property
    def player_service(self) -> PlayerService:
        """Get player service."""
        player_service = PlayerService()
        player_service.sprite_service = self.sprite_service
        player_service.item_service = self.item_service
        player_service.ship_service = self.ship_service
        player_service.room_service = self.room_service
        player_service.skin_service = self.skin_service

        return player_service
