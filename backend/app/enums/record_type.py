from enum import StrEnum, unique


@unique
class RecordTypeEnum(StrEnum):
    ACHIEVEMENT = "achievement"
    CHARACTER = "character"
    COLLECTION = "collection"
    CRAFT = "craft"
    ITEM = "item"
    MISSILE = "missile"
    PRESTIGE = "prestige"
    RESEARCH = "research"
    ROOM = "room"
    ROOM_SPRITE = "room_sprite"
    SHIP = "ship"
    SKIN = "skin"
    SKINSET = "skinset"
    SPRITE = "sprite"
    TRAINING = "training"
