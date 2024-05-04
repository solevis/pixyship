from xml.etree import ElementTree

from app.constants import RESEARCH_TYPE_MAP
from app.enums import RecordTypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class ResearchService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._researches = {}

    @property
    def researches(self):
        if not self._researches:
            self._researches = self.get_researches_from_records()

        return self._researches

    def get_researches_from_records(self):
        """Load researches from database."""

        records = self.record_service.records[RecordTypeEnum.RESEARCH]

        researches = {}
        for record in records.values():
            research = PixelStarshipsApi.parse_research_node(ElementTree.fromstring(record.data))
            researches[record.type_id] = {
                **research,
                "id": record.type_id,
                "name": research["ResearchName"],
                "description": research["ResearchDescription"],
                "gas_cost": int(research["GasCost"]),
                "starbux_cost": int(research["StarbuxCost"]),
                "lab_level": int(research["RequiredLabLevel"]),
                "research_seconds": int(research["ResearchTime"]),
                "logo_sprite": self.sprite_service.get_sprite_infos(research["LogoSpriteId"]),
                "sprite": self.sprite_service.get_sprite_infos(research["ImageSpriteId"]),
                "required_research_id": int(research["RequiredResearchDesignId"]),
                "research_type": RESEARCH_TYPE_MAP.get(research["ResearchDesignType"], research["ResearchDesignType"]),
            }

        for research in researches.values():
            research["required_research_name"] = (
                researches[research["required_research_id"]]["name"] if research["required_research_id"] else ""
            )

        return researches

    def get_researches_and_ship_min_level(self):
        """Retrieve research and min ship level of the needed lab."""

        researches = self.researches

        # get lab room and its min ship level
        for research in researches.values():
            # TODO: don't use the name but the lab level
            lab_name = "Laboratory Lv{}".format(research["lab_level"])
            if lab_name in self.room_service.rooms_by_name:
                room = self.room_service.rooms_by_name[lab_name]
                research["min_ship_level"] = room["min_ship_level"]

        return researches

    def update_researches(self):
        """Update data and save records."""

        researches = self.pixel_starships_api.get_researches()
        still_presents_ids = []

        for research in researches:
            record_id = int(research["ResearchDesignId"])
            self.record_service.add_record(
                RecordTypeEnum.RESEARCH,
                record_id,
                research["ResearchName"],
                int(research["ImageSpriteId"]),
                research["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(RecordTypeEnum.RESEARCH, still_presents_ids)
