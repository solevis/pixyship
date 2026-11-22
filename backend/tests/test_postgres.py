"""Tests of Postgres-specific queries, on the Postgres test database (see `postgres_app` fixture)."""

import datetime
import uuid

import pytest
from flask import Flask

from app.enums import TypeEnum
from app.ext.db import db
from app.models import Alliance, Listing, Player, Record
from app.services.changes import ChangesService
from app.services.market import MarketService
from app.services.player import PlayerService


def add_players(*names: str) -> None:
    """Add players with decreasing trophies."""
    db.session.add(Alliance(id=1, name="Alliance", sprite_id=0))
    for index, name in enumerate(names):
        db.session.add(Player(id=index + 1, name=name, trophies=1000 - index, alliance_id=1, last_login_at=None))
    db.session.commit()


@pytest.mark.usefixtures("postgres_app")
def test_rollback_between_tests_first():
    add_players("Solevis")
    assert Player.query.count() == 1


@pytest.mark.usefixtures("postgres_app")
def test_rollback_between_tests_second():
    # the player committed by the previous test was rolled back
    assert Player.query.count() == 0


def test_players_search_is_case_insensitive(postgres_app: Flask):
    add_players("Solevis", "SOLO", "Bob")

    with postgres_app.test_request_context():
        names = [player["name"] for player in PlayerService().get_player_data("sol")]

    assert names == ["Solevis", "SOLO"]


def add_record(record_type: TypeEnum, type_id: int, created_at: datetime.datetime, current: bool = True) -> None:
    """Add a record created at the given date (now() is constant during the test transaction)."""
    data = f'<Sprite SpriteId="{type_id}" ImageFileId="1" X="0" Y="0" Width="1" Height="1" SpriteKey="key" />'
    db.session.add(
        Record(
            type=record_type,
            type_id=type_id,
            current=current,
            md5_hash=uuid.uuid4(),
            data=data if current else "old",
            created_at=created_at,
            url="api",
            name=f"{record_type} {type_id}",
            sprite_id=type_id,
        ),
    )


def test_changes_on_empty_database(postgres_app: Flask):
    """Regression: no records produced an empty SQL condition (AND ()), so /changes returned a 500."""
    with postgres_app.test_request_context():
        assert ChangesService().get_changes_from_db() == []


def test_changes_only_list_new_sprites(postgres_app: Flask):
    """Regression: the sprite condition compared the type to "sprite" instead of "SPRITE", listing changed sprites."""
    first_import = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    later = first_import + datetime.timedelta(days=10)

    add_record(TypeEnum.SPRITE, 1, first_import)
    # changed sprite: old record replaced by a new one
    add_record(TypeEnum.SPRITE, 2, first_import, current=False)
    add_record(TypeEnum.SPRITE, 2, later)
    # new sprite
    add_record(TypeEnum.SPRITE, 3, later)
    # changed ship, listed like any other type
    add_record(TypeEnum.SHIP, 1, first_import)
    add_record(TypeEnum.SHIP, 2, first_import, current=False)
    add_record(TypeEnum.SHIP, 2, later)
    db.session.commit()

    with postgres_app.test_request_context():
        changes = ChangesService().get_changes_from_db()

    assert sorted((change["type"], change["id"], change["change_type"]) for change in changes) == [
        ("ship", 2, "Changed"),
        ("sprite", 3, "New"),
    ]


def test_prices_are_not_truncated(postgres_app: Flask):
    """Regression: price / amount was an integer division, rounding unit prices down."""
    now = datetime.datetime.now(tz=datetime.UTC)
    for listing_id, (price, amount) in enumerate([(10, 3), (10, 4), (9, 2)], start=1):
        db.session.add(
            Listing(
                id=listing_id,
                sale_at=now - datetime.timedelta(hours=1),
                item_name="Item",
                item_id=1,
                amount=amount,
                currency="Starbux",
                price=price,
            ),
        )
    db.session.commit()

    with postgres_app.test_request_context():
        prices = MarketService.get_prices_from_db()[1]["Starbux"]
        history = next(iter(MarketService.get_item_prices(1)["prices"]["Starbux"].values()))

    assert (prices["count"], prices["p25"], prices["p50"], prices["p75"]) == (9, 2.5, 10 / 3, 4.5)
    assert (history["p25"], history["p50"], history["p75"]) == (2.5, 10 / 3, 4.5)
