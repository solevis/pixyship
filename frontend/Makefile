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

.PHONY: build-staging
build-staging:
	@npx update-browserslist-db@latest
	@npm run build-staging

.PHONY: deploy-staging
rsync-staging:
	@rsync -av --delete ./dist/ pixyship:/opt/staging.pixyship.com/uploaded-dist

.PHONY: deploy-staging
deploy-staging: build-staging rsync-staging

.PHONY: build-beta
build-beta:
	@npx update-browserslist-db@latest
	@npm run build-beta

.PHONY: rsync-beta
rsync-beta:
	@rsync -av --delete ./dist/ pixyship:/opt/beta.pixyship.com/uploaded-dist

.PHONY: deploy-beta
deploy-beta: build-beta rsync-beta

.PHONY: deploy-all
deploy-all: deploy deploy-staging deploy-beta

.PHONY: update-browsers
update-browsers:
	@dnpx browserslist@latest --update-db
