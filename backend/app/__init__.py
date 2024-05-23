import logging

from flask import Flask, Response
from flask_cors import CORS

from app.blueprints.api import api_blueprint
from app.blueprints.root import root_blueprint
from app.commands import cache_cli, check_cli, importer_cli
from app.config import DefaultConfig
from app.ext import cache, db, migrate


def init_configuration(app: Flask, test_config: dict | None = None) -> None:
    """Initialize the configuration."""
    # Load the default configuration
    app.config.from_object(DefaultConfig)

    # Load the configuration from the instance folder
    app.config.from_pyfile("config.cfg", silent=True)

    # Load the configuration from the environment
    app.config.from_prefixed_env()

    if test_config is not None:
        # Load the test configuration if passed in
        app.config.from_mapping(test_config)


def init_headers(app: Flask) -> None:
    """Initialize default headers."""

    @app.after_request
    def after_request(response: Response) -> Response:
        """Before sending the request to the client."""
        # Add security headers for API
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

        # Default cache control (only in production)
        if not app.config["DEV_MODE"]:
            response.cache_control.max_age = 300

        return response


def init_cors(app: Flask) -> None:
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
                    ],
                },
            },
        )


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure an instance of the Flask application."""
    # Create the Flask application
    app = Flask(__name__, instance_relative_config=True)

    # Initialize configurations
    init_configuration(app, test_config)

    # Set the logging level
    if app.config["DEV_MODE"]:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    if app.config["ENALBE_PROFILER"]:
        from werkzeug.middleware.profiler import ProfilerMiddleware

        app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

    # Initialize Sentry if DSN is provided, only in production
    if app.config["SENTRY_DSN"] and not app.config["DEV_MODE"]:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    # Initialize database
    db.init_app(app)

    # Initialize the database migration
    migrate.init_app(app, db)

    # Initialize the cache
    cache.init_app(app)

    # Initialize default headers
    init_headers(app)

    # Register blueprints
    app.register_blueprint(root_blueprint, url_prefix="/")
    app.register_blueprint(api_blueprint, url_prefix="/api/")

    # Register commands
    app.cli.add_command(check_cli)
    app.cli.add_command(importer_cli)
    app.cli.add_command(cache_cli)

    # Enable CORS
    init_cors(app)

    return app
