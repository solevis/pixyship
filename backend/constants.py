import datetime

PSS_SPRITES_URL = 'https://pixelstarships.s3.amazonaws.com/{}.png'

# A map to find the correct interior for a given race's ship
# This fails for some rock ship cause this isn't actually how it works
RACE_SPECIFIC_SPRITE_MAP = {
    83: [83, 84, 83, 82, 1302, 561, 3134],  # basic lifts
    1532: [1532, 1534, 1532, 1533, 1536, 1535, 3163],  # endgame lifts
    871: [871, 872, 871, 869, 870, 873, 3135],  # armors
}

ABILITY_MAP = {
    'DamageToSameRoomCharacters': {'name': 'Gas', 'sprite': 2706},
    'HealRoomHp': {'name': 'Urgent Repair', 'sprite': 2709},
    'HealSelfHp': {'name': 'First Aid', 'sprite': 2707},
    'AddReload': {'name': 'Rush', 'sprite': 2703},
    'FireWalk': {'name': 'Fire Walk', 'sprite': 5389},
    'DamageToCurrentEnemy': {'name': 'Critical Strike', 'sprite': 2708},
    'DamageToRoom': {'name': 'Ultra Dismantle', 'sprite': 2710},
    'DeductReload': {'name': 'System Hack', 'sprite': 2704},
    'HealSameRoomCharacters': {'name': 'Healing Rain', 'sprite': 2705},
    'Freeze': {'name': 'Freeze', 'sprite': 5390},
    'SetFire': {'name': 'Arson', 'sprite': 5388},
    'Bloodlust': {'name': 'Bloodlust', 'sprite': 13866},
    'Invulnerability': {'name': 'Phase Shift', 'sprite': 13319},
    'ProtectRoom': {'name': 'Stasis Shield', 'sprite': 13320},
    'None': {'name': '', 'sprite': 110}  # Empty sprite
}

COLLECTION_ABILITY_MAP = {
    'EmpSkill': 'EMP Discharge',
    'SharpShooterSkill': 'Sharpshooter',
    'ResurrectSkill': 'Resurrection',
    'BloodThirstSkill': 'Vampirism',
    'MedicalSkill': 'Combat Medic',
    'FreezeAttackSkill': 'Cryo Field',
    'InstantKillSkill': 'Headshot',
    'None': 'None'
}

RARITY_MAP = {
    'Legendary': 7,
    'Special': 6,
    'Hero': 5,
    'Epic': 4,
    'Unique': 3,
    'Elite': 2,
    'Common': 1,
}

RARITY_COLOR = {
    'Common': 'grey',
    'Elite': 'white',
    'Unique': 'blue',
    'Epic': 'purple',
    'Hero': 'gold',
    'Special': 'gold',
    'Legendary': 'gold',
}

TYPE_PSS_API_NAME_FIELD = {
    'ship': 'ShipDesignName',
    'room': 'RoomName',
    'char': 'CharacterDesignName',
    'item': 'ItemDesignName',
    'collection': 'CollectionDesignId',
    'sprite': 'SpriteKey',
}

DEFAULT_EXPIRATION_DURATION = 60 * 5  # 5 minutes

EQUIPMENT_SLOTS = ['Head', 'Body', 'Leg', 'Weapon', 'Accessory', 'Pet']

SLOT_MAP = {
    'None': None,
    'EquipmentHead': 'Head',
    'EquipmentWeapon': 'Weapon',
    'EquipmentBody': 'Body',
    'EquipmentLeg': 'Leg',
    'EquipmentAccessory': 'Accessory',
    'EquipmentPet': 'Pet',
    'MineralPack': 'Mineral Pack',
    'GasPack': 'Gas Pack',
    'InstantPrize': 'Instant Prize',
    'InstantTraining': 'Instant Training',
    'ReducePrestige': 'Reduce Prestige',
    'ReduceFatigue': 'Reduce Fatigue',
    'ResetTraining': 'Reset Training',
    'AIBook': 'AI Book',
    'FillMineralStorage': 'Fill Mineral Storage',
    'FillGasStorage': 'Fill Gas Storage',
    'SpeedUpConstruction': 'SpeedUp Construction',
}

ROOM_TYPE_MAP = {
    'Wall': 'Armor',
}

ENHANCE_MAP = {
    'FireResistance': 'Fire Resistance',
    'FreezeAttackSkill': 'Freeze',
    'Hp': 'HP',
    'None': None
}

