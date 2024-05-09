import click
from flask import current_app
from flask.cli import AppGroup, with_appcontext

from app.api_errors import EXPIRED_TOKEN_RESP2
from app.pixelstarshipsapi import PixelStarshipsApi

check_cli = AppGroup("check", help="Check various aspects of the app.")


@check_cli.command("config")
@with_appcontext
def config() -> None:
    """Print the current app's configuration."""
    # current_app.config is a dictionary-like object that holds the configuration for the application.
    # print it line by line
    for key, value in current_app.config.items():
        click.echo(f"{key} = {value}")


@check_cli.command("token")
@with_appcontext
def token() -> None:
    """Check if the token given by Savy has expired."""
    # no need to check if token not defined
    if not current_app.config["SAVY_PUBLIC_API_TOKEN"]:
        return

    # get the top user
    params = {"from": 1, "to": 1}

    # retrieve data as XML from Pixel Starships API
    pss_api = PixelStarshipsApi()
    endpoint = f"https://{pss_api.server}/LadderService/ListUsersByRanking"
    current_app.logger.info("Checking %s...", endpoint)
    response = pss_api.call(endpoint, params=params, need_token=True)

    if response.text == EXPIRED_TOKEN_RESP2:
        current_app.logger.error("Savy Token has expired: %s", response.text)
    else:
        current_app.logger.info("Savy Token is still valid.")
