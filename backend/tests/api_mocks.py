"""Mock data and functions for testing."""

from unittest.mock import MagicMock


def mock_api_settings() -> dict[str, str]:
    """Return mock API settings."""
    return {
        "ProductionServer": "api.example.com",
        "MaintenanceMessage": "",
        "ShipDesignVersion": "1",
        "FileVersion": "1",
        "RoomDesignSpriteVersion": "1",
        "SkinSetVersion": "1",
        "SkinVersion": "1",
        "CraftDesignVersion": "1",
        "MissileDesignVersion": "1",
        "ItemDesignVersion": "1",
        "CharacterDesignVersion": "1",
        "CollectionDesignVersion": "1",
        "ResearchDesignVersion": "1",
        "RoomDesignPurchaseVersion": "1",
        "TrainingDesignVersion": "1",
        "AchievementDesignVersion": "1",
        "SituationDesignVersion": "1",
        "PromotionDesignVersion": "1",
    }


def mock_xml_response(xml_content: str) -> MagicMock:
    """Create a mock response object with XML content."""
    mock_response = MagicMock()
    mock_response.text = xml_content
    mock_response.content = xml_content.encode("utf-8")
    mock_response.status_code = 200
    mock_response.encoding = "utf-8"
    return mock_response


def mock_device_login_response() -> MagicMock:
    """Create a mock device login response."""
    xml_content = """
    <Response>
        <UserLogin accessToken="mock-device-token-12345678-1234-1234-1234-123456789012"/>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_inspect_ship_response() -> MagicMock:
    """Create a mock inspect ship response."""
    xml_content = """
    <Response>
        <User Id="6635604" Name="Solevis" IconSpriteId="123" AllianceName="Test Alliance"
              AllianceSpriteId="456" Trophy="1000" LastAlertDate="2023-01-01T00:00:00"/>
        <Ship ShipDesignId="1" OriginalRaceId="1">
            <Rooms>
                <Room RoomId="1" Row="0" Column="0" ConstructionStartDate="2023-01-01T00:00:00"/>
            </Rooms>
        </Ship>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_ship_details_response() -> MagicMock:
    """Create a mock ship details response."""
    xml_content = """
    <Response>
        <Ship ShipDesignId="1" OriginalRaceId="1"/>
        <User Id="6635604" Name="Solevis" IconSpriteId="123" AllianceName="Test Alliance"
              Trophy="1000" AllianceSpriteId="456" LastAlertDate="2023-01-01T00:00:00"/>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_ship_room_details_response() -> MagicMock:
    """Create a mock ship room details response."""
    xml_content = """
    <Response>
        <Rooms>
            <Room RoomDesignId="1" CurrentSkinKey="default" Row="0" Column="0" ConstructionStartDate="2023-01-01T00:00:00"/>
        </Rooms>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_dailies_response() -> MagicMock:
    """Create a mock dailies response."""
    xml_content = """
    <Response>
        <LiveOps LimitedCatalogCurrencyAmount="100" LimitedCatalogType="Starbux"
                 LimitedCatalogArgument="1" LimitedCatalogCurrencyType="Starbux"
                 LimitedCatalogQuantity="1" LimitedCatalogMaxTotal="10"
                 LimitedCatalogExpiryDate="2023-12-31T23:59:59" CommonCrewId="1"
                 HeroCrewId="2" CargoItems="item1,item2" CargoPrices="10,20"
                 DailyRewardArgument="reward1" DailyRewardType="Daily"
                 DailyItemRewards="reward1,reward2" SaleType="Sale" SaleArgument="arg1"
                 SaleItemMask="1" News="Test news" NewsUpdateDate="2023-01-01T00:00:00"
                 TournamentNews="Tournament news" NewsSpriteId="123"/>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_sprites_response() -> MagicMock:
    """Create a mock sprites response."""
    xml_content = """
    <Response>
        <Sprites>
            <Sprite SpriteId="1" ImageFileId="1" X="0" Y="0" Width="32" Height="32" SpriteKey="test"/>
        </Sprites>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_ships_response() -> MagicMock:
    """Create a mock ships response."""
    xml_content = """
    <Response>
        <ShipDesigns>
            <ShipDesign ShipDesignName="Test Ship" ShipDescription="A test ship" ShipLevel="1"
                        Hp="1000" RepairTime="60" InteriorSpriteId="1" ExteriorSpriteId="2"
                        LogoSpriteId="3" MiniShipSpriteId="4" RoomFrameSpriteId="5"
                        DoorFrameLeftSpriteId="6" DoorFrameRightSpriteId="7" Rows="5" Columns="5"
                        RaceId="1" Mask="1" MineralCost="1000" StarbuxCost="100" MineralCapacity="1000"
                        GasCapacity="1000" EquipmentCapacity="100" ShipType="Standard"/>
        </ShipDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_researches_response() -> MagicMock:
    """Create a mock researches response."""
    xml_content = """
    <Response>
        <ResearchDesigns>
            <ResearchDesign ResearchName="Test Research" ResearchDescription="Test description"
                           GasCost="100" StarbuxCost="10" RequiredLabLevel="1" ResearchTime="60"
                           LogoSpriteId="1" ImageSpriteId="2" RequiredResearchDesignId="0"
                           ResearchDesignType="Standard"/>
        </ResearchDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_rooms_response() -> MagicMock:
    """Create a mock rooms response."""
    xml_content = """
    <Response>
        <RoomDesigns>
            <RoomDesign RoomName="Test Room" RoomShortName="Test" RoomType="Standard" Level="1"
                        Capacity="10" Rows="1" Columns="1" ImageSpriteId="1" ConstructionSpriteId="2"
                        MaxSystemPower="100" MaxPowerGenerated="10" MinShipLevel="1"
                        UpgradeFromRoomDesignId="0" DefaultDefenceBonus="0" ReloadTime="10"
                        RefillUnitCost="5" PriceString="100" ConstructionTime="60"
                        RoomDescription="Test room" ManufactureType="None" ActivationDelay="0">
                <MissileDesign SystemDamage="10" HullDamage="5" CharacterDamage="2"/>
            </RoomDesign>
        </RoomDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_rooms_sprites_response() -> MagicMock:
    """Create a mock rooms sprites response."""
    xml_content = """
    <Response>
        <RoomDesignSprites>
            <RoomDesignSprite RoomDesignId="1" RaceId="1" SpriteId="1" RoomSpriteType="Standard"
                             SkinName="Default" SkinDescription="Default skin" SkinKey="default"
                             RequirementString="None"/>
        </RoomDesignSprites>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_characters_response() -> MagicMock:
    """Create a mock characters response."""
    xml_content = """
    <Response>
        <CharacterDesigns>
            <CharacterDesign CharacterDesignName="Test Character" ProfileSpriteId="1" Rarity="Common"
                            Hp="100" FinalHp="150" Pilot="10" FinalPilot="15" Attack="10"
                            FinalAttack="15" Repair="10" FinalRepair="15" Weapon="10" FinalWeapon="15"
                            Engine="10" FinalEngine="15" Research="10" FinalResearch="15" Science="10"
                            FinalScience="15" SpecialAbilityArgument="0" SpecialAbilityFinalArgument="0"
                            SpecialAbilityType="None" FireResistance="0" WalkingSpeed="1" RunSpeed="2"
                            TrainingCapacity="1" ProgressionType="Standard" CollectionDesignId="0"
                            EquipmentMask="0">
                <CharacterParts>
                    <CharacterPart CharacterPartType="Head" StandardSpriteId="1"/>
                    <CharacterPart CharacterPartType="Body" StandardSpriteId="2"/>
                    <CharacterPart CharacterPartType="Leg" StandardSpriteId="3"/>
                </CharacterParts>
            </CharacterDesign>
        </CharacterDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_collections_response() -> MagicMock:
    """Create a mock collections response."""
    xml_content = """
    <Response>
        <CollectionDesigns>
            <CollectionDesign CollectionName="Test Collection" MinCombo="2" MaxCombo="5"
                             BaseEnhancementValue="10" SpriteId="1" StepEnhancementValue="5"
                             IconSpriteId="2" TriggerType="Passive" BaseChance="50" StepChance="10"
                             MaxUse="10" AbilityIconSpriteId="3" AbilityName="Test Ability"
                             CooldownTime="60" Argument="0"/>
        </CollectionDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_items_response() -> MagicMock:
    """Create a mock items response."""
    xml_content = """
    <Response>
        <ItemDesigns>
            <ItemDesign ItemDesignName="Test Item" ItemDesignDescription="Test item" ImageSpriteId="1"
                        ItemSubType="None" EnhancementType="None" Ingredients="" Content=""
                        MarketPrice="100" FairPrice="150" ItemDesignId="1" ItemType="Standard"
                        Rarity="Common" EnhancementValue="0" ItemSpace="1" RequirementString="None"/>
        </ItemDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_alliances_response() -> MagicMock:
    """Create a mock alliances response."""
    xml_content = """
    <Response>
        <Alliances>
            <Alliance AllianceId="1" AllianceName="Test Alliance"/>
            <Alliance AllianceId="2" AllianceName="Another Alliance"/>
        </Alliances>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_sales_response() -> MagicMock:
    """Create a mock sales response."""
    xml_content = """
    <Response>
        <Sales>
            <Sale SaleId="1" StatusDate="2023-01-01T00:00:00" Quantity="1" CurrencyType="Starbux"
                  CurrencyValue="100" BuyerShipId="1" BuyerShipName="Buyer" SellerShipId="2"
                  SellerShipName="Seller" ItemId="1"/>
        </Sales>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_users_response() -> MagicMock:
    """Create a mock users response."""
    xml_content = """
    <Response>
        <Users>
            <User Id="1" Name="Test User" Trophy="1000" AllianceId="1" LastLoginDate="2023-01-01T00:00:00"
                  AllianceName="Test Alliance" AllianceSpriteId="123">
                <Stats PVPAttackWins="10" PVPAttackLosses="5" PVPAttackDraws="1" PVPDefenceDraws="2"
                       PVPDefenceWins="8" PVPDefenceLosses="3" HighestTrophy="1500" CrewDonated="100"
                       CrewReceived="50" AllianceJoinDate="2023-01-01T00:00:00" CreationDate="2022-01-01T00:00:00"/>
            </User>
            <User Id="2" Name="Another User" Trophy="500" AllianceId="2" LastLoginDate="2023-01-02T00:00:00"
                  AllianceName="Another Alliance" AllianceSpriteId="456">
                <Stats PVPAttackWins="5" PVPAttackLosses="3" PVPAttackDraws="0" PVPDefenceDraws="1"
                       PVPDefenceWins="4" PVPDefenceLosses="2" HighestTrophy="800" CrewDonated="50"
                       CrewReceived="25" AllianceJoinDate="2023-01-02T00:00:00" CreationDate="2022-02-01T00:00:00"/>
            </User>
        </Users>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_prestiges_response() -> MagicMock:
    """Create a mock prestiges response."""
    xml_content = """
    <Response>
        <Prestiges>
            <Prestige CharacterDesignId1="1" CharacterDesignId2="2"/>
        </Prestiges>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_rooms_purchase_response() -> MagicMock:
    """Create a mock rooms purchase response."""
    xml_content = """
    <Response>
        <RoomDesignPurchases>
            <RoomDesignPurchase RoomDesignId="1" AvailabilityMask="1"/>
        </RoomDesignPurchases>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_trainings_response() -> MagicMock:
    """Create a mock trainings response."""
    xml_content = """
    <Response>
        <TrainingDesigns>
            <TrainingDesign TrainingDesignId="1" TrainingSpriteId="1" HpChance="10" AttackChance="10"
                           PilotChance="10" RepairChance="10" WeaponChance="10" ScienceChance="10"
                           EngineChance="10" StaminaChance="10" AbilityChance="10" XpChance="10"
                           Fatigue="5" MinimumGuarantee="1" TrainingName="Test Training"/>
        </TrainingDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_achievements_response() -> MagicMock:
    """Create a mock achievements response."""
    xml_content = """
    <Response>
        <AchievementDesigns>
            <AchievementDesign AchievementDesignId="1" AchievementTitle="Test Achievement"
                              AchievementDescription="Test description" SpriteId="1" RewardString="Reward"
                              ParentAchievementDesignId="0"/>
        </AchievementDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_situations_response() -> MagicMock:
    """Create a mock situations response."""
    xml_content = """
    <Response>
        <SituationDesigns>
            <SituationDesign SituationDesignId="1" SituationName="Test Situation"
                           SituationDescription="Test description" FromDate="2023-01-01T00:00:00"
                           EndDate="2023-12-31T23:59:59" IconSpriteId="1"/>
        </SituationDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_promotions_response() -> MagicMock:
    """Create a mock promotions response."""
    xml_content = """
    <Response>
        <PromotionDesigns>
            <PromotionDesign PromotionDesignId="1" PromotionType="Standard" Title="Test Promotion"
                           SubTitle="Subtitle" Description="Test promotion" RewardString="Reward"
                           FromDate="2023-01-01T00:00:00" ToDate="2023-12-31T23:59:59" PackId="1"/>
        </PromotionDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_star_system_markers_response() -> MagicMock:
    """Create a mock star system markers response."""
    xml_content = """
    <Response>
        <StarSystemMarkers>
            <StarSystemMarker CostString="100" RewardString="Reward" MarkerType="Standard"
                             Title="Test Marker" ExpiryDate="2023-12-31T23:59:59"/>
        </StarSystemMarkers>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_crafts_response() -> MagicMock:
    """Create a mock crafts response."""
    xml_content = """
    <Response>
        <CraftDesigns>
            <CraftDesign CraftName="Test Craft" FlightSpeed="10" Reload="5" ReloadModifier="1"
                        Volley="1" VolleyDelay="1" AttackDistance="10" AttackRange="5" Hp="100"
                        CraftAttackType="Standard" SpriteId="1" MissileDesignId="1">
                <MissileDesign SystemDamage="10" HullDamage="5" CharacterDamage="2" ShieldDamage="1"
                              DirectSystemDamage="0" Volley="1" VolleyDelay="1" Speed="10" FireLength="1"
                              EMPLength="0" StunLength="0" HullPercentageDamage="0" ExplosionRadius="1"/>
            </CraftDesign>
        </CraftDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_missiles_response() -> MagicMock:
    """Create a mock missiles response."""
    xml_content = """
    <Response>
        <ItemDesigns>
            <ItemDesign ItemDesignName="Test Missile" BuildTime="60" ManufactureCost="100"
                        ReloadModifier="1" ImageSpriteId="1" ItemType="Missile" MissileDesignId="1">
                <MissileDesign SystemDamage="10" HullDamage="5" CharacterDamage="2" ShieldDamage="1"
                              DirectSystemDamage="0" Volley="1" VolleyDelay="1" Speed="10" FireLength="1"
                              EMPLength="0" StunLength="0" HullPercentageDamage="0" ExplosionRadius="1"/>
            </ItemDesign>
        </ItemDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_skins_response() -> MagicMock:
    """Create a mock skins response."""
    xml_content = """
    <Response>
        <Skins>
            <Skin SkinSetId="1" SkinType="Standard" SpriteType="Standard" RootId="1" RaceId="1"
                 SpriteId="1"/>
        </Skins>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_skinsets_response() -> MagicMock:
    """Create a mock skinsets response."""
    xml_content = """
    <Response>
        <SkinSets>
            <SkinSet SkinSetName="Test SkinSet" SkinSetDescription="Test description" SkinSetId="1"
                    SpriteId="1"/>
        </SkinSets>
    </Response>
    """
    return mock_xml_response(xml_content)


def mock_missile_designs_response() -> MagicMock:
    """Create a mock missile designs response."""
    xml_content = """
    <Response>
        <MissileDesigns>
            <MissileDesign MissileDesignId="1" SystemDamage="10" HullDamage="5" CharacterDamage="2"
                          ShieldDamage="1" DirectSystemDamage="0" Volley="1" VolleyDelay="1" Speed="10"
                          FireLength="1" EMPLength="0" StunLength="0" HullPercentageDamage="0"
                          ExplosionRadius="1"/>
        </MissileDesigns>
    </Response>
    """
    return mock_xml_response(xml_content)
