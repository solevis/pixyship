from xml.etree.ElementTree import Element

from app.enums import TypeEnum
from app.ext.db import db
from app.models import Record
from app.services.record import RecordService


def current_records() -> dict[int, Record]:
    return {record.type_id: record for record in Record.query.filter_by(type=TypeEnum.ITEM, current=True)}


def item(name: str, price: str = "10") -> Element:
    return Element("ItemDesign", {"ItemDesignName": name, "MarketPrice": price})


def import_items(items: dict[int, Element]) -> None:
    service = RecordService()
    for type_id, element in items.items():
        service.add_record(
            TypeEnum.ITEM, type_id, element.get("ItemDesignName", ""), 5, element, "api", ["MarketPrice"]
        )
    service.purge_old_records(TypeEnum.ITEM, list(items))


def test_records_lifecycle(app):
    with app.app_context():
        import_items({1: item("Gun"), 2: item("Shield")})
        assert {type_id: record.name for type_id, record in current_records().items()} == {1: "Gun", 2: "Shield"}
        assert current_records()[1].sprite_id == 5

        # unchanged hash (only an ignored field changed): same record, data updated
        first_id = current_records()[1].id
        import_items({1: item("Gun", price="99"), 2: item("Shield")})
        assert current_records()[1].id == first_id
        assert 'MarketPrice="99"' in current_records()[1].data

        # changed hash: new current record, old one kept as not current
        import_items({1: item("Big Gun"), 2: item("Shield")})
        assert current_records()[1].name == "Big Gun"
        assert Record.query.filter_by(type=TypeEnum.ITEM, type_id=1).count() == 2

        # no more in API: not current anymore
        import_items({1: item("Big Gun")})
        assert list(current_records()) == [1]


def test_purge_old_records_ignores_empty_api_response(app):
    with app.app_context():
        import_items({1: item("Gun")})
        import_items({})

        assert list(current_records()) == [1]
        db.session.rollback()
