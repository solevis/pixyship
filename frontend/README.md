# Frontend

## Requirements

- [devenv](https://devenv.sh/) (recommended) or [Node.js 16](https://nodejs.org/)
- [just](https://github.com/casey/just) (command runner)

## Getting Started

### Using devenv (Recommended)

```bash
# Enter the development environment
devenv shell

# Configure frontend (defaults options should work)
${EDITOR} .env.development

# Install npm dependencies
just bootstrap

# Serve with hot reload
just serve
```

### Using Node.js directly

```bash
# Configure frontend (defaults options should work)
${EDITOR} .env.development

# Install npm dependencies
npm install

# Serve with hot reload
npm run serve
```

Access frontend at [http://localhost:8080](http://localhost:8080).

## Available Commands

This project uses `just` as a command runner. To see all available commands:

```bash
just --list
```
