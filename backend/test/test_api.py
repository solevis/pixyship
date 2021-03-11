from pixelstarshipsapi import PixelStarshipsApi
from run import push_context


def test_login():
    pixel_starships_api = PixelStarshipsApi()

    device_key, device_checksum = pixel_starships_api.generate_device()
    token = pixel_starships_api.get_device_token(device_key, device_checksum)

    assert isinstance(token, str)
    assert len(token) == 36


def test_settings():
    pixel_starships_api = PixelStarshipsApi()

    settings = pixel_starships_api.get_api_settings()

    assert 'ProductionServer' in settings


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
    assert 'ImmunityDate' in ship

    # Room
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

    # News messages
    assert 'News' in dailies
    assert 'NewsUpdateDate' in dailies
    assert 'MaintenanceMessage' in dailies
    assert 'TournamentNews' in dailies


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
    assert 'MarketPrice' in item
    assert 'FairPrice' in item
    assert 'ItemDesignId' in item
    assert 'ItemType' in item
    assert 'Rarity' in item
    assert 'EnhancementValue' in item


def test_alliances():
    pixel_starships_api = PixelStarshipsApi()
    alliances = pixel_starships_api.get_alliances(42)

    assert len(alliances) == 42

    alliance = alliances[0]
    assert 'AllianceId' in alliance
    assert 'AllianceName' in alliance


def test_sales():
    pixel_starships_api = PixelStarshipsApi()
    sales = pixel_starships_api.get_sales(131, 0, 1)  # Scratchy

    assert len(sales) == 1

    sale = sales[0]
    assert 'SaleId' in sale
    assert 'StatusDate' in sale
    assert 'Quantity' in sale
    assert 'CurrencyType' in sale
    assert 'CurrencyValue' in sale
    assert 'BuyerShipId' in sale


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
