import functools
from collections.abc import Callable

import flask
from flask import current_app


def enforce_source[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Check in production if the referrer is really PixyShip."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
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

    return wrapper
