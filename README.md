![Python 3.7](https://github.com/solevis/pixyship/actions/workflows/python.yml/badge.svg?branch=main) 
![Node.js 15.x](https://github.com/solevis/pixyship/actions/workflows/nodejs.yml/badge.svg?branch=main)
[![CodeQL](https://github.com/solevis/pixyship/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/solevis/pixyship/actions/workflows/codeql-analysis.yml)

# PixyShip

![Pixyship logo](./pixyship.png) 

Created by [Sokitume](https://github.com/JThinkable/pixyship)

Forked by [Solevis](https://github.com/solevis/pixyship)

## Requirements

* Python 3.7
* Node.js 15
* npm 7.7

## Getting Started locally with Docker

```bash
# Configure database connection
cp alembic.ini.dist alembic.ini
${EDITOR} alembic.ini

cp config.py.dist config.py
${EDITOR} config.py

# Launch the stack
docker-compose up --build

# Initialize the database
docker-compose exec  -w /app pixyship-backend alembic upgrade head

# Initial data load
docker-compose exec  -w /app pixyship-backend python importer.py --assets
docker-compose exec  -w /app pixyship-backend python importer.py --players
docker-compose exec  -w /app pixyship-backend python importer.py --market-one-item 73

# PEP-8 linter
docker-compose exec  -w /app pixyship-backend pycodestyle

# Units tests
docker-compose exec  -w /app pixyship-backend python -m pytest

# Build frontend for deployment
docker-compose exec  -w /app pixyship-frontend npm run build
```

Access the local PixyShip at [http://localhost:8080](http://localhost:8080).

## Getting Started locally

### Frontend

Install :

```bash
cd frontend/

# Configure frontend (defaults options should work)
${EDITOR} .env.development

# Install npm dependencies
npm install

# Build with minification
npm run build
```

Run :

```bash
# Serve with hot reload
npm run serve
```

Access the web server at [http://localhost:8080](http://localhost:8080).

### Backend

Install :

```bash
cd backend/

# Create virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install wheel # not mandatory, but easier for installing modules
pip install -r requirements.txt

# Configure database
cp alembic.ini.dist alembic.ini
${EDITOR} alembic.ini # update sqlalchemy.url, user must be SUPERUSER

cp config.py.dist config.py
${EDITOR} config.py # update DSN

# Create database
alembic upgrade head

# Initial data load
python importer.py --assets
python importer.py --players

python importer.py --market  # very long, several hours
python importer.py --market-one-item 73  # retrieve market history for only one item, much faster for dev
```

Run :

```bash
# Serve backend API
python run.py
```

PEP-8 linter :

```bash
pycodestyle
```

Unit test :

```bash
python -m pytest
```

## Deploying remotely

**TODO: I will soon share an Ansible role for deploying Pixyship.**

## Sponsors

<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" width="150">
