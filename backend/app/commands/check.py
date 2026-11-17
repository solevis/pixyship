import re

import click
from flask import current_app
from flask.cli import AppGroup

from app.api_errors import EXPIRED_TOKEN_RESP2
from app.pixelstarshipsapi import PixelStarshipsApi

check_cli = AppGroup("check", help="Check various aspects of the app.")

SECRET_KEY_REGEX = re.compile(r"SECRET|TOKEN|KEY|PASSWORD|DSN", re.IGNORECASE)

# password in URLs like postgresql://user:password@host/db
URL_PASSWORD_REGEX = re.compile(r"(?<=://)([^:/@]*):[^@/]+@")


def mask_config_value(key: str, value: object) -> object:
    """Mask secrets (tokens, keys, DSN, passwords in URLs) of a configuration value."""
    if value and SECRET_KEY_REGEX.search(key):
        return "***"

    if isinstance(value, str):
        return URL_PASSWORD_REGEX.sub(r"\1:***@", value)

    return value


@check_cli.command("config")
def config() -> None:
    """Print the current app's configuration, secrets are masked."""
    for key, value in current_app.config.items():
        click.echo(f"{key} = {mask_config_value(key, value)}")


@check_cli.command("token")
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
