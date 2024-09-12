# Description: Makefile for the PixyShip's frontend project

# Set default shell
SHELL:=/bin/bash

# Set default environment variables
export NODE_OPTIONS:= --openssl-legacy-provider

.PHONY: build
build:
	@docker compose exec frontend npx update-browserslist-db@latest
	@docker compose exec frontend npm run build

.PHONY: deploy
rsync:
	@rsync -av --delete ./dist/ pixyship:/opt/pixyship.com/uploaded-dist

.PHONY: deploy
deploy: build rsync

.PHONY: rsync-staging
rsync-staging:
	@rsync -av --delete ./dist/ pixyship:/opt/staging.pixyship.com/uploaded-dist

.PHONY: deploy-staging
deploy-staging: build rsync-staging

.PHONY: rsync-beta
rsync-beta:
	@rsync -av --delete ./dist/ pixyship:/opt/beta.pixyship.com/uploaded-dist

.PHONY: deploy-beta
deploy-beta: build rsync-beta

.PHONY: deploy-all
deploy-all: build rsync rsync-staging rsync-beta

.PHONY: update-browsers
update-browsers:
	@docker compose exec frontend npx browserslist@latest --update-db
