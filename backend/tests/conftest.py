import os
from collections.abc import Iterator
from typing import Any

import flask_migrate
import psycopg
import pytest
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner
from flask_sqlalchemy.session import Session
from psycopg import sql
from sqlalchemy.engine import Connection, Engine, make_url

from app import create_app
from app.ext.db import db

# Postgres database used by the `postgres_app` fixture, created and migrated if needed
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql+psycopg://pixyship@localhost:5432/pixyship_test")

# fail instead of skipping Postgres tests when the database is unreachable (CI)
REQUIRE_POSTGRES_TESTS = os.environ.get("REQUIRE_POSTGRES_TESTS") == "1"


def make_test_app(database_url: str) -> Flask:
    """Create an app for tests on the given database."""
    return create_app(
        {
            "TESTING": True,
            "DEV_MODE": True,
            "CACHE_TYPE": "SimpleCache",
            "SQLALCHEMY_DATABASE_URI": database_url,
        },
    )


@pytest.fixture
def app() -> Flask:
    """Create and configure a new app instance for each test, on an in-memory SQLite database."""
    app = make_test_app("sqlite:///:memory:")

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


@pytest.fixture(scope="session")
def postgres_database_url() -> str:
    """Create the Postgres test database if needed and migrate it, once per test session."""
    url = make_url(TEST_DATABASE_URL)
    assert url.database, "TEST_DATABASE_URL must name a database"
    server_url = url.set(drivername="postgresql", database="postgres").render_as_string(hide_password=False)

    try:
        with psycopg.connect(server_url, autocommit=True, connect_timeout=3) as connection:
            exists = connection.execute("SELECT 1 FROM pg_database WHERE datname = %s", (url.database,)).fetchone()
            if not exists:
                connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(url.database)))
    except psycopg.OperationalError as e:
        if REQUIRE_POSTGRES_TESTS:
            raise

        pytest.skip(f"Postgres test database unreachable: {e}")

    with make_test_app(TEST_DATABASE_URL).app_context():
        flask_migrate.upgrade()

    return TEST_DATABASE_URL


class ConnectionSession(Session):
    """Session always using its bind, the connection holding the test transaction."""

    def get_bind(self, *_args: Any, **_kwargs: Any) -> Engine | Connection:  # noqa: ANN401
        """Use the test connection for every query (models and raw SQL)."""
        assert self.bind is not None
        return self.bind


@pytest.fixture
def postgres_app(postgres_database_url: str) -> Iterator[Flask]:
    """App on the Postgres test database, everything done during the test is rolled back.

    Commits of the tested code are turned into savepoints of an outer transaction.
    """
    app = make_test_app(postgres_database_url)

    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        original_session = db.session
        db.session = db._make_scoped_session(  # noqa: SLF001
            {"class_": ConnectionSession, "bind": connection, "join_transaction_mode": "create_savepoint"},
        )

        try:
            yield app
        finally:
            db.session.remove()
            db.session = original_session
            transaction.rollback()
            connection.close()
            db.engine.dispose()
