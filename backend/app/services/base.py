from __future__ import annotations

from functools import cached_property
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


class BaseService:
    """Base service class."""

    @cached_property
    def record_service(self) -> RecordService:
        """Get record service."""
        from app.services.record import RecordService

        return RecordService()

    @cached_property
    def sprite_service(self) -> SpriteService:
        """Get sprite service."""
        from app.services.sprite import SpriteService

        return SpriteService()

    @cached_property
    def market_service(self) -> MarketService:
        """Get market service."""
        from app.services.market import MarketService

        return MarketService()

    @cached_property
    def training_service(self) -> TrainingService:
        """Get training service."""
        from app.services.training import TrainingService

        return TrainingService()

    @cached_property
    def skin_service(self) -> SkinService:
        """Get skin service."""
        from app.services.skin import SkinService

        return SkinService()

    @cached_property
    def collection_service(self) -> CollectionService:
        """Get collection service."""
        from app.services.collection import CollectionService

        return CollectionService()

    @cached_property
    def character_service(self) -> CharacterService:
        """Get character service."""
        from app.services.character import CharacterService

        return CharacterService()

    @cached_property
    def item_service(self) -> ItemService:
        """Get item service."""
        from app.services.item import ItemService

        return ItemService()

    @cached_property
    def research_service(self) -> ResearchService:
        """Get research service."""
        from app.services.reasearch import ResearchService

        return ResearchService()

    @cached_property
    def room_service(self) -> RoomService:
        """Get room service."""
        from app.services.room import RoomService

        return RoomService()

    @cached_property
    def ship_service(self) -> ShipService:
        """Get ship service."""
        from app.services.ship import ShipService

        return ShipService()

    @cached_property
    def achievement_service(self) -> AchievementService:
        """Get achievement service."""
        from app.services.achievement import AchievementService

        return AchievementService()

    @cached_property
    def craft_service(self) -> CraftService:
        """Get craft service."""
        from app.services.craft import CraftService

        return CraftService()

    @cached_property
    def pixyship_service(self) -> PixyShipService:
        """Get pixyship service."""
        from app.services.pixyship import PixyShipService

        return PixyShipService()

    @cached_property
    def missile_service(self) -> MissileService:
        """Get missile service."""
        from app.services.missile import MissileService

        return MissileService()

    @cached_property
    def prestige_service(self) -> PrestigeService:
        """Get prestige service."""
        from app.services.prestige import PrestigeService

        return PrestigeService()

    @cached_property
    def changes_service(self) -> ChangesService:
        """Get changes service."""
        from app.services.changes import ChangesService

        return ChangesService()

    @cached_property
    def record_details_service(self) -> RecordDetailsService:
        """Get record details service."""
        from app.services.record_details import RecordDetailsService

        return RecordDetailsService(
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

    @cached_property
    def daily_offer_service(self) -> DailyOfferService:
        """Get daily offer service."""
        from app.services.daily_offer import DailyOfferService

        return DailyOfferService()

    @cached_property
    def player_service(self) -> PlayerService:
        """Get player service."""
        from app.services.player import PlayerService

        return PlayerService()
