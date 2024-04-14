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

# Configure database
cp alembic.ini.dist alembic.ini
${EDITOR} alembic.ini # update sqlalchemy.url, user must be SUPERUSER

cp config.py.dist config.py
${EDITOR} config.py # update DATABASE_URI

# Create database
rye run alembic upgrade head

# Initial data load
rye run python importer.py --assets
rye run python importer.py --players
rye run python importer.py --market  # very long, several hours
rye run python importer.py --market-one-item 73  # retrieve market history for only one item, much faster for dev
```

Run :

```bash
# Serve backend API
rye run python run.py
```

Access the backend at [http://localhost:8080](http://localhost:8080).

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
# Configure database connection
cp alembic.ini.dist alembic.ini
${EDITOR} alembic.ini

cp config.py.dist config.py
${EDITOR} config.py

# Launch the stack
docker compose up --build

# Initialize the database
docker compose exec  -w /app pixyship-backend alembic upgrade head

# Initial data load
docker compose exec  -w /app pixyship-backend python importer.py --assets
docker compose exec  -w /app pixyship-backend python importer.py --players
docker compose exec  -w /app pixyship-backend python importer.py --market-one-item 73
```

Access the backend at [http://localhost:8080](http://localhost:8080).
