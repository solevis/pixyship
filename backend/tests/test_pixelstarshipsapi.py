from unittest.mock import MagicMock

from app.pixelstarshipsapi import PixelStarshipsApi

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
