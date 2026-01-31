import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

from app import create_app
from app.ext.db import db


@pytest.fixture
def app() -> Flask:
    """Create and configure a new app instance for each test."""
    app = create_app({"TESTING": True, "CACHE_TYPE": "SimpleCache", "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    # Create all tables for in-memory database
    with app.app_context():
        db.create_all()

    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()
