import datetime

from pixelstarshipsapi import PixelStarshipsApi
from run import push_context


def test_login():
    pixel_starships_api = PixelStarshipsApi()

    utc_now = datetime.datetime.utcnow()
    client_datetime = utc_now.strftime("%Y-%m-%dT%H:%M:%S")

    device_key, device_checksum = pixel_starships_api.generate_device(client_datetime)
    token = pixel_starships_api.get_device_token(device_key, client_datetime, device_checksum)

    assert isinstance(token, str)
    assert len(token) == 36


def test_settings():
    pixel_starships_api = PixelStarshipsApi()

    settings = pixel_starships_api.get_api_settings()

    assert 'ProductionServer' in settings
    assert 'MaintenanceMessage' in settings


def test_inspect_ship():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()

    user_id = 6635604  # Solevis
    inspect_ship = pixel_starships_api.inspect_ship(user_id)

    # Player
    user = inspect_ship['User']
    assert 'Id' in user
    assert 'Name' in user
    assert 'IconSpriteId' in user
    assert 'AllianceName' in user
    assert 'AllianceSpriteId' in user
    assert 'Trophy' in user
    assert 'LastAlertDate' in user

    # Ship
    ship = inspect_ship['Ship']
    assert 'ShipDesignId' in ship
    assert 'OriginalRaceId' in ship

    # Ship -> Room
    room = inspect_ship['Ship']['Rooms'][0]
    assert 'RoomId' in room
    assert 'Row' in room
    assert 'Column' in room
    assert 'ConstructionStartDate' in room


def test_dailies():
    pixel_starships_api = PixelStarshipsApi()
    dailies = pixel_starships_api.get_dailies()

    assert len(dailies) > 0

    # Shop
    assert 'LimitedCatalogCurrencyAmount' in dailies
    assert 'LimitedCatalogType' in dailies
    assert 'LimitedCatalogArgument' in dailies
    assert 'LimitedCatalogCurrencyType' in dailies
    assert 'LimitedCatalogQuantity' in dailies
    assert 'LimitedCatalogMaxTotal' in dailies
    assert 'LimitedCatalogExpiryDate' in dailies

    # Blue cargo
    assert 'CommonCrewId' in dailies
    assert 'HeroCrewId' in dailies

    # Green cargo
    assert 'CargoItems' in dailies
    assert 'CargoPrices' in dailies

    # Daily reward
    assert 'DailyRewardArgument' in dailies
    assert 'DailyRewardType' in dailies
    assert 'DailyItemRewards' in dailies

    # Sale
    assert 'SaleType' in dailies
    assert 'SaleArgument' in dailies
    assert 'SaleItemMask' in dailies

    # News messages
    assert 'News' in dailies
    assert 'NewsUpdateDate' in dailies
    assert 'TournamentNews' in dailies
    assert 'NewsSpriteId' in dailies


def test_sprites():
    pixel_starships_api = PixelStarshipsApi()
    sprites = pixel_starships_api.get_sprites()

    assert len(sprites) > 0

    sprite = sprites[0]

    assert 'SpriteId' in sprite
    assert 'ImageFileId' in sprite
    assert 'X' in sprite
    assert 'Y' in sprite
    assert 'Width' in sprite
    assert 'Height' in sprite
    assert 'SpriteKey' in sprite


def test_ships():
    pixel_starships_api = PixelStarshipsApi()
    ships = pixel_starships_api.get_ships()

    assert len(ships) > 0

    ship = ships[0]
    assert 'ShipDesignName' in ship
    assert 'ShipDescription' in ship
    assert 'ShipLevel' in ship
    assert 'Hp' in ship
    assert 'RepairTime' in ship
    assert 'InteriorSpriteId' in ship
    assert 'ExteriorSpriteId' in ship
    assert 'LogoSpriteId' in ship
    assert 'MiniShipSpriteId' in ship
    assert 'RoomFrameSpriteId' in ship
    assert 'DoorFrameLeftSpriteId' in ship
    assert 'DoorFrameRightSpriteId' in ship
    assert 'Rows' in ship
    assert 'Columns' in ship
    assert 'RaceId' in ship
    assert 'Mask' in ship
    assert 'MineralCost' in ship
    assert 'StarbuxCost' in ship
    assert 'MineralCapacity' in ship
    assert 'GasCapacity' in ship
    assert 'EquipmentCapacity' in ship
    assert 'ShipType' in ship


