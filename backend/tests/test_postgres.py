"""Tests of Postgres-specific queries, on the Postgres test database (see `postgres_app` fixture)."""

import pytest
from flask import Flask

from app.ext.db import db
from app.models import Alliance, Player
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
