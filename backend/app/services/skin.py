from functools import cached_property
from xml.etree import ElementTree

from app.constants import (
    RACES,
)
from app.enums import TypeEnum
from app.ext import cache
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class SkinService(BaseService):
    """Service to manage skins."""

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def skins(self) -> dict[int, dict]:
        """Get skins data."""
        skins = cache.get("skins")
        if skins is None:
            skins = self.get_skins_from_records()
            cache.set("skins", skins)

        return skins

    @cached_property
    def skinsets(self) -> dict[int, dict]:
        """Get skinsets data."""
        skinsets = cache.get("skinsets")
        if skinsets is None:
            skinsets = self.get_skinsets_from_db()
            cache.set("skinsets", skinsets)

        return skinsets

    def update_cache(self) -> None:
        """Load skins in cache."""
        cache.set("skins", self.get_skins_from_records())
        cache.set("skinsets", self.get_skinsets_from_db())

    def get_skins_from_records(self) -> dict[int, dict]:
        """Load skins from database."""
        skin_records = self.record_service.get_records_from_type(TypeEnum.SKIN)
        skins = {}

        # for each skin, find the skinset and add name and description
        for skin_record in skin_records:
            skin = PixelStarshipsApi.parse_skin_node(ElementTree.fromstring(skin_record.data))
            skinset_id = int(skin["SkinSetId"])

            # if skinset is not in the skinsets, skip
            if skinset_id not in self.skinsets:
                continue

            skinset = self.skinsets[skinset_id]
            skin_id = int(skin["SkinId"])
            skins[skin_id] = {
                "id": skin_id,
                "skinset_id": skinset_id,
                "name": skinset["name"],
                "description": skinset["description"],
                "sprite": self.sprite_service.get_sprite_infos(int(skin["SpriteId"])),
                "root_id": int(skin["RootId"]),
                "skin_type": skin["SkinType"],
                "sprite_type": skin["SpriteType"],
                "race_id": int(skin["RaceId"]),
                "race": RACES.get(int(skin["RaceId"]), RACES.get(0)),
            }

        return skins

    def get_skinsets_from_db(self) -> dict[int, dict]:
        """Load skinsets from database."""
        skinset_records = self.record_service.get_records_from_type(TypeEnum.SKINSET)

        skinsets = {}

        # retrieve all skinsets
        for skinset_record in skinset_records:
            skinset = PixelStarshipsApi.parse_skinset_node(ElementTree.fromstring(skinset_record.data))

            skinsets[skinset_record.type_id] = {
                "id": int(skinset["SkinSetId"]),
                "name": skinset["SkinSetName"],
                "description": skinset["SkinSetDescription"],
                "sprite": self.sprite_service.get_sprite_infos(int(skinset["SpriteId"])),
            }

        return skinsets

    def update_skinsets(self) -> None:
        """Update skinsets and save records."""
        pixel_starships_api = PixelStarshipsApi()
        skinsets = pixel_starships_api.get_skinsets()
        still_presents_ids = []

        for skinset in skinsets:
            record_id = int(skinset["SkinSetId"])
            self.record_service.add_record(
                TypeEnum.SKINSET,
                record_id,
                skinset["SkinSetName"],
                int(skinset["SpriteId"]),
                skinset["pixyship_xml_element"],
                pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SKINSET, still_presents_ids)

    def update_skins(self) -> None:
        """Update skins and save records."""
        pixel_starships_api = PixelStarshipsApi()
        skins = pixel_starships_api.get_skins()
        still_presents_ids = []

        for skin in skins:
            record_id = int(skin["SkinId"])
            self.record_service.add_record(
                TypeEnum.SKIN,
                record_id,
                skin["SkinName"],
                int(skin["SpriteId"]),
                skin["pixyship_xml_element"],
                pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SKIN, still_presents_ids)