def test_researches():
    pixel_starships_api = PixelStarshipsApi()
    researches = pixel_starships_api.get_researches()

    assert len(researches) > 0

    research = researches[0]
    assert 'ResearchName' in research
    assert 'ResearchDescription' in research
    assert 'GasCost' in research
    assert 'StarbuxCost' in research
    assert 'RequiredLabLevel' in research
    assert 'ResearchTime' in research
    assert 'LogoSpriteId' in research
    assert 'ImageSpriteId' in research
    assert 'RequiredResearchDesignId' in research
    assert 'ResearchDesignType' in research


def test_rooms():
    pixel_starships_api = PixelStarshipsApi()
    rooms = pixel_starships_api.get_rooms()

    assert len(rooms) > 0

    room = rooms[0]
    assert 'RoomName' in room
    assert 'RoomShortName' in room
    assert 'RoomType' in room
    assert 'Level' in room
    assert 'Capacity' in room
    assert 'Rows' in room
    assert 'Columns' in room
    assert 'ImageSpriteId' in room
    assert 'ConstructionSpriteId' in room
    assert 'MaxSystemPower' in room
    assert 'MaxPowerGenerated' in room
    assert 'MinShipLevel' in room
    assert 'UpgradeFromRoomDesignId' in room
    assert 'DefaultDefenceBonus' in room
    assert 'ReloadTime' in room
    assert 'RefillUnitCost' in room
    assert 'RoomType' in room
    assert 'PriceString' in room
    assert 'PriceString' in room
    assert 'ConstructionTime' in room
    assert 'RoomDescription' in room
    assert 'ManufactureType' in room

    room_with_missile_design = None
    for room in rooms:
        if room['MissileDesign']:
            room_with_missile_design = room
            break

    assert room_with_missile_design
    assert 'SystemDamage' in room_with_missile_design['MissileDesign']
    assert 'HullDamage' in room_with_missile_design['MissileDesign']
    assert 'CharacterDamage' in room_with_missile_design['MissileDesign']

    room_with_purchase = None
    for room in rooms:
        if room['AvailabilityMask']:
            room_with_purchase = room
            break

    assert room_with_purchase
    assert 'AvailabilityMask' in room_with_purchase


def test_rooms_sprites():
    pixel_starships_api = PixelStarshipsApi()
    rooms_sprites = pixel_starships_api.get_rooms_sprites()

    assert len(rooms_sprites) > 0

    room_sprite = rooms_sprites[0]
    assert 'RoomDesignId' in room_sprite
    assert 'RaceId' in room_sprite
    assert 'SpriteId' in room_sprite
    assert 'RoomSpriteType' in room_sprite
    assert 'SkinName' in room_sprite
    assert 'SkinDescription' in room_sprite
    assert 'SkinKey' in room_sprite
    assert 'RequirementString' in room_sprite


