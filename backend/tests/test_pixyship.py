from flask import Flask

from app.services.pixyship import PixyShipService


def test_parse_assets_from_string_currencies(app: Flask):
    with app.app_context():
        service = PixyShipService()

        assert service.parse_assets_from_string("starbux:500|gas:10x2|unknown:1|") == [
            {"count": 1, "data": 500, "id": None, "type": "starbux"},
            {"count": 2, "data": 10, "id": None, "type": "gas"},
        ]
        # count of IAP rewards isn't handled yet
        assert service.parse_assets_from_string("starbux:500x[USD/3]") == [
            {"count": None, "data": 500, "id": None, "type": "starbux"},
        ]
