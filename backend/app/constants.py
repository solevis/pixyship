import datetime

PSS_SPRITES_URL = "https://pixelstarships.s3.amazonaws.com/{}.png"

# A map to find the correct interior for a given race's ship
# This fails for some rock ship cause this isn't actually how it works
RACE_SPECIFIC_SPRITE_MAP: dict[int, list[int]] = {
    83: [83, 84, 83, 82, 1302, 561, 3134],  # basic lifts
    1532: [1532, 1534, 1532, 1533, 1536, 1535, 3163],  # endgame lifts
    871: [871, 872, 871, 869, 870, 873, 3135],  # armors
}

ABILITY_NAME_MAP: dict[str, str] = {
    "DamageToSameRoomCharacters": "Gas",
    "HealRoomHp": "Urgent Repair",
    "HealSelfHp": "First Aid",
    "AddReload": "Rush",
    "FireWalk": "Fire Walk",
    "DamageToCurrentEnemy": "Critical Strike",
    "DamageToRoom": "Ultra Dismantle",
    "DeductReload": "System Hack",
    "HealSameRoomCharacters": "Healing Rain",
    "Freeze": "Freeze",
    "SetFire": "Arson",
    "Bloodlust": "Bloodlust",
    "Invulnerability": "Phase Shift",
    "ProtectRoom": "Stasis Shield",
    "None": "",
}

ABILITY_SPRITE_MAP: dict[str, int] = {
    "DamageToSameRoomCharacters": 2706,
    "HealRoomHp": 2709,
    "HealSelfHp": 2707,
    "AddReload": 2703,
    "FireWalk": 5389,
    "DamageToCurrentEnemy": 2708,
    "DamageToRoom": 2710,
    "DeductReload": 2704,
    "HealSameRoomCharacters": 2705,
    "Freeze": 5390,
    "SetFire": 5388,
    "Bloodlust": 13866,
    "Invulnerability": 13319,
    "ProtectRoom": 13320,
    "None": 110,  # Empty sprite
}

COLLECTION_ABILITY_MAP = {
    "EmpSkill": "EMP Discharge",
    "SharpShooterSkill": "Sharpshooter",
    "ResurrectSkill": "Resurrection",
    "BloodThirstSkill": "Vampirism",
    "MedicalSkill": "Combat Medic",
    "FreezeAttackSkill": "Cryo Field",
    "InstantKillSkill": "Headshot",
    "RefreshAbility": "Refresh",
    "CastAbilitySkill": "Cast",
    "CastAssignedAbilitySkill": "Cast Assigned",
    "ApplyArmorSkill": "Apply Armor",
    "PreventDamageSkill": "Prevent Damage",
    "GainItemSkill": "Gain Item",
    "DamageReductionTimeSkill": "Damage Reduction Time",
    "Repair": "Repair",
    "MoveSpeedBoost": "Move Speed Boost",
    "FireSkill": "Fire",
    "ReduceStatusSkill": "Reduce Status",
    "DirectDamage": "Direct Damage",
    "ReduceRoomStatusSkill": "Reduce Room Status",
    "Cloak": "Cloak",
    "DamageReductionSkill": "Damage Reduction",
    "RoomDamageBoostInstance": "Room Damage Boost",
    "ReduceFutureDamageInstance": "Reduce Future Damage",
    "DestroyModules": "Destroy Modules",
    "PreventStatusSkill": "Prevent Status",
    "ReduceActionCooldown": "Reduce Action Cooldown",
    "RepairModuleSkill": "Repair Module",
    "SpawnCrewSkill": "Spawn Crew",
    "SpawnModuleSkill": "Spawn Module",
    "StaminaRegenSkill": "Stamina Regen",
    "ReduceCrewStatusSkill": "Reduce Crew Status",
    "None": "None",
}

COLLECTION_ABILITY_TRIGGER_MAP = {
    "AbilityUsed": "Ability Used",
    "AttackCrew": "Attack Crew",
    "Death": "Death",
    "Repair": "Repair",
    "RoomDestruction": "Room Destruction",
    "Constant": "Constant",
    "Start": "Start",
    "TakeCrewDamage": "Take Crew Damage",
    "Stun": "Stun",
    "DamageTaken": "Damage Taken",
    "Teleport": "Teleport",
    "TakeDamageFromRoom": "Take Damage From Room",
    "ChangeRoom": "Change Room",
    "ModuleTrigger": "Module Trigger",
    "TakeFireDamage": "Take Fire Damage",
    "None": "None",
}

