"""Tests from real PSS API responses, through the records import to the API outputs.

The fixtures (tests/fixtures/pss, one file per endpoint) are real responses of 2026-11-17, trimmed to the daily offers
items (with their recipes and contents), a few rooms, and the sprites, trainings and characters they reference.
"""

from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import urlparse

import pytest
from flask import Flask

from app.pixelstarshipsapi import PixelStarshipsApi
from app.services.character import CharacterService
from app.services.daily_offer import DailyOfferService
from app.services.item import ItemService
from app.services.room import RoomService
from app.services.sprite import SpriteService
from app.services.training import TrainingService

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures" / "pss"


def fixture_call(_api: PixelStarshipsApi, endpoint: str, params: dict, *_args: object, **_kwargs: object) -> MagicMock:
    """Return the fixture of the called endpoint (named Service_Method.xml), whatever the parameters."""
    del params
    name = "_".join(urlparse(endpoint).path.strip("/").split("/")[-2:])
    return MagicMock(text=(FIXTURES_DIRECTORY / f"{name}.xml").read_text(), status_code=200)


@pytest.fixture
def pss_app(postgres_app: Flask) -> Iterator[Flask]:
    """Postgres app with records imported from the fixtures, PSS API calls answered by the fixtures."""
    with postgres_app.test_request_context(), patch.object(PixelStarshipsApi, "call", fixture_call):
        SpriteService().update_sprites()
        TrainingService().update_trainings()
        ItemService().update_items()
        CharacterService().update_characters()
        RoomService().update_rooms()
        yield postgres_app


@pytest.mark.usefixtures("pss_app")
def test_items():
    items = ItemService().items

    turkey = items[343]
    assert turkey["name"] == "Roast Turkey"
    assert turkey["rarity"] == "legendary"
    assert turkey["sprite"] == {"id": 8953, "source": 1391, "x": 260, "y": 103, "width": 36, "height": 28}
    assert turkey["training"]["id"] == 126
    assert turkey["training"]["xp"] == 3200

    # recipe of a recipe: Pilgrim's Pants <- Cosmic Cornucopia <- Cranberry Sauce <- Acorn
    pants = items[994]
    assert pants["short_disp_enhancement"] == "ABL"
    assert [(ingredient["name"], ingredient["count"]) for ingredient in pants["recipe"]] == [
        ("Acorn", 5),
        ("Cosmic Cornucopia", 4),
    ]
    cornucopia = pants["recipe"][1]
    assert [ingredient["id"] for ingredient in cornucopia["recipe"]] == [986, 987, 988, 989, 990, 991]
    assert [(ingredient["name"], ingredient["count"]) for ingredient in cornucopia["recipe"][1]["recipe"]] == [
        ("Acorn", 5),
    ]

    leftovers = items[999]
    assert [(content["type"], content["id"], content["count"]) for content in leftovers["content"]] == [
        ("item", "986", 5),
        ("item", "987", 1),
        ("item", "988", 1),
        ("item", "989", 1),
        ("item", "990", 1),
        ("item", "991", 1),
    ]
    assert leftovers["content"][0]["data"]["name"] == "Acorn"


@pytest.mark.usefixtures("pss_app")
def test_rooms():
    rooms = RoomService().rooms

    gym = rooms[440]
    assert gym["name"] == "Zaki Dragon Gym Lv9"
    assert gym["upgrade_cost"] == 1000000
    assert gym["upgrade_currency"] == "mineral"
    assert gym["purchasable"] is False
    assert gym["requirement"]["id"] == 779
    assert gym["requirement"]["count"] == 1
    assert gym["requirement"]["object"]["name"] == "Zaki Gym Renovation Kit"

    laser = rooms[6]
    assert laser["name"] == "Mineral Mining Laser Lv1"
    assert laser["has_weapon_stats"] is True
    assert laser["system_damage"] == 1.0
    assert laser["purchasable"] is True
    assert laser["shop_type"] == ["Player"]
    assert laser["sprite"]["id"] == 49

    assert rooms[517]["hull_damage"] == 0.3


@pytest.mark.usefixtures("pss_app")
def test_daily_offers():
    daily = DailyOfferService().get_daily_offers_from_api()
    offers = daily["offers"]

    shop = offers["shop"]
    assert shop["object"]["id"] == 343
    assert shop["object"]["object"]["name"] == "Roast Turkey"
    assert shop["cost"] == {"price": "750", "currency": "Starbux"}
    assert shop["details"] == {"left": "102", "max": "9999"}

    assert offers["blueCargo"]["mineralCrew"]["object"]["name"] == "Handsome Michael"
    assert offers["blueCargo"]["starbuxCrew"]["object"]["name"] == "Mama"

    cargo = offers["greenCargo"]["items"]
    assert [(item["object"]["id"], item["cost"]) for item in cargo] == [
        (994, {"currency": "starbux", "price": 200}),
        (992, {"currency": "starbux", "price": 100}),
        (992, {"currency": "starbux", "price": 100}),
    ]

    daily_rewards = offers["dailyRewards"]["objects"]
    assert daily_rewards[0]["object"] == {"price": 3, "currency": "Starbux"}
    assert (daily_rewards[1]["id"], daily_rewards[1]["count"]) == (999, 1)

    # fleet gift sold for real money: SaleRewardString="item:994x[USD/3]"
    sale = offers["sale"]
    assert (sale["object"]["id"], sale["object"]["count"]) == (994, None)
    assert [option["name"] for option in sale["options"]] == ["Clip", "Roll", "Stash", "Case", "Vault"]

    (marker,) = daily["merchant_markers"]
    assert marker["title"] == "Gray Bazaar"
    assert [(item["cost"]["id"], item["cost"]["count"], item["reward"]["id"]) for item in marker["items"]] == [
        (778, 60, 275),
        (741, 12, 153),
        (778, 166, 268),
        (778, 166, 269),
        (778, 200, 793),
        (744, 17, 378),
        (744, 9, 1466),
    ]


@pytest.mark.usefixtures("pss_app")
def test_promotions():
    promotions = {promotion["id"]: promotion for promotion in DailyOfferService().get_promotions_from_api()}

    training_pack = promotions[167]
    assert training_pack["title"] == "Epic Ability"
    assert training_pack["pack"] == 2
    assert [(reward["type"], reward["id"], reward["count"]) for reward in training_pack["rewards"]] == [
        ("starbux", None, 1),
        ("purchasePoints", None, 1),
        ("item", 333, 15),
        ("item", 563, 5),
    ]
