![Python 3.11](https://github.com/solevis/pixyship/actions/workflows/python311.yml/badge.svg?branch=quart-pssapi-quasar)
![Node.js 18](https://github.com/solevis/pixyship/actions/workflows/nodejs18.yml/badge.svg?branch=quart-pssapi-quasar)
[![CodeQL](https://github.com/solevis/pixyship/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/solevis/pixyship/actions/workflows/codeql-analysis.yml)

# PixyShip

![Pixyship logo](./pixyship.png)

## Requirements

- Python 3.11
- Node.js 18

## Getting Started locally

### Frontend

Install :

```bash
cd frontend/

# Install npm dependencies
yarn install
```

Run :

```bash
# Serve with hot reload
quasar dev
```

Access the web server at [http://localhost:9000](http://localhost:9000).

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
```

Run :

```bash
# Serve backend API
python app.py
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

**TODO**

## Sponsors

<a href="https://jb.gg/OpenSourceSupport">
<img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" width="150">
</a>
