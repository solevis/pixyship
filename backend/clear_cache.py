from app import create_app
from app.ext import cache


def main() -> None:
    """Clear the Flask cache."""
    app = create_app()

    with app.app_context():
        app.logger.info("Clearing cache...")
        cache.clear()
        app.logger.info("Cache cleared.")


if __name__ == "__main__":
    main()
