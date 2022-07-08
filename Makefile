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

run:
	@docker compose up

build:
	@docker compose build

all: build run
