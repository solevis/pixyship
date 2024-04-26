import datetime
from xml.etree.ElementTree import Element

from app.enums import RecordTypeEnum
from app.utils import (
    compute_pvp_ratio,
    float_range,
    format_delta_time,
    get_type_enum_from_string,
    has_offstat,
    int_range,
    parse_assets_string,
    sort_attributes,
)


def test_get_type_enum_from_string_with_known_type(app):
    with app.app_context():
        result = get_type_enum_from_string("room")
        assert result == RecordTypeEnum.ROOM


def test_get_type_enum_from_string_with_allrooms_type(app):
    with app.app_context():
        result = get_type_enum_from_string("allrooms")
        assert result == RecordTypeEnum.ROOM


def test_get_type_enum_from_string_with_unknown_type(app):
    with app.app_context():
        result = get_type_enum_from_string("unknown")
        assert result is None


def test_get_type_enum_from_string_with_empty_string(app):
    with app.app_context():
        result = get_type_enum_from_string("")
        assert result is None


def float_range_handles_empty_values(app):
    with app.app_context():
        result = float_range({}, "start", "end")
        assert result == (0.0, 0.0)


def float_range_handles_non_empty_values(app):
    with app.app_context():
        result = float_range({"start": "1.1", "end": "2.2"}, "start", "end")
        assert result == (1.1, 2.2)


def int_range_handles_empty_values(app):
    with app.app_context():
        result = int_range({}, "start", "end")
        assert result == (0, 0)


def int_range_handles_non_empty_values(app):
    with app.app_context():
        result = int_range({"start": "1", "end": "2"}, "start", "end")
        assert result == (1, 2)


def sort_attributes_preserves_single_attribute(app):
    with app.app_context():
        root = Element("root", {"a": "1"})
        sort_attributes(root)
        assert root.attrib == {"a": "1"}


def sort_attributes_sorts_multiple_attributes(app):
    with app.app_context():
        root = Element("root", {"b": "2", "a": "1"})
        sort_attributes(root)
        assert root.attrib == {"a": "1", "b": "2"}


def sort_attributes_sorts_nested_elements(app):
    with app.app_context():
        root = Element("root", {"b": "2", "a": "1"})
        child = Element("child", {"d": "4", "c": "3"})
        root.append(child)
        sort_attributes(root)
        assert root.attrib == {"a": "1", "b": "2"}
        assert child.attrib == {"c": "3", "d": "4"}


def sort_attributes_handles_empty_attributes(app):
    with app.app_context():
        root = Element("root")
        sort_attributes(root)
        assert root.attrib == {}


def test_parse_assets_string():
    """Test parse_assets_string function."""

    test_cases = [
        "room:233|character:217|item:83x6|starbux:500|purchasePoints:7|item:1467",
        "item:1021",
        "skin:2",
        "points:1|points:2|points:3",
        "gas:10",
        "mineral:1200",
        "1709x1|1708x1|476x1|376x1",
    ]

    for assets_string in test_cases:
        result = parse_assets_string(assets_string)
        assert isinstance(result, list)
        for asset in result:
            assert "type" in asset
            assert "id" in asset
            assert "count" in asset or asset["count"] is None

    result = parse_assets_string(
        test_cases[0]
        + "|"
        + test_cases[1]
        + "|"
        + test_cases[2]
        + "|"
        + test_cases[3]
        + "|"
        + test_cases[4]
        + "|"
        + test_cases[5]
        + "|"
        + test_cases[6]
    )
    assert isinstance(result, list)
    for asset in result:
        assert "type" in asset
        assert "id" in asset
        assert "count" in asset or asset["count"] is None

    assert result[0]["type"] == "room"
    assert result[0]["id"] == 233
    assert result[0]["count"] is None
    assert result[1]["type"] == "character"
    assert result[1]["id"] == 217
    assert result[1]["count"] is None
    assert result[2]["type"] == "item"
    assert result[2]["id"] == 83
    assert result[2]["count"] == 6
    assert result[3]["type"] == "starbux"
    assert result[3]["id"] == 500
    assert result[3]["count"] is None
    assert result[4]["type"] == "purchasePoints"
    assert result[4]["id"] == 7
    assert result[4]["count"] is None
    assert result[5]["type"] == "item"
    assert result[5]["id"] == 1467

    result = parse_assets_string(test_cases[0])
    assert result[0]["type"] == "room"
    assert result[0]["id"] == 233
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[1])
    assert result[0]["type"] == "item"
    assert result[0]["id"] == 1021
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[2])
    assert result[0]["type"] == "skin"
    assert result[0]["id"] == 2
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[3])
    assert result[0]["type"] == "points"
    assert result[0]["id"] == 1
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[4])
    assert result[0]["type"] == "gas"
    assert result[0]["id"] == 10
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[5])
    assert result[0]["type"] == "mineral"
    assert result[0]["id"] == 1200
    assert result[0]["count"] is None

    result = parse_assets_string(test_cases[6])
    assert result[0]["type"] is None
    assert result[0]["id"] == 1709
    assert result[0]["count"] == 1
    assert result[1]["type"] is None


