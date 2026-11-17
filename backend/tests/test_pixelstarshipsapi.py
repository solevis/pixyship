from unittest.mock import MagicMock, patch

from app.pixelstarshipsapi import REQUEST_TIMEOUT, PixelStarshipsApi, get_http_session

SEARCH_USERS_RESPONSE = """<UserService><SearchUsers><Users>
<User Id="1" Name="Bob" />
<User Id="2" Name="It's &quot;me&quot;" />
</Users></SearchUsers></UserService>"""


def make_api() -> PixelStarshipsApi:
    # skip __init__, it fetches the API settings (network call)
    api = PixelStarshipsApi.__new__(PixelStarshipsApi)
    api.server = "api.example"
    api.call = MagicMock(return_value=MagicMock(text=SEARCH_USERS_RESPONSE))
    return api


def test_search_users_exact_match_with_both_quotes_in_name():
    users = make_api().search_users('It\'s "me"', exact_match=True)

    assert [user["Id"] for user in users] == ["2"]


def test_search_users_exact_match_not_found():
    assert make_api().search_users("Bo", exact_match=True) == []


def test_get_response_uses_shared_session_with_timeout():
    session = MagicMock()

    with patch("app.pixelstarshipsapi.get_http_session", return_value=session):
        PixelStarshipsApi.get_response("https://api.example/Endpoint", {"a": 1})

    session.get.assert_called_once_with("https://api.example/Endpoint", params={"a": 1}, timeout=REQUEST_TIMEOUT)


def test_http_session_is_shared_and_retries():
    session = get_http_session()

    assert get_http_session() is session
    assert session.get_adapter("https://api.example").max_retries.total == 3


def test_empty_api_settings_are_not_cached(app):
    api = PixelStarshipsApi.__new__(PixelStarshipsApi)
    api._forced_pixelstarships_api_url = "https://api.example"  # noqa: SLF001
    api._main_pixelstarships_api_url = "https://api.example"  # noqa: SLF001
    settings = {"ProductionServer": "api.example"}

    with app.app_context(), patch.object(PixelStarshipsApi, "fetch_settings", side_effect=[{}, settings]) as fetch:
        assert api.get_api_settings() == {}
        assert api.get_api_settings() == settings
        assert api.get_api_settings() == settings

    assert fetch.call_count == 2