SHORT_ENHANCE_MAP = {
    'Ability': 'ABL',
    'Attack': 'ATK',
    'Engine': 'ENG',
    'FireResistance': 'RST',
    'FreezeAttackSkill': 'ABL',
    'Hp': 'HP',
    'Pilot': 'PLT',
    'Repair': 'RPR',
    'Science': 'SCI',
    'Stamina': 'STA',
    'Weapon': 'WPN',
    'None': None
}

RESEARCH_TYPE_MAP = {
    'CrewLevelUpCost': 'Crew LevelUp Cost',
    'ConcurrentConstruction': 'Concurrent Construction',
    'TradeCapacity': 'Trade',
    'ModuleCapacity': 'Module',
    'StickerCapacity': 'Sticker',
    'AmmoSalvageCapacity': 'Ammo Recycling',
    'CollectAll': 'Collector',
    'ItemRecycling': 'Item Recycling',
    'BoostGauge': 'Boost Gauge',
    'None': None
}

# Daily IAP mask (see https://github.com/PieInTheSky-Inc/YaDc)
IAP_NAMES = {
    500: 'Clip',
    1200: 'Roll',
    2500: 'Stash',
    6500: 'Case',
    14000: 'Vault'
}

# 0 - Unknown
# 1 - Pirate/Dark
# 2 - Fed/Blue
# 3 - Qtari/Gold
# 4 - Visiri/Red
# 5 - UFO/Green
# 6 - Starbase
RACES = {
    None: 'None',
    0: "Unknown",
    1: "Pirate",
    2: "Federation",
    3: "Qtarian",
    4: "Visiri",
    5: "Gray",
}

MODULE_ENHANCEMENT_MAP = {
    'Turret': 'Attack',
    'XP': 'XP'
}

MODULE_BONUS_RATIO_MAP = {
    'Turret': 100
}

MANUFACTURE_CAPACITY_MAP = {
    'Shield': 'Restore',
    'Recycling': 'Max Blend',
    'Council': 'Max Donations',
}

MANUFACTURE_RATE_MAP = {
    'Recycling': 'Harvest',
}

MANUFACTURE_RATE_PER_HOUR_MAP = {
    'Laser': True,
    'Mineral': True,
    'Gas': True,
    'Supply': True,
}

MANUFACTURE_CAPACITY_RATIO_MAP = {
    'Shield': 100,
    'Recycling': 1,
}

LABEL_CAPACITY_MAP = {
    'Medical': 'Healing',
    'Shield': 'Shield',
    'Stealth': 'Cloak',
    'Engine': 'Evasion',
    'Trap': 'Crew Dmg',
    'Radar': 'Detection',
    'Training': 'Training Lvl',
    'Recycling': 'DNA Capacity',
    'Gas': 'Salvage',
    'Mineral': 'Salvage',
    'Council': 'Garrison',
    'Command': 'Max AI',
    'Bridge': 'Escape',
}

CAPACITY_RATIO_MAP = {
    'Medical': 100,
}

DAILY_SALE_SPRITE_ID = 11006
DAILY_REWARDS_SPRITE_ID = 2326
GREEN_CARGO_SPRITE_ID = 11881
BLUE_CARGO_SPRITE_ID = 11880
SHOP_SPRITE_ID = 592

MIN_DEVICES = 10
PSS_START_DATE = datetime.date(year=2016, month=1, day=6)

IAP_OPTIONS_MASK_LOOKUP = [
    500,
    1200,
    2500,
    6500,
    14000
]

ROOM_SHOP_TYPE_MASK = {
    '1': ['Player'],
    '2': ['Starbase'],
    '3': ['Player', 'Starbase'],
    None: ['Bux']
}

SALE_FROM_MAP = {
    'green_cargo': 'Merchant Ship (green cargo)',
    'promotion_valueoffer': 'Bank',
    'blue_cargo_starbux': 'Dropship (blue cargo)',
    'daily_rewards': 'Daily Reward',
    'promotion_dailydealoffer': 'Bank',
    'sale': 'Bank',
    'shop': 'Shop',
    'blue_cargo_mineral': 'Dropship (blue cargo)',
    'promotion_offer': 'Bank'
}

API_URLS = {
    'MAIN': 'https://api.pixelstarships.com/',
    'STAGING': 'https://apistaging.pixelstarships.com/',
}