def test_characters():
    pixel_starships_api = PixelStarshipsApi()
    characters = pixel_starships_api.get_characters()

    assert len(characters) > 0

    character = characters[0]
    assert 'CharacterDesignName' in character
    assert 'ProfileSpriteId' in character
    assert 'Rarity' in character
    assert 'Hp' in character
    assert 'FinalHp' in character
    assert 'Pilot' in character
    assert 'FinalPilot' in character
    assert 'Attack' in character
    assert 'FinalAttack' in character
    assert 'Repair' in character
    assert 'FinalRepair' in character
    assert 'Weapon' in character
    assert 'FinalWeapon' in character
    assert 'Engine' in character
    assert 'FinalEngine' in character
    assert 'Research' in character
    assert 'FinalResearch' in character
    assert 'Science' in character
    assert 'FinalScience' in character
    assert 'SpecialAbilityArgument' in character
    assert 'SpecialAbilityFinalArgument' in character
    assert 'SpecialAbilityType' in character
    assert 'FireResistance' in character
    assert 'WalkingSpeed' in character
    assert 'RunSpeed' in character
    assert 'TrainingCapacity' in character
    assert 'ProgressionType' in character
    assert 'CollectionDesignId' in character
    assert 'EquipmentMask' in character

    parts = character['CharacterParts']
    assert 'StandardSpriteId' in parts['Head']
    assert 'StandardSpriteId' in parts['Body']
    assert 'StandardSpriteId' in parts['Leg']


def test_collections():
    pixel_starships_api = PixelStarshipsApi()
    collections = pixel_starships_api.get_collections()

    assert len(collections) > 0

    collection = collections[0]
    assert 'CollectionName' in collection
    assert 'MinCombo' in collection
    assert 'MaxCombo' in collection
    assert 'BaseEnhancementValue' in collection
    assert 'SpriteId' in collection
    assert 'StepEnhancementValue' in collection
    assert 'IconSpriteId' in collection
    assert 'TriggerType' in collection
    assert 'BaseChance' in collection
    assert 'StepChance' in collection
    assert 'MaxUse' in collection


def test_items():
    pixel_starships_api = PixelStarshipsApi()
    items = pixel_starships_api.get_items()

    assert len(items) > 0

    item = items[0]
    assert 'ItemDesignName' in item
    assert 'ItemDesignDescription' in item
    assert 'ImageSpriteId' in item
    assert 'ItemSubType' in item
    assert 'EnhancementType' in item
    assert 'Ingredients' in item
    assert 'Content' in item
    assert 'MarketPrice' in item
    assert 'FairPrice' in item
    assert 'ItemDesignId' in item
    assert 'ItemType' in item
    assert 'Rarity' in item
    assert 'EnhancementValue' in item
    assert 'ItemSpace' in item
    assert 'RequirementString' in item


def test_alliances():
    pixel_starships_api = PixelStarshipsApi()
    alliances = pixel_starships_api.get_alliances(42)

    assert len(alliances) == 42

    alliance = alliances[0]
    assert 'AllianceId' in alliance
    assert 'AllianceName' in alliance


def test_sales():
    pixel_starships_api = PixelStarshipsApi()
    sales = pixel_starships_api.get_sales(73, 0, 1)  # Power Drill

    assert len(sales) == 1

    sale = sales[0]
    assert 'SaleId' in sale
    assert 'StatusDate' in sale
    assert 'Quantity' in sale
    assert 'CurrencyType' in sale
    assert 'CurrencyValue' in sale
    assert 'BuyerShipId' in sale
    assert 'BuyerShipName' in sale
    assert 'BuyerShipName' in sale
    assert 'SellerShipId' in sale
    assert 'SellerShipName' in sale
    assert 'ItemId' in sale


def test_users():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()

    users = pixel_starships_api.get_users()  # top 10
    assert len(users) == 100

    user = users[0]
    assert 'Id' in user
    assert 'Name' in user
    assert 'Trophy' in user
    assert 'AllianceId' in user
    assert 'LastLoginDate' in user
    assert 'AllianceName' in user
    assert 'AllianceSpriteId' in user


def test_alliance_users():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()

    alliance_id = 9343  # Trek Federation
    users = pixel_starships_api.get_alliance_users(alliance_id)
    assert len(users) > 0

    user = users[0]
    assert 'Id' in user
    assert 'Name' in user
    assert 'Trophy' in user
    assert 'AllianceId' in user
    assert 'LastLoginDate' in user
    assert 'AllianceName' in user
    assert 'AllianceSpriteId' in user


