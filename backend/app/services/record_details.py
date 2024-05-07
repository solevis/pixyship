from app.enums import TypeEnum
from app.services.base import BaseService


class RecordDetailsService(BaseService):
    def __init__(self):
        super().__init__()

    def get_record_details(self, record_type: TypeEnum, record_id: int) -> dict | None:
        record = self.record_service.get_record(record_type, record_id)
        if record is None:
            return None

        if record.type == TypeEnum.ITEM:
            return self.item_service.items[record.type_id]

        if record.type == TypeEnum.SHIP:
            return self.ship_service.ships[record.type_id]

        if record.type == TypeEnum.CHARACTER:
            return self.character_service.characters[record.type_id]

        if record.type == TypeEnum.SKIN:
            return self.skin_service.skins[record.type_id]

        if record.type == TypeEnum.SKINSET:
            return self.skin_service.skinsets[record.type_id]

        if record.type == TypeEnum.ACHIEVEMENT:
            return self.achievement_service.achievements[record.type_id]

        if record.type == TypeEnum.COLLECTION:
            return self.collection_service.collections[record.type_id]

        if record.type == TypeEnum.CRAFT:
            return self.craft_service.crafts[record.type_id]

        if record.type == TypeEnum.MISSILE:
            return self.missile_service.missiles[record.type_id]

        if record.type == TypeEnum.PRESTIGE:
            return self.character_service.characters[record.type_id]

        if record.type == TypeEnum.RESEARCH:
            return self.research_service.researches[record.type_id]

        if record.type == TypeEnum.ROOM:
            return self.room_service.rooms[record.type_id]

        if record.type == TypeEnum.ROOM_SPRITE:
            return self.room_service.rooms[record.type_id]

        if record.type == TypeEnum.SPRITE:
            return self.sprite_service.sprites[record.type_id]

        if record.type == TypeEnum.TRAINING:
            return self.training_service.trainings[record.type_id]

        return None
