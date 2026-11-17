from unittest.mock import MagicMock, patch
from xml.etree.ElementTree import ParseError

import pytest

from app.services.player import PlayerService


@pytest.mark.parametrize("error", [ValueError("Missing required Ship or User element"), ParseError("bad xml")])
def test_get_ship_data_returns_none_on_invalid_ship_details(app, error):
    api = MagicMock()
    api.ship_details.side_effect = error
    service = PlayerService()
    service.pixel_starships_api = api

    with app.app_context(), patch.object(PlayerService, "find_user_id", return_value=42):
        assert service.get_ship_data("Someone") is None