def test_format_delta_time_with_weeks():
    delta_time = datetime.timedelta(weeks=2, days=3, hours=4, minutes=5)
    result = format_delta_time(delta_time)
    assert result == "2w 3d 4h 5m"


def test_format_delta_time_without_minutes():
    delta_time = datetime.timedelta(weeks=2, days=3, hours=4)
    result = format_delta_time(delta_time)
    assert result == "2w 3d 4h"


def test_format_delta_time_without_hours():
    delta_time = datetime.timedelta(weeks=2, days=3)
    result = format_delta_time(delta_time)
    assert result == "2w 3d"


def test_format_delta_time_without_days():
    delta_time = datetime.timedelta(weeks=2)
    result = format_delta_time(delta_time)
    assert result == "2w"


def test_format_delta_time_with_days_only():
    delta_time = datetime.timedelta(days=3)
    result = format_delta_time(delta_time)
    assert result == "3d"


def test_format_delta_time_with_hours_only():
    delta_time = datetime.timedelta(hours=23)
    result = format_delta_time(delta_time)
    assert result == "23h"


def test_format_delta_time_with_minutes_only():
    delta_time = datetime.timedelta(minutes=59)
    result = format_delta_time(delta_time)
    assert result == "59m"


def test_format_delta_time_with_seconds_only():
    delta_time = datetime.timedelta(seconds=59)
    result = format_delta_time(delta_time)
    assert result == ""


def test_format_delta_time_with_zero_time():
    delta_time = datetime.timedelta(0)
    result = format_delta_time(delta_time)
    assert result == ""


def compute_pvp_ratio_returns_zero_for_no_battles(app):
    with app.app_context():
        result = compute_pvp_ratio(0, 0, 0)
        assert result == 0.0


def compute_pvp_ratio_returns_correct_ratio_for_wins_only(app):
    with app.app_context():
        result = compute_pvp_ratio(10, 0, 0)
        assert result == 100.0


def compute_pvp_ratio_returns_correct_ratio_for_draws_only(app):
    with app.app_context():
        result = compute_pvp_ratio(0, 0, 10)
        assert result == 50.0


def compute_pvp_ratio_returns_correct_ratio_for_losses_only(app):
    with app.app_context():
        result = compute_pvp_ratio(0, 10, 0)
        assert result == 0.0


def compute_pvp_ratio_returns_correct_ratio_for_mixed_results(app):
    with app.app_context():
        result = compute_pvp_ratio(5, 3, 2)
        assert result == 60.0


def offstat_returns_false_for_non_equipment(app):
    with app.app_context():
        result = has_offstat("NonEquipment", "Head", 5, 1.0, "Enhancement")
        assert result is False


def offstat_returns_false_for_invalid_slot(app):
    with app.app_context():
        result = has_offstat("Equipment", "InvalidSlot", 5, 1.0, "Enhancement")
        assert result is False


def offstat_returns_false_for_low_rarity(app):
    with app.app_context():
        result = has_offstat("Equipment", "Head", 1, 1.0, "Enhancement")
        assert result is False


def offstat_returns_false_for_no_enhancement_and_no_bonus(app):
    with app.app_context():
        result = has_offstat("Equipment", "Head", 5, 0.0, None)
        assert result is False


def offstat_returns_true_for_valid_input(app):
    with app.app_context():
        result = has_offstat("Equipment", "Head", 5, 1.0, "Enhancement")
        assert result is True
