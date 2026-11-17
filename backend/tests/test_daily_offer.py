from app.services.daily_offer import DailyOfferService


def make_service() -> DailyOfferService:
    # skip __init__, it creates a PixelStarshipsApi (network call)
    service = DailyOfferService.__new__(DailyOfferService)
    service.__dict__["item_service"] = type("FakeItemService", (), {"items": {73: {"id": 73}, 74: {"id": 74}}})()
    return service


def test_parse_daily_cargo_skips_unparsable_price_and_keeps_alignment(app):
    service = make_service()

    with app.app_context():
        cargo = service.parse_daily_cargo("73x1|74x2", "invalid|starbux:10")

    assert len(cargo) == 1
    assert cargo[0]["object"]["id"] == 74
    assert cargo[0]["cost"] == {"currency": "starbux", "price": 10}


def test_parse_daily_cargo_with_item_price(app):
    service = make_service()

    with app.app_context():
        cargo = service.parse_daily_cargo("73x1", "item:74x3")

    assert cargo[0]["cost"]["price"] == 74
    assert cargo[0]["cost"]["count"] == "3"
    assert cargo[0]["cost"]["object"] == {"id": 74}
