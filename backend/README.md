# Backend

## Requirements

- [Python 3.11](https://www.python.org/)
- [PostgreSQL 15](https://www.postgresql.org/)
- [uv](https://docs.astral.sh/uv/)

## Getting Started locally

Install :

```bash
# Initialize environment
uv sync

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

Run :

```bash
uv run flask --debug run
```

Access the backend at [http://localhost:5000](http://localhost:5000).

Linter :

```bash
uv run ruff check
```

Tests :

```bash
uv run pytest
```

## Getting Started locally with Docker

```bash
# Configure database and other settings, see app/config.py for available settings
mkdir -p instance
${EDITOR} instance/config.cfg

# Launch the stack
docker compose up --build

# Initialize the database
docker compose exec  -w /app backend flask db upgrade

# Initial data load
docker compose exec  -w /app backend flask import assets
docker compose exec  -w /app backend flask import players
docker compose exec  -w /app backend flask import market --item 73
```

Access the backend at [http://localhost:8080](http://localhost:8080).
