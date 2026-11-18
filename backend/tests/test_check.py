from flask import Flask

from app.commands.check import mask_config_value


def test_mask_config_value():
    assert mask_config_value("SAVY_PUBLIC_API_TOKEN", "abc") == "***"
    assert mask_config_value("DEVICE_LOGIN_CHECKSUM_KEY", "abc") == "***"
    assert mask_config_value("SENTRY_DSN", "https://key@sentry.example/1") == "***"
    assert mask_config_value("SENTRY_DSN", None) is None
    assert (
        mask_config_value("SQLALCHEMY_DATABASE_URI", "postgresql://user:pass@host/db")
        == "postgresql://user:***@host/db"
    )
    assert mask_config_value("SQLALCHEMY_DATABASE_URI", "postgresql://user@host/db") == "postgresql://user@host/db"
    assert mask_config_value("CACHE_REDIS_URL", "redis://:pass@host:6379/1") == "redis://:***@host:6379/1"
    assert mask_config_value("DOMAIN", "pixyship.example") == "pixyship.example"


def test_check_config_command_masks_secrets(app: Flask):
    app.config["SAVY_PUBLIC_API_TOKEN"] = "very-secret-token"
    result = app.test_cli_runner().invoke(args=["check", "config"])

    assert "SAVY_PUBLIC_API_TOKEN = ***" in result.output
    assert "very-secret-token" not in result.output
