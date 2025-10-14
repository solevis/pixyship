import time

import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext

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


@cache_cli.command("clear")
@with_appcontext
def clear_cache_command() -> None:
    """Clear the Flask cache."""
    with current_app.app_context():
        click.echo("Clearing cache...")
        cache.clear()
        click.echo("Cache cleared.")


@cache_cli.command("update")
@with_appcontext
def update_cache_command() -> None:
    """Update the Flask cache."""
    with current_app.app_context():
        click.echo("Updating sprite cache...")
        start = time.time()
        SpriteService().update_cache()
        duration = time.time() - start
        click.echo(f"Sprite cache updated in {duration:.2f}s.")

        click.echo("Updating market cache...")
        start = time.time()
        MarketService().update_cache()
        duration = time.time() - start
        click.echo(f"Market cache updated in {duration:.2f}.")

        click.echo("Updating training cache...")
        start = time.time()
        TrainingService().update_cache()
        duration = time.time() - start
        click.echo(f"Training cache updated {duration:.2f}s.")

        click.echo("Updating item cache...")
        start = time.time()
        ItemService().update_cache()
        duration = time.time() - start
        click.echo(f"Item cache updated {duration:.2f}s.")

        click.echo("Updating character cache...")
        start = time.time()
        CharacterService().update_cache()
        duration = time.time() - start
        click.echo(f"Character cache updated {duration:.2f}s.")

        click.echo("Updating ship cache...")
        start = time.time()
        ShipService().update_cache()
        duration = time.time() - start
        click.echo(f"Ship cache updated {duration:.2f}s.")

        click.echo("Updating room cache...")
        start = time.time()
        RoomService().update_cache()
        duration = time.time() - start
        click.echo(f"Room cache updated {duration:.2f}s.")

        click.echo("Updating craft cache...")
        start = time.time()
        CraftService().update_cache()
        duration = time.time() - start
        click.echo(f"Craft cache updated {duration:.2f}s.")

        click.echo("Updating skin cache...")
        start = time.time()
        SkinService().update_cache()
        duration = time.time() - start
        click.echo(f"Skin cache updated {duration:.2f}s.")

        click.echo("Updating achievement cache...")
        start = time.time()
        AchievementService().update_cache()
        duration = time.time() - start
        click.echo(f"Achievement cache updated {duration:.2f}s.")

        click.echo("Updating collection cache...")
        start = time.time()
        CollectionService().update_cache()
        duration = time.time() - start
        click.echo(f"Collection cache updated {duration:.2f}s.")

        click.echo("Updating missile cache...")
        start = time.time()
        MissileService().update_cache()
        duration = time.time() - start
        click.echo(f"Missile cache updated {duration:.2f}s.")

        click.echo("Updating research cache...")
        start = time.time()
        ResearchService().update_cache()
        duration = time.time() - start
        click.echo(f"Research cache updated {duration:.2f}s.")

        click.echo("Updating changes cache...")
        start = time.time()
        ChangesService().update_cache()
        duration = time.time() - start
        click.echo(f"Changes cache updated {duration:.2f}s.")
