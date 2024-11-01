import pytest

from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    return create_app({"TESTING": True})


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()
