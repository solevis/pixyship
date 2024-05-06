from xml.etree import ElementTree

from app.constants import (
    RACES,
)
from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class SkinService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()
        self._skins = {}
        self._skinsets = {}

    @property
    def skins(self):
        if not self._skins:
            self._skins = self.get_skins_from_records()
        return self._skins

    @property
    def skinsets(self):
        if not self._skinsets:
            self._skinsets = self.get_skinsets_from_db()
        return self._skinsets

    def get_skins_from_records(self):
        """Load skins from database."""

        skin_records = self.record_service.records[TypeEnum.SKIN]
        skins = {}

        # for each skin, find the skinset and add name and description
        for skin_record in skin_records.values():
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

    def get_skinsets_from_db(self):
        """Load skinsets from database."""

        skinset_records = self.record_service.records[TypeEnum.SKINSET]

        skinsets = {}

        # retrieve all skinsets
        for skinset_record in skinset_records.values():
            skinset = PixelStarshipsApi.parse_skinset_node(ElementTree.fromstring(skinset_record.data))

            skinsets[skinset_record.type_id] = {
                "id": int(skinset["SkinSetId"]),
                "name": skinset["SkinSetName"],
                "description": skinset["SkinSetDescription"],
                "sprite": self.sprite_service.get_sprite_infos(int(skinset["SpriteId"])),
            }

        return skinsets

    def update_skinsets(self):
        """Update skinsets and save records."""

        skinsets = self.pixel_starships_api.get_skinsets()
        still_presents_ids = []

        for skinset in skinsets:
            record_id = int(skinset["SkinSetId"])
            self.record_service.add_record(
                TypeEnum.SKINSET,
                record_id,
                skinset["SkinSetName"],
                int(skinset["SpriteId"]),
                skinset["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SKINSET, still_presents_ids)

    def update_skins(self):
        """Update skins and save records."""

        skins = self.pixel_starships_api.get_skins()
        still_presents_ids = []

        for skin in skins:
            record_id = int(skin["SkinId"])
            self.record_service.add_record(
                TypeEnum.SKIN,
                record_id,
                skin["SkinName"],
                int(skin["SpriteId"]),
                skin["pixyship_xml_element"],
                self.pixel_starships_api.server,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.SKIN, still_presents_ids)
