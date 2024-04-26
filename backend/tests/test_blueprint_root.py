import pytest
from flask import url_for


def test_api_index_unauthorized(client, app):
    with app.test_request_context():
        response = client.get(url_for("root.api_index"))
    assert response.status_code == 401


def test_api_health_check(client, app):
    with app.test_request_context():
        response = client.get(url_for("root.api_users"))
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


@pytest.mark.parametrize("endpoint", ["/nonexistent", "/invalid"])
def test_api_invalid_endpoints(client, app, endpoint):
    with app.test_request_context():
        response = client.get(endpoint)
    assert response.status_code == 404
