from app.enums import TypeEnum
from app.services.achievement import AchievementService
from app.services.base import BaseService
from app.services.character import CharacterService
from app.services.collection import CollectionService
from app.services.craft import CraftService
from app.services.item import ItemService
from app.services.missile import MissileService
from app.services.research import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.skin import SkinService
from app.services.sprite import SpriteService
from app.services.training import TrainingService


class RecordDetailsService(BaseService):
    """Service to get record details."""

    def __init__(
        self,
        item_service: ItemService,
        ship_service: ShipService,
        character_service: CharacterService,
        skin_service: SkinService,
        achievement_service: AchievementService,
        collection_service: CollectionService,
        craft_service: CraftService,
        missile_service: MissileService,
        research_service: ResearchService,
        room_service: RoomService,
        sprite_service: SpriteService,
        training_service: TrainingService,
    ) -> None:
        super().__init__()
        self.services = {
            TypeEnum.ITEM: item_service,
            TypeEnum.SHIP: ship_service,
            TypeEnum.CHARACTER: character_service,
            TypeEnum.SKIN: skin_service,
            TypeEnum.SKINSET: skin_service,
            TypeEnum.ACHIEVEMENT: achievement_service,
            TypeEnum.COLLECTION: collection_service,
            TypeEnum.CRAFT: craft_service,
            TypeEnum.MISSILE: missile_service,
            TypeEnum.PRESTIGE: character_service,
            TypeEnum.RESEARCH: research_service,
            TypeEnum.ROOM: room_service,
            TypeEnum.ROOM_SPRITE: room_service,
            TypeEnum.SPRITE: sprite_service,
            TypeEnum.TRAINING: training_service,
        }

    def get_record_details(self, record_type: TypeEnum, record_id: int) -> dict | None:
        """Get record details from record type and id."""
        record = self.record_service.get_record(record_type, record_id)
        if record is None:
            return None

        service = self.services.get(record.type)
        if service is None:
            return None

        return getattr(service, record.type.name.lower() + "s")[record.type_id]
