from functools import cached_property
from xml.etree import ElementTree as ET

from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class TrainingService(BaseService):
    """Service to manage trainings."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def trainings(self) -> dict[int, dict]:
        """Get trainings data."""
        trainings = cache.get("trainings")
        if trainings is None:
            trainings = self.get_trainings_from_records()
            cache.set("trainings", trainings)

        return trainings

    def update_cache(self) -> None:
        """Load trainings in cache."""
        cache.set("trainings", self.get_trainings_from_records())

    def get_trainings_from_records(self) -> dict[int, dict]:
        """Load trainings from database."""
        records = self.record_service.records[TypeEnum.TRAINING]

        trainings = {}
        for record in records.values():
            training = PixelStarshipsApi.parse_training_node(ET.fromstring(record.data))

            trainings[record.type_id] = {
                "id": int(training["TrainingDesignId"]),
                "sprite": self.sprite_service.get_sprite_infos(int(training["TrainingSpriteId"])),
                "hp": int(training["HpChance"]),
                "attack": int(training["AttackChance"]),
                "pilot": int(training["PilotChance"]),
                "repair": int(training["RepairChance"]),
                "weapon": int(training["WeaponChance"]),
                "science": int(training["ScienceChance"]),
                "engine": int(training["EngineChance"]),
                "stamina": int(training["StaminaChance"]),
                "ability": int(training["AbilityChance"]),
                "xp": int(training["XpChance"]),
                "fatigue": int(training["Fatigue"]),
                "minimum_guarantee": int(training["MinimumGuarantee"]),
            }

        return trainings

    def update_trainings(self) -> None:
        """Update data and save records."""
        pixel_starships_api = PixelStarshipsApi()
        trainings = pixel_starships_api.get_trainings()
        still_presents_ids = []

        for training in trainings:
            record_id = int(training["TrainingDesignId"])
            self.record_service.add_record(
                TypeEnum.TRAINING,
                record_id,
                training["TrainingName"],
                int(training["TrainingSpriteId"]),
                training["pixyship_xml_element"],
                pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.TRAINING, still_presents_ids)
