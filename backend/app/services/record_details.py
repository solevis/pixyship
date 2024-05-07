from app.enums import TypeEnum
from app.services.base import BaseService


class RecordDetailsService(BaseService):
    """Service to get record details."""

    def __init__(self):
        super().__init__()
        self.services = {
            TypeEnum.ITEM: self.item_service,
            TypeEnum.SHIP: self.ship_service,
            TypeEnum.CHARACTER: self.character_service,
            TypeEnum.SKIN: self.skin_service,
            TypeEnum.SKINSET: self.skin_service,
            TypeEnum.ACHIEVEMENT: self.achievement_service,
            TypeEnum.COLLECTION: self.collection_service,
            TypeEnum.CRAFT: self.craft_service,
            TypeEnum.MISSILE: self.missile_service,
            TypeEnum.PRESTIGE: self.character_service,
            TypeEnum.RESEARCH: self.research_service,
            TypeEnum.ROOM: self.room_service,
            TypeEnum.ROOM_SPRITE: self.room_service,
            TypeEnum.SPRITE: self.sprite_service,
            TypeEnum.TRAINING: self.training_service,
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
