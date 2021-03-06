from ps_client import PixelStarshipsApi


def test_login():
    pixel_starships_api = PixelStarshipsApi()

    device_key, device_checksum = pixel_starships_api.generate_device()
    token = pixel_starships_api.get_device_token(device_key, device_checksum)

    assert isinstance(token, str)
    assert len(token) == 36


def test_settings():
    pixel_starships_api = PixelStarshipsApi()

    settings = pixel_starships_api.get_settings()

    assert 'ProductionServer' in settings

#
# TODO: all PSS API calls
#
