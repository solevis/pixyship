# Backend

## Requirements

- [devenv](https://devenv.sh/) - Provides Python 3.11, PostgreSQL 15, Redis, and uv

## Getting Started locally

Initialize environment:

```bash
# Enter the devenv shell (starts PostgreSQL and Redis automatically)
devenv shell

# Configure database and other settings, see app/config.py for available settings
mkdir -p instance
${EDITOR} instance/config.cfg

# Create database
uv run flask db upgrade

# Initial data load
uv run flask import assets
uv run flask import players
uv run flask import market  # very long, several hours
uv run flask import market --item 73  # retrieve market history for only one item, much faster for dev
```

Run:

```bash
uv run flask --debug run
```

Access the backend at [http://localhost:5000](http://localhost:5000).

Linter:

```bash
uv run ruff check
```

Tests:

```bash
uv run pytest
```
