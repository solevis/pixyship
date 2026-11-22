from unittest.mock import MagicMock, patch

from app.pixelstarshipsapi import REQUEST_TIMEOUT, PixelStarshipsApi, get_http_session

SEARCH_USERS_RESPONSE = """<UserService><SearchUsers><Users>
<User Id="1" Name="Bob" />
<User Id="2" Name="It's &quot;me&quot;" />
</Users></SearchUsers></UserService>"""


def make_api(response_text: str = SEARCH_USERS_RESPONSE, status_code: int = 200) -> tuple[PixelStarshipsApi, MagicMock]:
    """Create an API client whose calls all return the given response, return it with the call mock."""
    # skip __init__, it fetches the API settings (network call)
    api = PixelStarshipsApi.__new__(PixelStarshipsApi)
    api.server = "api.example"
    call = MagicMock(return_value=MagicMock(text=response_text, status_code=status_code))
    api.call = call
    return api, call


def test_search_users_exact_match_with_both_quotes_in_name():
    users = make_api()[0].search_users('It\'s "me"', exact_match=True)

    assert [user["Id"] for user in users] == ["2"]


def test_search_users_exact_match_not_found():
    assert make_api()[0].search_users("Bo", exact_match=True) == []


def test_search_users_returns_attributes_and_xml_node_without_mutating_it():
    api, call = make_api()
    users = api.search_users("o")

    call.assert_called_once_with(
        "https://api.example/UserService/SearchUsers", params={"searchstring": "o"}, need_token=False
    )
    assert [user["Name"] for user in users] == ["Bob", 'It\'s "me"']
    node = users[0]["pixyship_xml_element"]
    assert node.tag == "User"
    assert "pixyship_xml_element" not in node.attrib


def test_get_entities_without_container():
    api, _ = make_api("<UserService><SearchUsers /></UserService>")

    assert api.search_users("o") == []


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


def test_get_sales_skips_item_on_non_xml_error_pages(app):
    api, call = make_api("<html><body>Bad Gateway</body>", 502)

    with app.app_context(), patch("app.pixelstarshipsapi.api_sleep"):
        assert api.get_sales(73) == []

    assert call.call_count == 3


def test_get_market_messages_returns_nothing_on_non_xml_error_page(app):
    api, _ = make_api("<html><body>Bad Gateway</body>", 502)

    with app.app_context():
        assert api.get_market_messages(73) == []


def test_find_node_in_response():
    assert PixelStarshipsApi.find_node_in_response("not xml", ".//Sales") is None
    assert PixelStarshipsApi.find_node_in_response("<a><Sales /></a>", ".//Sales") is not None


def test_get_device_starts_at_random_device_then_round_robins():
    api, _ = make_api()
    devices = [MagicMock(name=f"device{i}") for i in range(3)]
    api._devices = devices  # noqa: SLF001
    api._device_next_index = None  # noqa: SLF001

    with (
        patch("app.pixelstarshipsapi.random.randrange", return_value=2) as randrange,
        patch("app.pixelstarshipsapi.db") as db,
    ):
        db.session.merge.side_effect = lambda device: device
        picked = [api.get_device() for _ in range(4)]

    randrange.assert_called_once_with(3)
    assert picked == [devices[2], devices[0], devices[1], devices[2]]
