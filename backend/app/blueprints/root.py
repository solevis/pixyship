from flask import Blueprint, abort

root_blueprint = Blueprint("root", __name__)


@root_blueprint.route("/")
def api_index() -> None:
    """Root endpoint."""
    abort(401)


@root_blueprint.route("/health")
def api_users() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
