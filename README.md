![Python 3.7](https://github.com/solevis/pixyship/actions/workflows/python.yml/badge.svg?branch=main)

# PixyShip

![Pixyship logo](./pixyship.png) 

Created by [Sokitume](https://github.com/JThinkable/pixyship)

Forked by [Solevis](https://github.com/solevis/pixyship)

## Requirements

* Python 3.7
* NodeJS 15.14
* npm 7.7

## Getting Started locally

### Frontend

Install :

```bash
cd frontend/

# Install npm dependencies
npm install

# Build for production/Flask with minification
npm run build
```

Run :

```bash
# Serve with hot reload
npm run dev
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
python importer.py --market-first-item  # retrieve market history for only one item, much faster for dev
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


