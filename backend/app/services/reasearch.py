from xml.etree import ElementTree

from werkzeug.utils import cached_property

from app.constants import RESEARCH_TYPE_MAP
from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class ResearchService(BaseService):
    """Service to manage researches."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def researches(self) -> dict[int, dict]:
        """Get researches data."""
        researches = cache.get("researches")
        if researches is None:
            researches = self.get_researches_from_records()
            cache.set("researches", researches)

        return researches

    def update_cache(self) -> None:
        """Load researches in cache."""
        cache.set("researches", self.get_researches_from_records())

    def get_researches_from_records(self) -> dict[int, dict]:
        """Load researches from database."""
        records = self.record_service.get_records_from_type(TypeEnum.RESEARCH)

        researches = {}
        for record in records:
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

    def get_researches_and_ship_min_level(self) -> dict:
        """Retrieve research and min ship level of the needed lab."""
        researches = self.researches

        # get lab room and its min ship level
        for research in researches.values():
            lab_name = "Laboratory Lv{}".format(research["lab_level"])
            if lab_name in self.room_service.rooms_by_name:
                room = self.room_service.rooms_by_name[lab_name]
                research["min_ship_level"] = room["min_ship_level"]

        return researches

    def update_researches(self) -> None:
        """Update data and save records."""
        pixel_starships_api = PixelStarshipsApi()
        researches = pixel_starships_api.get_researches()
        still_presents_ids = []

        for research in researches:
            record_id = int(research["ResearchDesignId"])
            self.record_service.add_record(
                TypeEnum.RESEARCH,
                record_id,
                research["ResearchName"],
                int(research["ImageSpriteId"]),
                research["pixyship_xml_element"],
                pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.RESEARCH, still_presents_ids)
