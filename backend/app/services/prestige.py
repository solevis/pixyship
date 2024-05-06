import datetime
import json
from collections import Counter, defaultdict

from app.enums import TypeEnum
from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.base import BaseService


class PrestigeService(BaseService):
    def __init__(self):
        super().__init__()
        self.pixel_starships_api = PixelStarshipsApi()

    def get_prestige_from_from_api(self, character_id):
        """Get prestige paires and groups created with given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_from(character_id)
        prestiges_from = [
            [int(prestige["CharacterDesignId2"]), int(prestige["ToCharacterDesignId"])] for prestige in prestiges
        ]

        grouped_from = defaultdict(list)
        for response in prestiges_from:
            grouped_from[response[1]].append(response[0])

        return prestiges_from, grouped_from

    def get_prestiges_from_api(self, char_id):
        """Get all prestige combinaisons."""

        prestiges_to, grouped_to = self.get_prestige_to_from_api(char_id)
        prestiges_from, grouped_from = self.get_prestige_from_from_api(char_id)

        all_ids = list(
            set(
                [i for prestige in prestiges_to for i in prestige]
                + [i for prestige in prestiges_from for i in prestige]
                + [char_id],
            ),
        )
        all_characters = [
            self.character_service.characters[i] for i in all_ids if i in self.character_service.characters
        ]

        return {
            "to": grouped_to,
            "from": grouped_from,
            "chars": all_characters,
            "expires_at": datetime.datetime.now() + datetime.timedelta(minutes=1),
        }

    def get_prestige_to_from_api(self, character_id):
        """Get prestige paires and groups which create given char_id."""

        prestiges = self.pixel_starships_api.get_prestiges_character_to(character_id)

        # if only one unique prestige, add it in list
        if not isinstance(prestiges, list):
            prestiges = list((prestiges,))

        prestiges_to = list(
            set(
                tuple(
                    sorted(
                        [
                            int(prestige["CharacterDesignId1"]),
                            int(prestige["CharacterDesignId2"]),
                        ],
                    ),
                )
                for prestige in prestiges
            ),
        )

        # determine which crews to group
        temp_to = prestiges_to
        grouped_to = defaultdict(list)
        while len(temp_to):
            counter = Counter([x for y in temp_to for x in y])
            [(most_id, _)] = counter.most_common(1)

            # find all the pairs with the id
            new_to = []
            for pair in temp_to:
                if most_id == pair[0]:
                    grouped_to[most_id].append(pair[1])
                elif most_id == pair[1]:
                    grouped_to[most_id].append(pair[0])
                else:
                    new_to.append(pair)

            temp_to = new_to

        return prestiges_to, grouped_to

    def update_prestiges(self):
        """Get prestiges from API and save them in database."""

        still_presents_ids = []

        for character in self.character_service.characters.values():
            prestiges = self.get_prestiges_from_api(character["id"])

            # no prestiges, probably special crew or API bug
            if not prestiges["to"] and not prestiges["from"]:
                continue

            json_content = json.dumps(
                {
                    "to": prestiges["to"],
                    "from": prestiges["from"],
                },
                sort_keys=True,
            )

            record_id = int(character["id"])
            self.record_service.add_record(
                TypeEnum.PRESTIGE,
                record_id,
                character["name"],
                int(character["sprite"]["id"]),
                json_content,
                self.pixel_starships_api.server,
                data_as_xml=False,
            )
            still_presents_ids.append(int(record_id))

        self.record_service.purge_old_records(TypeEnum.PRESTIGE, still_presents_ids)
