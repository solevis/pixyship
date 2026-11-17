from flask import Flask

from app import create_app
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


def test_cors_only_allows_https_domain_in_production():
    app = create_app({"TESTING": True, "DEV_MODE": False, "CACHE_TYPE": "SimpleCache", "DOMAIN": "pixyship.example"})
    client = app.test_client()
    referer = {"Referer": "https://pixyship.example/"}

    response = client.get("/api/time", headers={**referer, "Origin": "https://pixyship.example"})
    assert response.headers["Access-Control-Allow-Origin"] == "https://pixyship.example"
    assert "Access-Control-Allow-Credentials" not in response.headers

    response = client.get("/api/time", headers={**referer, "Origin": "http://pixyship.example"})
    assert "Access-Control-Allow-Origin" not in response.headers
