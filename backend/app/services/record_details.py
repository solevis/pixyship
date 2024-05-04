from app.enums import RecordTypeEnum
from app.services.base import BaseService


class RecordDetailsService(BaseService):
    def __init__(self):
        super().__init__()

    def get_record_details(self, record_type: RecordTypeEnum, record_id: int) -> dict | None:
        record = self.record_service.get_record(record_type, record_id)
        if record is None:
            return None

        if record.type == RecordTypeEnum.ITEM:
            return self.item_service.items[record.type_id]
        elif record.type == RecordTypeEnum.SHIP:
            return self.ship_service.ships[record.type_id]
        elif record.type == RecordTypeEnum.CHARACTER:
            return self.character_service.characters[record.type_id]
        elif record.type == RecordTypeEnum.SKIN:
            return self.skin_service.skins[record.type_id]
        elif record.type == RecordTypeEnum.SKINSET:
            return self.skin_service.skinsets[record.type_id]
        elif record.type == RecordTypeEnum.ACHIEVEMENT:
            return self.achievement_service.achievements[record.type_id]
        elif record.type == RecordTypeEnum.COLLECTION:
            return self.collection_service.collections[record.type_id]
        elif record.type == RecordTypeEnum.CRAFT:
            return self.craft_service.crafts[record.type_id]
        elif record.type == RecordTypeEnum.MISSILE:
            return self.missile_service.missiles[record.type_id]
        elif record.type == RecordTypeEnum.PRESTIGE:
            return self.character_service.characters[record.type_id]
        elif record.type == RecordTypeEnum.RESEARCH:
            return self.research_service.researches[record.type_id]
        elif record.type == RecordTypeEnum.ROOM:
            return self.room_service.rooms[record.type_id]
        elif record.type == RecordTypeEnum.ROOM_SPRITE:
            return self.room_service.rooms[record.type_id]
        elif record.type == RecordTypeEnum.SPRITE:
            return self.sprite_service.sprites[record.type_id]
        elif record.type == RecordTypeEnum.TRAINING:
            return self.training_service.trainings[record.type_id]
        else:
            return None
