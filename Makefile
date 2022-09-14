.PHONY: help build run frontend assets update-browsers

.DEFAULT_GOAL := all

update-browsers:
	@docker compose exec -w /app pixyship-frontend npx browserslist@latest --update-db

npm-build:
	@docker compose exec -w /app pixyship-frontend npm run build

frontend: update-browsers npm-build

assets:
	@docker compose exec -w /app pixyship-backend python importer.py --assets

players:
	@docker compose exec -w /app pixyship-backend python importer.py --players

market:
	@docker compose exec -w /app pixyship-backend python importer.py --market

market-first-item:
	@docker compose exec -w /app pixyship-backend python importer.py --market-first-item

daily-sales:
	@docker compose exec -w /app pixyship-backend python importer.py --daily-sales

market-messages:
	@docker compose exec -w /app pixyship-backend python importer.py --market-messages

market-messages-first-item:
	@docker compose exec -w /app pixyship-backend python importer.py --market-messages-first-item

pycodestyle:
	@docker compose exec -w /app pixyship-backend pycodestyle

pytest:
	@docker compose exec -w /app pixyship-backend python -m pytest

flake8:
	@docker compose exec  -w /app pixyship-backend flake8 . --count --show-source --statistics

run:
	@docker compose up

restart:
	@docker compose restart

stop:
	@docker compose stop

build:
	@docker compose build

all: build run
