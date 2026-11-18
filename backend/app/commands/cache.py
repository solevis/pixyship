import time

import click
from flask.cli import AppGroup

from app.ext import cache
from app.services.achievement import AchievementService
from app.services.changes import ChangesService
from app.services.character import CharacterService
from app.services.collection import CollectionService
from app.services.craft import CraftService
from app.services.item import ItemService
from app.services.market import MarketService
from app.services.missile import MissileService
from app.services.research import ResearchService
from app.services.room import RoomService
from app.services.ship import ShipService
from app.services.skin import SkinService
from app.services.sprite import SpriteService
from app.services.training import TrainingService

cache_cli = AppGroup("cache", help="Manage the Flask cache.")


# in dependency order: items need sprites, market prices and trainings, etc.
CACHED_SERVICES = (
    ("sprite", SpriteService),
    ("market", MarketService),
    ("training", TrainingService),
    ("item", ItemService),
    ("character", CharacterService),
    ("ship", ShipService),
    ("room", RoomService),
    ("craft", CraftService),
    ("skin", SkinService),
    ("achievement", AchievementService),
    ("collection", CollectionService),
    ("missile", MissileService),
    ("research", ResearchService),
    ("changes", ChangesService),
)


@cache_cli.command("clear")
def clear_cache_command() -> None:
    """Clear the Flask cache."""
    click.echo("Clearing cache...")
    cache.clear()
    click.echo("Cache cleared.")


@cache_cli.command("update")
def update_cache_command() -> None:
    """Update the Flask cache."""
    for name, service_class in CACHED_SERVICES:
        click.echo(f"Updating {name} cache...")
        start = time.time()
        service_class().update_cache()
        duration = time.time() - start
        click.echo(f"{name.capitalize()} cache updated in {duration:.2f}s.")
