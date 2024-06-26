from enum import StrEnum, unique


@unique
class TypeEnum(StrEnum):
    """Type enumeration."""

    ACHIEVEMENT = "ACHIEVEMENT"
    CHARACTER = "CHARACTER"
    COLLECTION = "COLLECTION"
    CRAFT = "CRAFT"
    ITEM = "ITEM"
    MISSILE = "MISSILE"
    PRESTIGE = "PRESTIGE"
    RESEARCH = "RESEARCH"
    ROOM = "ROOM"
    ROOM_SPRITE = "ROOM_SPRITE"
    SHIP = "SHIP"
    SKIN = "SKIN"
    SKINSET = "SKINSET"
    SPRITE = "SPRITE"
    TRAINING = "TRAINING"
    FLEETGIFT = "FLEETGIFT"
    NONE = "NONE"
    BONUS = "BONUS"
