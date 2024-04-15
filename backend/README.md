# Backend

## Requirements

- [Python 3.11](https://www.python.org/)
- [PostgreSQL 15](https://www.postgresql.org/)
- [rye](https://rye-up.com/)

## Getting Started locally

Install :

```bash
# Initialize environment
rye pin 3.11
rye sync

# Configure database and other settings, see app/config.py for available settings
mkdir -p instance
${EDITOR} instance/config.cfg

# Create database
rye run flask db upgrade

# Initial data load
rye run flask import assets
rye run flask import players
rye run flask import market  # very long, several hours
rye run flask import market --item 73  # retrieve market history for only one item, much faster for dev
```

Run :

```bash
rye run flask --debug run
```

Access the backend at [http://localhost:5000](http://localhost:5000).

Linter :

```bash
rye lint
```

Tests :

```bash
rye test
```

## Getting Started locally with Docker

```bash
# Configure database and other settings, see app/config.py for available settings
mkdir -p instance
${EDITOR} instance/config.cfg

# Launch the stack
docker compose up --build

# Initialize the database
docker compose exec  -w /app pixyship-backend flask db upgrade

# Initial data load
docker compose exec  -w /app pixyship-backend flask import assets
docker compose exec  -w /app pixyship-backend flask import players
docker compose exec  -w /app pixyship-backend flask import market --item 73
```

Access the backend at [http://localhost:8080](http://localhost:8080).