def test_prestiges_character_to():
    pixel_starships_api = PixelStarshipsApi()

    character_id = 196  # PinkZilla
    prestiges = pixel_starships_api.get_prestiges_character_to(character_id)
    assert len(prestiges) > 0

    prestige = prestiges[0]
    assert 'CharacterDesignId1' in prestige
    assert 'CharacterDesignId2' in prestige


def test_prestiges_character_from():
    pixel_starships_api = PixelStarshipsApi()

    character_id = 338  # Zongzi-Man
    prestiges = pixel_starships_api.get_prestiges_character_from(character_id)
    assert len(prestiges) > 0

    prestige = prestiges[0]
    assert 'CharacterDesignId1' in prestige
    assert 'CharacterDesignId2' in prestige


def test_rooms_purchase():
    pixel_starships_api = PixelStarshipsApi()
    rooms_purchase = pixel_starships_api.get_rooms_purchase()

    assert len(rooms_purchase) > 0

    room_purchase = rooms_purchase[0]
    assert 'RoomDesignId' in room_purchase
    assert 'AvailabilityMask' in room_purchase


def test_exact_match_search_users():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    user_name_to_search = 'Solevis'
    users = pixel_starships_api.search_users(user_name_to_search, True)

    assert len(users) == 1

    user = users[0]
    assert 'Name' in user
    assert user['Name'] == user_name_to_search

    assert 'PVPAttackWins' in user
    assert 'PVPAttackLosses' in user
    assert 'PVPAttackDraws' in user
    assert 'PVPDefenceDraws' in user
    assert 'PVPDefenceWins' in user
    assert 'PVPDefenceLosses' in user
    assert 'HighestTrophy' in user
    assert 'CrewDonated' in user
    assert 'CrewReceived' in user
    assert 'AllianceJoinDate' in user
    assert 'CreationDate' in user


def test_search_users():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    user_name_to_search = 'Sol'
    users = pixel_starships_api.search_users(user_name_to_search, False)

    assert len(users) > 1

    user = users[0]
    assert 'Name' in user
    assert 'PVPAttackWins' in user
    assert 'PVPAttackLosses' in user
    assert 'PVPAttackDraws' in user
    assert 'PVPDefenceDraws' in user
    assert 'PVPDefenceWins' in user
    assert 'PVPDefenceLosses' in user
    assert 'HighestTrophy' in user
    assert 'CrewDonated' in user
    assert 'CrewReceived' in user
    assert 'AllianceJoinDate' in user
    assert 'CreationDate' in user


def test_trainings():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    trainings = pixel_starships_api.get_trainings()

    assert len(trainings) > 0

    training = trainings[0]

    assert 'TrainingDesignId' in training
    assert 'TrainingSpriteId' in training
    assert 'HpChance' in training
    assert 'AttackChance' in training
    assert 'PilotChance' in training
    assert 'RepairChance' in training
    assert 'WeaponChance' in training
    assert 'ScienceChance' in training
    assert 'EngineChance' in training
    assert 'StaminaChance' in training
    assert 'AbilityChance' in training
    assert 'XpChance' in training
    assert 'Fatigue' in training
    assert 'MinimumGuarantee' in training


def test_achievements():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    achievements = pixel_starships_api.get_achievements()

    assert len(achievements) > 0

    achievement = achievements[0]

    assert 'AchievementDesignId' in achievement
    assert 'AchievementTitle' in achievement
    assert 'AchievementDescription' in achievement
    assert 'SpriteId' in achievement
    assert 'RewardString' in achievement
    assert 'ParentAchievementDesignId' in achievement


def test_situations():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    situations = pixel_starships_api.get_situations()

    assert len(situations) > 0

    situation = situations[0]

    assert 'SituationDesignId' in situation
    assert 'SituationName' in situation
    assert 'SituationDescription' in situation
    assert 'FromDate' in situation
    assert 'EndDate' in situation
    assert 'IconSpriteId' in situation


