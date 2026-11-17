from unittest.mock import MagicMock, patch
from xml.etree.ElementTree import ParseError

import pytest

from app.services.player import PlayerService


def make_service() -> PlayerService:
    # skip __init__, it creates a PixelStarshipsApi (network call)
    service = PlayerService.__new__(PlayerService)
    service.pixel_starships_api = MagicMock()
    return service


@pytest.mark.parametrize("error", [ValueError("Missing required Ship or User element"), ParseError("bad xml")])
def test_get_ship_data_returns_none_on_invalid_ship_details(app, error):
    api = MagicMock()
    api.ship_details.side_effect = error
    service = make_service()
    service.pixel_starships_api = api

    with app.app_context(), patch.object(PlayerService, "find_user_id", return_value=42):
        assert service.get_ship_data("Someone") is None
