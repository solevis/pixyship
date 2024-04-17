import logging

from flask import Flask
from flask_cors import CORS

from app.blueprints.api import api_blueprint
from app.blueprints.root import root_blueprint
from app.commands import check_cli, importer_cli, tools_cli
from app.config import DefaultConfig
from app.ext import db, migrate


def init_configuration(app, test_config=None):
    # Load the default configuration
    app.config.from_object(DefaultConfig)

    # Load the configuration from the instance folder
    app.config.from_pyfile("config.cfg", silent=True)

    # Load the configuration from the environment
    app.config.from_prefixed_env()

    if test_config is not None:
        # Load the test configuration if passed in
        app.config.from_mapping(test_config)


def init_headers(app):
    @app.after_request
    def after_request(response):
        """Before sending the request to the client."""

        # Add security headers for API
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        return response


def init_cors(app):
    """Initialize CORS."""

    if app.config["DEV_MODE"]:
        CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    else:
        CORS(
            app,
            supports_credentials=True,
            resources={
                r"/api/*": {
                    "origins": [
                        "https://{}".format(app.config["DOMAIN"]),
                        "http://{}".format(app.config["DOMAIN"]),
                    ]
                }
            },
        )


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Set the logging level
    app.logger.setLevel(logging.INFO)

    # Initialize configurations
    init_configuration(app, test_config)

    # Initialize database
    db.init_app(app)

    # Initialize the database migration
    migrate.init_app(app, db)

    # Initialize default headers
    init_headers(app)

    # Register blueprints
    app.register_blueprint(root_blueprint, url_prefix="/")
    app.register_blueprint(api_blueprint, url_prefix="/api/")

    # Register commands
    app.cli.add_command(check_cli)
    app.cli.add_command(importer_cli)
    app.cli.add_command(tools_cli)

    # Enable CORS
    init_cors(app)

    return app
