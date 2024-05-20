# Description: Makefile for the PixyShip's frontend project

# Set default shell
SHELL:=/bin/bash

# Set default environment variables
export NODE_OPTIONS:= --openssl-legacy-provider

.PHONY: build
build:
	@npx update-browserslist-db@latest
	@npm run build

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
deploy-all: deploy rsync-staging rsync-beta

.PHONY: update-browsers
update-browsers:
	@npx browserslist@latest --update-db
