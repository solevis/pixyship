from collections.abc import Callable
from typing import ParamSpec

import flask
from flask import current_app

P = ParamSpec("P")


def enforce_source(func: Callable) -> Callable:
    """Check in production if the referrer is really PixyShip."""

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Callable:
        # no need to check referrer on DEV
        if current_app.config["DEV_MODE"]:
            return func(*args, **kwargs)

        # no referrer ?
        if not flask.request.referrer:
            flask.abort(404)

        # referrer is PixyShip ?
        if "//{}/".format(current_app.config["DOMAIN"]) not in flask.request.referrer:
            flask.abort(404)

        # everything is ok, continue
        return func(*args, **kwargs)

    # lets flask see the underlying function
    wrapper.__name__ = func.__name__

    return wrapper
