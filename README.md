# PixyShip

Created by [Sokitume](https://github.com/JThinkable/pixyship)

Forked by [Solevis](https://github.com/solevis/pixyship)

## Requirements

* Python 3.7
* NPM 5.8.0

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
cp config/alembic_dev.ini alembic.ini
${EDITOR} alembic.ini # update sqlalchemy.url, user must be SUPERUSER

cp config/config_template.py config/config.py
${EDITOR} config/config.py # update DSN

# Create database
alembic upgrade head

# Initial data load
python data_load.py --data
python data_load.py --players
```

Run :

```bash
# Serve backend API
python run.py
```

## Deploying remotely

**TODO: I will soon share an Ansible role for deploying Pixyship.**