COLLECTION_ABILITY_TRIGGER_DESC_MAP = {
    "Constant": "Triggers once every second.",
    "Death": "Triggers on death.",
    "Idle": "Triggers once every second when idling.",
    "Kill": "Triggers on successful crew kill.",
    "Repair": "Triggers on room repair.",
    "Start": "Triggers at the start of battle.",
    "Stun": "Triggers when stunned.",
    "Teleport": "Triggers after teleporting.",
    "Walk": "Triggers once every movement step.",
    "AbilityUsed": "Triggers on special ability activation.",
    "AllyDeath": "Triggers on death of friendly crew in the current room.",
    "AttackCrew": "Triggers on crew attack.",
    "AttackRoom": "Triggers on room attack.",
    "AttackAny": "Triggers on any attack.",
    "ChangeRoom": "Triggers when entering a new room.",
    "DamageTaken": "Triggers when receiving damage.",
    "EnemyEncounter": "Triggers when encountering a new enemy.",
    "HealingReceived": "Triggers when receiving healing.",
    "RoomDestruction": "Triggers when current room is destroyed.",
    "TakeFireDamage": "Triggers when receiving fire damage.",
    "TakeCrewDamage": "Triggers when receiving crew damage.",
    "TakeDamageFromRoom": "Triggers when receiving damage from a weapon room attack.",
    "FriendlyAbilityUsed": "Triggers when a friendly crew activates an ability in the same room.",
    "EnemyAbilityUsed": "Triggers when an enemy crew activates an ability in the same room.",
    "ModuleTrigger": "Triggers when the crew causes a module in the current room to trigger.",
    "None": "None",
}

COLLECTION_BASIC_ABILITY_MAP = {
    "Ability",
    "Attack",
    "Engine",
    "Hp",
    "Pilot",
    "Repair",
    "Science",
    "Stamina",
    "Weapon",
    "FireResistance",
}

RARITY_MAP: dict[str, int] = {
    "Legendary": 7,
    "Special": 6,
    "Hero": 5,
    "Epic": 4,
    "Unique": 3,
    "Elite": 2,
    "Common": 1,
}

RARITY_COLOR: dict[str, str] = {
    "Common": "grey",
    "Elite": "white",
    "Unique": "blue",
    "Epic": "purple",
    "Hero": "gold",
    "Special": "gold",
    "Legendary": "gold",
}

TYPE_PSS_API_NAME_FIELD: dict[str, str] = {
    "ship": "ShipDesignName",
    "room": "RoomName",
    "char": "CharacterDesignName",
    "item": "ItemDesignName",
    "collection": "CollectionDesignId",
    "sprite": "SpriteKey",
}

EQUIPMENT_SLOTS: list[str] = ["Head", "Body", "Leg", "Weapon", "Accessory", "Pet"]

SLOT_MAP: dict[str, str | None] = {
    "EquipmentHead": "Head",
    "EquipmentWeapon": "Weapon",
    "EquipmentBody": "Body",
    "EquipmentLeg": "Leg",
    "EquipmentAccessory": "Accessory",
    "EquipmentPet": "Pet",
    "MineralPack": "Mineral Pack",
    "GasPack": "Gas Pack",
    "InstantPrize": "Instant Prize",
    "InstantTraining": "Instant Training",
    "ReducePrestige": "Reduce Prestige",
    "ReduceFatigue": "Reduce Fatigue",
    "ResetTraining": "Reset Training",
    "AIBook": "AI Book",
    "FillMineralStorage": "Fill Mineral Storage",
    "FillGasStorage": "Fill Gas Storage",
    "SpeedUpConstruction": "SpeedUp Construction",
    "None": None,
}

ROOM_TYPE_MAP: dict[str, str] = {
    "Wall": "Armor",
}

ENHANCE_MAP: dict[str | None, str | None] = {
    "FireResistance": "Fire Resistance",
    "FreezeAttackSkill": "Freeze",
    "Hp": "HP",
    "None": None,
    None: None,
}

