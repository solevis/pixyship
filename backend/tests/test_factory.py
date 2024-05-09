from app import create_app


def test_testing():
    """Test create_app without passing test config."""
    assert create_app({"TESTING": True}).testing


def test_health(client):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.data == b'{"status":"ok"}\n'


def test_config(app):
    """Test the app's configuration."""
    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert "DEV_MODE" in app.config
    assert "DOMAIN" in app.config
    assert "SECRET_KEY" in app.config
    assert "SPRITES_DIRECTORY" in app.config
    assert "CHANGES_MAX_ASSETS" in app.config
    assert "FORCED_PIXELSTARSHIPS_API_URL" in app.config
    assert "USE_STAGING_API" in app.config
    assert "SAVY_PUBLIC_API_TOKEN" in app.config
    assert "DEVICE_LOGIN_CHECKSUM_KEY" in app.config
