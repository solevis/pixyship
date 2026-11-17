from flask import Flask

from app.blueprints.api import api_time


def test_enforce_source_keeps_function_metadata():
    assert api_time.__name__ == "api_time"
    assert api_time.__doc__ == "Return the current time."


def test_enforce_source_checks_referrer_in_production(app: Flask):
    app.config["DEV_MODE"] = False
    app.config["DOMAIN"] = "pixyship.example"
    client = app.test_client()

    assert client.get("/api/time").status_code == 404
    assert client.get("/api/time", headers={"Referer": "https://evil.example/"}).status_code == 404
    assert client.get("/api/time", headers={"Referer": "https://pixyship.example/items"}).status_code == 200
