import pytest

from app.services.market import MarketService


def test_parse_offstats_no_message():
    assert MarketService.parse_offstats(None) == []
    assert MarketService.parse_offstats("") == []


def test_parse_offstats_without_offstat():
    assert MarketService.parse_offstats("Selling 1 Rocket Pig") == []
    assert MarketService.parse_offstats("Selling 1 Medium Mineral Crate") == []


def test_parse_offstats_ignores_parentheses_in_item_name():
    assert MarketService.parse_offstats("Selling 1 Gold (Au)") == []


def test_parse_offstats_single():
    assert MarketService.parse_offstats("Selling 1 Rocket Pig (+4.4 Pilot)") == [
        {"value": "4.4", "bonus": "Pilot", "short_bonus": "PLT"},
    ]


def test_parse_offstats_multiple():
    assert MarketService.parse_offstats("Selling 1 Ethereal Extendo-Clamp Plus (+12.2 Ability) (+1.5 Engine)") == [
        {"value": "12.2", "bonus": "Ability", "short_bonus": "ABL"},
        {"value": "1.5", "bonus": "Engine", "short_bonus": "ENG"},
    ]


def test_parse_offstats_multi_word_bonus():
    assert MarketService.parse_offstats("Selling 1 Armor (+5.1 Fire Resistance)") == [
        {"value": "5.1", "bonus": "Fire Resistance", "short_bonus": "RST"},
    ]


def test_parse_offstats_comma_decimal_separator():
    assert MarketService.parse_offstats("Selling 1 Thing (+12,5 Ability)") == [
        {"value": "12,5", "bonus": "Ability", "short_bonus": "ABL"},
    ]


def test_parse_offstats_empty_bonus_is_ignored():
    assert MarketService.parse_offstats("Selling 1 Thing (+5 )") == []


def test_parse_offstats_unknown_bonus_keeps_raw_name():
    assert MarketService.parse_offstats("Selling 1 Thing (+2 Unknown)") == [
        {"value": "2", "bonus": "Unknown", "short_bonus": "Unknown"},
    ]


# Real messages captured from the PSS market Pusher channel
@pytest.mark.parametrize(
    "message",
    [
        # listed items without offstat
        "Selling 1 Engi-Exo Boots",
        "Selling 1 Scratchy",
        "Selling 1 Void Particle",
        "Selling 10 Concentrated Growth Supplement",
        "Selling 40 Small Cola",
        "Selling 42 Weak Growth Supplement",
        "Selling 1 Jack O' Lantern Sticker",
        # item names with parentheses (chemical symbols)
        "Selling 1 Scrap Iron (Fe)",
        "Selling 1 Titanium (Ti)",
        # sold items, including seller names with non-ASCII characters
        "Bought 1 Engi-Exo Boots from Marcourios",
        "Bought 1 Repair Kit from Kasteilmanusko",
        "Bought 1 Repair Kit from dinalt",
        "Bought 1 Void Particle from Alternative4Love",
        "Bought 1 Void Particle from RUBILA2006",
        "Bought 3 Void Particle from RIPing PUMA",
        "Bought 5 Espresso Shot from TVOY BATYA",
        "Bought 1 Titanium (Ti) from StarCinder",
        # seller name with Cyrillic "a" letters
        "Bought 1 Titanium (Ti) from G\u0430nj\u0430",
        # seller name with fullwidth "@" and Hangul filler characters
        "Bought 1 Epic Leg Armor from \uff20\u3164LeoFc zzzz",
    ],
)
def test_parse_offstats_real_messages_without_offstat(message):
    assert MarketService.parse_offstats(message) == []


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        (
            "Selling 1 Chopsticlaw (+14.3 Stamina)",
            [{"value": "14.3", "bonus": "Stamina", "short_bonus": "STA"}],
        ),
        (
            "Selling 1 Extendo-Clamp Plus (+8.3 Science)",
            [{"value": "8.3", "bonus": "Science", "short_bonus": "SCI"}],
        ),
        (
            "Selling 1 Raven Swarm (+13.5 Ability)",
            [{"value": "13.5", "bonus": "Ability", "short_bonus": "ABL"}],
        ),
        (
            "Selling 1 Storm Lance (+3.9 Engine)",
            [{"value": "3.9", "bonus": "Engine", "short_bonus": "ENG"}],
        ),
    ],
)
def test_parse_offstats_real_messages_with_offstat(message, expected):
    assert MarketService.parse_offstats(message) == expected


def test_pusher_refresh_prices_cache_is_throttled(app):
    from unittest.mock import patch

    from app.services.market_pusher import PRICES_CACHE_REFRESH_INTERVAL, MarketPusherService

    with (
        app.app_context(),
        patch("app.services.market_pusher.MarketService.update_cache") as update_cache,
        patch("app.services.market_pusher.ItemService.update_cache") as update_items_cache,
    ):
        service = MarketPusherService()

        with patch("app.services.market_pusher.time.monotonic", return_value=1000.0):
            service.refresh_prices_cache()
            service.refresh_prices_cache()
        assert update_cache.call_count == 1
        assert update_items_cache.call_count == 1

        with patch("app.services.market_pusher.time.monotonic", return_value=1000.0 + PRICES_CACHE_REFRESH_INTERVAL):
            service.refresh_prices_cache()
        assert update_cache.call_count == 2
        assert update_items_cache.call_count == 2
