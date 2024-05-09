from flask import current_app
from flask.cli import AppGroup, with_appcontext

from app.ext import cache

cache_cli = AppGroup("cache", help="Manage the Flask cache.")


@cache_cli.command("clear")
@with_appcontext
def clear_cache_command() -> None:
    """Clear the Flask cache."""
    with current_app.app_context():
        current_app.logger.info("Clearing cache...")
        cache.clear()
        current_app.logger.info("Cache cleared.")
