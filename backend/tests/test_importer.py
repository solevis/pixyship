from unittest.mock import MagicMock, patch

from app.ext.db import db
from app.models import Alliance, Player

USER = {
    "name": "NewPlayer",
    "trophies": 3000,
    "alliance_id": 7,
    "last_login_at": None,
    "alliance_name": "NewAlliance",
    "alliance_sprite_id": 1,
}


def run_import_players(runner, top_users: dict, alliance_users: dict | None = None):
    player_service = MagicMock()
    player_service.get_top100_users_from_api.return_value = top_users
    player_service.get_top100_alliances_from_api.return_value = {7: {"name": "NewAlliance"}} if alliance_users else {}
    player_service.get_alliance_users_from_api.return_value = alliance_users or {}

    with (
        patch("app.commands.importer.PlayerService", return_value=player_service),
        patch("app.commands.importer.api_sleep"),
    ):
        return runner.invoke(args=["import", "players"])


def add_old_player(app):
    with app.app_context():
        db.session.add(Player(id=1, name="OldPlayer", trophies=1000, alliance_id=None, last_login_at=None))
        db.session.commit()


def test_import_players_replaces_players(app, runner):
    add_old_player(app)

    result = run_import_players(runner, {2: USER}, alliance_users={2: USER})

    assert result.exit_code == 0
    with app.app_context():
        assert [player.name for player in Player.query.all()] == ["NewPlayer"]
        assert [alliance.name for alliance in Alliance.query.all()] == ["NewAlliance"]


def test_import_players_keeps_players_when_api_returns_nothing(app, runner):
    add_old_player(app)

    result = run_import_players(runner, {})

    assert result.exit_code == 0
    with app.app_context():
        assert [player.name for player in Player.query.all()] == ["OldPlayer"]