SHORT_ENHANCE_MAP: dict[str | None, str | None] = {
    "Ability": "ABL",
    "Attack": "ATK",
    "Engine": "ENG",
    "FireResistance": "RST",
    "FreezeAttackSkill": "ABL",
    "Hp": "HP",
    "Pilot": "PLT",
    "Repair": "RPR",
    "Science": "SCI",
    "Stamina": "STA",
    "Weapon": "WPN",
    "None": None,
    None: None,
}

RESEARCH_TYPE_MAP: dict[str, str | None] = {
    "CrewLevelUpCost": "Crew LevelUp Cost",
    "ConcurrentConstruction": "Concurrent Construction",
    "TradeCapacity": "Trade",
    "ModuleCapacity": "Module",
    "StickerCapacity": "Sticker",
    "AmmoSalvageCapacity": "Ammo Recycling",
    "CollectAll": "Collector",
    "ItemRecycling": "Item Recycling",
    "BoostGauge": "Boost Gauge",
    "None": None,
}

# Daily IAP mask (see https://github.com/PieInTheSky-Inc/YaDc)
IAP_NAMES: dict[int, str] = {500: "Clip", 1200: "Roll", 2500: "Stash", 6500: "Case", 14000: "Vault"}

# 0 - Unknown
# 1 - Pirate/Dark
# 2 - Fed/Blue
# 3 - Qtari/Gold
# 4 - Visiri/Red
# 5 - UFO/Green
# 6 - Starbase
RACES: dict[int | None, str] = {
    None: "None",
    0: "Unknown",
    1: "Pirate",
    2: "Federation",
    3: "Qtarian",
    4: "Visiri",
    5: "Gray",
}

MODULE_ENHANCEMENT_MAP: dict[str, str] = {"Turret": "Attack", "XP": "XP"}

MODULE_BONUS_RATIO_MAP: dict[str, int] = {"Turret": 100}

MANUFACTURE_CAPACITY_MAP: dict[str, str] = {
    "Shield": "Restore",
    "Recycling": "Max Blend",
    "Council": "Max Donations",
}

MANUFACTURE_RATE_MAP: dict[str, str] = {
    "Recycling": "Harvest",
}

MANUFACTURE_RATE_PER_HOUR_MAP: dict[str, bool] = {
    "Laser": True,
    "Mineral": True,
    "Gas": True,
    "Supply": True,
}

MANUFACTURE_CAPACITY_RATIO_MAP: dict[str, int] = {
    "Shield": 100,
    "Recycling": 1,
}

LABEL_CAPACITY_MAP: dict[str, str] = {
    "Medical": "Healing",
    "Shield": "Shield",
    "Stealth": "Cloak",
    "Engine": "Evasion",
    "Trap": "Crew Dmg",
    "Radar": "Detection",
    "Training": "Training Lvl",
    "Recycling": "DNA Capacity",
    "Gas": "Salvage",
    "Mineral": "Salvage",
    "Council": "Garrison",
    "Command": "Max AI",
    "Bridge": "Escape",
}

CAPACITY_RATIO_MAP: dict[str, int] = {
    "Medical": 100,
}

DAILY_SALE_SPRITE_ID: int = 11006
DAILY_REWARDS_SPRITE_ID: int = 2326
GREEN_CARGO_SPRITE_ID: int = 11881
BLUE_CARGO_SPRITE_ID: int = 11880
SHOP_SPRITE_ID: int = 592

PSS_START_DATE: datetime.date = datetime.date(year=2016, month=1, day=6)

IAP_OPTIONS_MASK_LOOKUP: list[int] = [500, 1200, 2500, 6500, 14000]

ROOM_SHOP_TYPE_MASK: dict[str | None, list[str]] = {
    "1": ["Player"],
    "2": ["Starbase"],
    "3": ["Player", "Starbase"],
    None: ["Bux"],
}

SALE_FROM_MAP: dict[str, str] = {
    "green_cargo": "Merchant Ship (green cargo)",
    "promotion_valueoffer": "Bank",
    "blue_cargo_starbux": "Dropship (blue cargo)",
    "daily_rewards": "Daily Reward",
    "promotion_dailydealoffer": "Bank",
    "sale": "Bank",
    "shop": "Shop",
    "blue_cargo_mineral": "Dropship (blue cargo)",
    "promotion_offer": "Bank",
}

API_URLS: dict[str, str] = {
    "MAIN": "https://api.pixelstarships.com/",
    "STAGING": "https://apistaging.pixelstarships.com/",
}

FRAME_SIZE: int = 40