def test_promotions():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    promotions = pixel_starships_api.get_promotions()

    assert len(promotions) > 0

    promotion = promotions[0]

    assert 'PromotionDesignId' in promotion
    assert 'PromotionType' in promotion
    assert 'Title' in promotion
    assert 'SubTitle' in promotion
    assert 'Description' in promotion
    assert 'RewardString' in promotion
    assert 'FromDate' in promotion
    assert 'ToDate' in promotion
    assert 'PackId' in promotion


def test_star_system_markers():
    # avoid Flask RuntimeError: No application found
    push_context()

    pixel_starships_api = PixelStarshipsApi()
    markers = pixel_starships_api.get_star_system_markers()

    assert len(markers) > 0

    marker = markers[0]

    assert 'CostString' in marker
    assert 'RewardString' in marker
    assert 'MarkerType' in marker
    assert 'Title' in marker
    assert 'ExpiryDate' in marker


def test_crafts():
    pixel_starships_api = PixelStarshipsApi()
    crafts = pixel_starships_api.get_crafts()

    assert len(crafts) > 0

    craft = crafts[0]
    assert 'CraftName' in craft
    assert 'FlightSpeed' in craft
    assert 'Reload' in craft
    assert 'ReloadModifier' in craft
    assert 'Volley' in craft
    assert 'VolleyDelay' in craft
    assert 'AttackDistance' in craft
    assert 'AttackRange' in craft
    assert 'Hp' in craft
    assert 'CraftAttackType' in craft
    assert 'SpriteId' in craft
    assert 'SystemDamage' in craft['MissileDesign']
    assert 'HullDamage' in craft['MissileDesign']
    assert 'CharacterDamage' in craft['MissileDesign']
    assert 'ShieldDamage' in craft['MissileDesign']
    assert 'DirectSystemDamage' in craft['MissileDesign']
    assert 'Volley' in craft['MissileDesign']
    assert 'VolleyDelay' in craft['MissileDesign']
    assert 'Speed' in craft['MissileDesign']
    assert 'FireLength' in craft['MissileDesign']
    assert 'EMPLength' in craft['MissileDesign']
    assert 'StunLength' in craft['MissileDesign']
    assert 'HullPercentageDamage' in craft['MissileDesign']


def test_missiles():
    pixel_starships_api = PixelStarshipsApi()
    missiles = pixel_starships_api.get_missiles()

    assert len(missiles) > 0

    missile = missiles[0]
    assert 'ItemDesignName' in missile
    assert 'BuildTime' in missile
    assert 'ManufactureCost' in missile
    assert 'ReloadModifier' in missile
    assert 'ImageSpriteId' in missile
    assert 'ReloadModifier' in missile
    assert 'SystemDamage' in missile['MissileDesign']
    assert 'HullDamage' in missile['MissileDesign']
    assert 'CharacterDamage' in missile['MissileDesign']
    assert 'ShieldDamage' in missile['MissileDesign']
    assert 'DirectSystemDamage' in missile['MissileDesign']
    assert 'Volley' in missile['MissileDesign']
    assert 'VolleyDelay' in missile['MissileDesign']
    assert 'Speed' in missile['MissileDesign']
    assert 'FireLength' in missile['MissileDesign']
    assert 'EMPLength' in missile['MissileDesign']
    assert 'StunLength' in missile['MissileDesign']
    assert 'HullPercentageDamage' in missile['MissileDesign']


def test_skins():
    pixel_starships_api = PixelStarshipsApi()
    skinsets, skins = pixel_starships_api.get_skins()

    assert len(skinsets) > 0
    assert len(skins) > 0

    skinset = skinsets[0]
    assert 'SkinSetName' in skinset
    assert 'SkinSetDescription' in skinset
    assert 'SkinSetId' in skinset
    assert 'SpriteId' in skinset

    skin = skins[0]
    assert 'SkinSetId' in skin
    assert 'SkinType' in skin
    assert 'SpriteType' in skin
    assert 'RootId' in skin
    assert 'RaceId' in skin
    assert 'SpriteId' in skin
