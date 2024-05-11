from xml.etree import ElementTree

from flask import current_app

from app.constants import (
    COLLECTION_ABILITY_MAP,
    COLLECTION_ABILITY_TRIGGER_DESC_MAP,
    COLLECTION_ABILITY_TRIGGER_MAP,
    FRAME_SIZE,
    SHORT_ENHANCE_MAP,
    SPECIAL_ABILITY_TYPE_MAP,
)
from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class CollectionService(BaseService):
    """Service to manage collections."""

    def __init__(self) -> None:
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._collections: dict[int, dict] = {}

    @property
    def collections(self) -> dict[int, dict]:
        """Get collections data."""
        if not self._collections:
            self._collections = self.get_collections_from_records()

        return self._collections

    def get_collections_from_records(self) -> dict[int, dict]:
        """Load collections from database."""
        records = self.record_service.records[TypeEnum.COLLECTION]

        collections = {}
        for record in records.values():
            collection_node = ElementTree.fromstring(record.data)
            collection = PixelStarshipsApi.parse_collection_node(collection_node)

            max_use = int(collection["MaxUse"])
            cooldown_time = int(collection["CooldownTime"])
            trigger_type = collection["TriggerType"]
            ability_description = self.get_ability_description(
                collection["EnhancementType"],
                int(collection["BaseChance"]),
                int(collection["BaseEnhancementValue"]),
                int(collection["Argument"]),
                trigger_type,
            )

            collections[record.type_id] = {
                "id": int(collection["CollectionDesignId"]),
                "name": collection["CollectionName"],
                "min": int(collection["MinCombo"]),
                "max": int(collection["MaxCombo"]),
                "base_enhancement": int(collection["BaseEnhancementValue"]),
                "sprite": self.sprite_service.get_sprite_infos(int(collection["SpriteId"])),
                "step_enhancement": float(collection["StepEnhancementValue"]),
                "icon_sprite": self.sprite_service.get_sprite_infos(int(collection["IconSpriteId"])),
                "chars": [],
                "ability_sprite": self.sprite_service.get_sprite_infos(int(collection["AbilityIconSpriteId"])),
                "ability_name": self.get_ability_name(collection["AbilityName"], collection["EnhancementType"]),
                "ability_description": ability_description,
                "trigger_description": self.get_trigger_description(trigger_type, max_use, cooldown_time),
                "base_chance": int(collection["BaseChance"]),
                "step_chance": int(collection["StepChance"]),
                "max_use": max_use,
                "description": collection["CollectionDescription"],
            }

        return collections

    @staticmethod
    def get_trigger_name(trigger_type: str) -> str:
        """Get collection trigger name."""
        trigger_name = COLLECTION_ABILITY_TRIGGER_MAP.get(trigger_type)
        if trigger_name is None:
            current_app.logger.warning("Unknown collection trigger type: %s", trigger_type)
            return trigger_type

        return trigger_name

    @staticmethod
    def get_ability_name(ability_name: str, enhancement: str) -> str:
        """Get collection ability name."""
        if ability_name:
            return ability_name

        ability_map_get = COLLECTION_ABILITY_MAP.get(enhancement)
        if ability_map_get is None:
            current_app.logger.warning("Unknown collection ability enhancement: %s", enhancement)
            return enhancement

        return ability_map_get

    @staticmethod
    def get_trigger_description(trigger_type: str, max_use: int, cooldown: int) -> str:
        """Get collection ability description."""
        trigger_desc = COLLECTION_ABILITY_TRIGGER_DESC_MAP.get(trigger_type)
        if not trigger_desc:
            current_app.logger.warning("Unknown collection trigger type: %s", trigger_type)
            return ""

        if max_use < 10000:
            if max_use > 1:
                trigger_desc += f"Can only be activated {max_use} times."
            elif max_use == 1:
                trigger_desc += "Can only be activated once."

        if cooldown > 0:
            cooldown_in_seconds = cooldown / FRAME_SIZE
            formatted_cooldown = f"{cooldown_in_seconds:0.2f}".rstrip("0").rstrip(".")  # Remove trailing zeros
            trigger_desc += f"Has a {formatted_cooldown} seconds cooldown."

        return trigger_desc

    def get_ability_description(
        self, enhancement_type: str, base_chance: int, base_enhancement_value: int, argument: int, trigger_type: str
    ) -> str:
        """Get collection ability description."""
        enhancement_map = {
            "FireSkill": lambda: f"{base_chance}% chance to inflict a {base_enhancement_value / FRAME_SIZE:.1f} seconds of fire on the current enemy room.",
            "EmpSkill": lambda: f"{base_chance}% chance to inflict a {base_enhancement_value / FRAME_SIZE:.1f} seconds EMP stun on the current enemy room.",
            "SharpShooterSkill": lambda: f"{base_chance}% chance to deal {base_enhancement_value}% of current attack damage to a target enemy crew or an enemy crew in current room.",
            "ResurrectSkill": lambda: f"{base_chance}% chance to revive a friendly crew in current room with {base_enhancement_value}% hp when they are killed."
            if trigger_type == "AllyDeath"
            else f"{base_chance}% chance to revive with {base_enhancement_value}% hp when killed.",
            "BloodThirstSkill": lambda: self.handle_blood_thirst_skill(
                base_chance, base_enhancement_value, trigger_type
            ),
            "MedicalSkill": lambda: f"{base_chance}% chance to heal the lowest hp target of other friendly crews in current room for {(base_enhancement_value / 100.0):.1f}hp.",
            "FreezeAttackSkill": lambda: f"{base_chance}% chance to inflict a {base_enhancement_value / FRAME_SIZE:.1f} seconds freeze on a target enemy crew or an enemy crew in current room.",
            "InstantKillSkill": lambda: f"{base_chance}% chance to reduce {base_enhancement_value}% of the hp of the target or an enemy crew in current room.",
            "ApplyArmorSkill": lambda: f"{base_chance}% chance to increase the current room's armor by {base_enhancement_value}, up to a maximum of {argument} bonus armor (including bonuses from other sources)."
            if argument > 0
            else f"{base_chance}% chance to increase the current room's armor by {base_enhancement_value}.",
            "CastAbilitySkill": lambda: self.handle_cast_ability_skill(base_chance, base_enhancement_value, argument),
            "CastAssignedAbilitySkill": lambda: self.handle_cast_assigned_ability_skill(
                base_chance, base_enhancement_value
            ),
            "DamageReductionSkill": lambda: f"{base_chance}% chance to apply a {base_enhancement_value}% damage reduction to self or friendly crew for {argument / FRAME_SIZE:.1f} seconds.",
            "DamageReductionTimeSkill": lambda: f"{base_chance}% chance to apply a {argument}% damage reduction to self or friendly crew for {base_enhancement_value / FRAME_SIZE:.1f} seconds.",
            "GainItemSkill": lambda: self.handle_gain_item_skill(base_chance, base_enhancement_value, argument),
            "MoveSpeedBoost": lambda: self.handle_move_speed_boost(base_chance, base_enhancement_value, argument),
            "PreventDamageSkill": lambda: f"{base_chance}% chance to reduce the next {argument} instances of damage by {base_enhancement_value}. This includes any damage that triggers this ability.",
            "ReduceFutureDamage": lambda: f"{base_chance}% chance to reduce the next {argument} instances of damage by {base_enhancement_value}%. This includes any damage that triggers this ability.",
            "ReduceFutureDamageInstance": lambda: f"{base_chance}% chance to reduce the next {base_enhancement_value} instances of damage by {argument}%. This includes any damage that triggers this ability.",
            "PreventStatusSkill": lambda: self.handle_prevent_status_skill(
                base_chance, base_enhancement_value, argument
            ),
            "ReduceActionCooldown": lambda: f"{base_chance}% chance to reduce the crew's action cooldown by {base_enhancement_value / FRAME_SIZE:.1f} seconds.",
            "RepairModuleSkill": lambda: f"{base_chance}% chance to repair a module in the room by {base_enhancement_value:.1f}hp.",
            "SpawnCrewSkill": lambda: self.handle_spawn_crew_skill(base_chance, base_enhancement_value, argument),
            "SpawnModuleSkill": lambda: self.handle_spawn_module_skill(base_chance, argument),
            "StaminaRegenSkill": lambda: f"{base_chance}% chance to regenerate {base_enhancement_value} stamina.",
            "ReduceCrewStatusSkill": lambda: self.handle_reduce_crew_status_skill(
                base_chance, base_enhancement_value, argument
            ),
            "ReduceRoomStatusSkill": lambda: self.handle_reduce_room_status_skill(
                base_chance, base_enhancement_value, argument
            ),
            "RefreshAbility": lambda: f"{base_chance}% chance to refresh the crew's ability, allowing it to be activated again.",
            "DirectDamage": lambda: f"{base_chance}% chance to deal {base_enhancement_value / 100} damage to the target crew.",
            "RoomDamageBoost": lambda: f"{base_chance}% chance to increase the damage of the next {argument} weapon shots for the current room by {base_enhancement_value}%.",
            "RoomDamageBoostInstance": lambda: f"{base_chance}% chance to increase the damage of the next {base_enhancement_value} weapon shots for the current room by {argument}%.",
        }

        # Call the appropriate function based on the enhancement_type, log if unknown
        try:
            return enhancement_map[enhancement_type]()
        except KeyError:
            current_app.logger.exception("Unknown collection ability enhancement: %s", enhancement_type)
            return ""

    @staticmethod
    def handle_blood_thirst_skill(base_chance: int, base_enhancement_value: int, trigger_type: str) -> str:
        """Handle BloodThirstSkill ability."""
        if trigger_type == "AttackRoom":
            return f"{base_chance}% chance to convert {base_enhancement_value}% of attack damage dealt to enemy rooms to replenish own hp."

        if trigger_type == "AttackCrew":
            return f"{base_chance}% chance to convert {base_enhancement_value}% of attack damage dealt to enemy crews to replenish own hp."

        if trigger_type == "AttackAny":
            return f"{base_chance}% chance to convert {base_enhancement_value}% of attack damage dealt to enemy crews or rooms to replenish own hp."

        return f"{base_chance}% chance to restore {base_enhancement_value}% of max hp."

    @staticmethod
    def handle_cast_ability_skill(base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle CastAbilitySkill ability."""
        special_ability_name = SPECIAL_ABILITY_TYPE_MAP[argument]
        ability_power = SHORT_ENHANCE_MAP["Ability"]

        if base_enhancement_value > 0:
            description = f"{base_chance}% chance to activate {special_ability_name}."
        else:
            description = f"{base_chance}% chance to activate {special_ability_name} special ability using current {ability_power} power."

        ability_description = CollectionService.get_ability_description_string(
            special_ability_name, base_enhancement_value
        )
        return f"{description} {ability_description}"

    @staticmethod
    def get_ability_description_string(special_ability_name: str, base_enhancement_value: int) -> str:
        """Get ability description string."""
        ability_map = {
            "DamageToSameRoomCharacters": lambda stat: f"Deals {stat:0.0f} damage to all enemy crews in the current room.",
            "DamageToRoom": lambda stat: f"Deals {stat:0.0f} damage to the current room and all of its barrier modules and mines.",
            "DeductReload": lambda stat: f"Delays the current room's reload progress by {stat / FRAME_SIZE:0.0f} seconds. Will not trigger on unpowered rooms.",
            "DamageToCurrentEnemy": lambda stat: f"Deals {stat:0.0f} damage to the current targeted enemy crew.",
            "HealSelfHp": lambda stat: f"Restores {stat:0.0f} hp to self.",
            "HealSameRoomCharacters": lambda stat: f"Restores {stat:0.0f} hp to all friendly crews in the current room.",
            "HealRoomHp": lambda stat: f"Repairs current room for {stat:0.0f} damage.",
            "AddReload": lambda stat: f"Instantly increases reload progress of the current room by {(1 + (stat / 50)) * 100:0.0f}% divided by the room's max power.",
            "SetFire": lambda stat: f"Sets the current room on fire for {stat / FRAME_SIZE:0.0f} seconds. Fire damage dealt is proportional to the remaining fire duration.",
            "Freeze": lambda stat: f"Stops the actions of all enemy crews in the current room for {stat / FRAME_SIZE:0.0f} seconds.",
            "FireWalk": lambda stat: f"Automatically sets the current room on fire for {stat / FRAME_SIZE:0.0f} seconds. Fire damage dealt is proportional to the remaining fire duration.",
            "Invulnerability": lambda stat: f"Forms a shield that prevents status effects from affecting this crew for {stat / FRAME_SIZE:0.0f} seconds.",
            "ProtectRoom": lambda stat: f"Shields the current room from all attacks and abilities for {stat / FRAME_SIZE:0.0f} seconds. The affected room cannot be activated for the duration of the ability.",
            "Bloodlust": lambda stat: f"Doubles combat speed for {stat / FRAME_SIZE:0.0f} seconds.",
            "PoisonRoom": lambda stat: f"Inflicts a lingering cloud of poison on the room that will in turn inflict a poisoned state on passing crews over time for {stat / FRAME_SIZE:0.0f} seconds. Poison damage dealt is proportional to the remaining poison duration on the poisoned crew.",
            "RemoveDebuffsFromSameRoomCharacters": lambda stat: f"Reduces the duration of all negative status effects by {stat / FRAME_SIZE:0.0f} seconds on all friendly crews in the current room.",
            "SelfDestruct": lambda stat: f"Instantly reduces current hp to 0 and immediately deals {stat:0.0f} damage to all enemy crews in the current room.",
            "XmasExplosion": lambda stat: f"Drops a special gift for your enemies, which will explode after a 0.5 seconds delay, dealing {stat:0.0f} damage to all enemy crews in the current room.",
        }

        ability_stat_formatted = f"{base_enhancement_value:0.0f}"
        if special_ability_name in ability_map:
            return ability_map[special_ability_name](float(ability_stat_formatted))

        return "Ability description not available."

    @staticmethod
    def handle_cast_assigned_ability_skill(base_chance: int, base_enhancement_value: int) -> str:
        """Handle CastAssignedAbilitySkill ability."""
        ability_power = SHORT_ENHANCE_MAP["Ability"]
        if base_enhancement_value > 0:
            return f"{base_chance}% chance to activate assigned special ability with {base_enhancement_value} {ability_power} power."

        return f"{base_chance}% chance to activate assigned special ability skill using current {ability_power} power."

    def handle_gain_item_skill(self, base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle GainItemSkill ability."""
        item_design = self.item_service.items[argument]
        item_name = item_design["name"]
        enhancement_type_short = item_design["short_disp_enhancement"]
        return f"{base_chance}% chance to gain a {item_name} with +{base_enhancement_value}{enhancement_type_short}."

    @staticmethod
    def handle_move_speed_boost(base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle MoveSpeedBoost ability."""
        if argument == 1:
            return f"{base_chance}% chance to gain {base_enhancement_value} walk speed."

        if argument == 2:
            return f"{base_chance}% chance to gain {base_enhancement_value} run speed."

        return f"{base_chance}% chance to gain {base_enhancement_value} to both walk and run speed."

    @staticmethod
    def handle_prevent_status_skill(base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle PreventStatusSkill ability."""
        if argument == 1:
            return f"{base_chance}% chance to prevent {base_enhancement_value} negative status effects."

        return f"{base_chance}% chance to gain ability to block negative status effects from being inflicted {base_enhancement_value} times."

    def handle_spawn_crew_skill(self, base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle SpawnCrewSkill ability."""
        character_design = self.character_service.characters[argument]
        character_name = character_design["name"]
        return f"{base_chance}% chance to spawn a Lv.{base_enhancement_value} {character_name} in the current room if a slot is available."

    def handle_spawn_module_skill(self, base_chance: int, argument: int) -> str:
        """Handle SpawnModuleSkill ability."""
        item_design = self.item_service.items[argument]  # Assume item_service is a service for item information
        module_name = item_design["name"]
        return f"{base_chance}% chance to spawn a {module_name} in the current room if a slot is available."

    @staticmethod
    def handle_reduce_crew_status_skill(base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle ReduceCrewStatusSkill ability."""
        duration_seconds = base_enhancement_value / FRAME_SIZE
        if argument == 1:
            return f"{base_chance}% chance to reduce any freeze status duration on the crew by {duration_seconds:.1f} seconds."

        return f"{base_chance}% chance to reduce all negative status effects' duration on the crew by {duration_seconds:.1f} seconds."

    @staticmethod
    def handle_reduce_room_status_skill(base_chance: int, base_enhancement_value: int, argument: int) -> str:
        """Handle ReduceRoomStatusSkill ability."""
        duration_seconds = base_enhancement_value / FRAME_SIZE
        if argument == 1:
            return f"{base_chance}% chance to reduce any fire status duration on the current room by {duration_seconds:.1f} seconds."

        if argument == 2:
            return f"{base_chance}% chance to reduce any EMP status duration on the current room by {duration_seconds:.1f} seconds."

        return f"{base_chance}% chance to reduce all negative status effects' duration on the current room by {duration_seconds:.1f} seconds."

    def update_collections(self) -> None:
        """Get collections from API and save them in database."""
        collections = self.pixel_starships_api.get_collections()
        still_presents_ids = []

        for collection in collections:
            record_id = int(collection["CollectionDesignId"])
            self.record_service.add_record(
                TypeEnum.COLLECTION,
                record_id,
                collection["CollectionName"],
                int(collection["SpriteId"]),
                collection["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.COLLECTION, still_presents_ids)
