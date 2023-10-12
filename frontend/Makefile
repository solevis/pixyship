.PHONY: build
build:
	@npx update-browserslist-db@latest
	@npm run build

.PHONY: deploy
deploy:
	@rsync -av --delete ./dist/ pixyship:/opt/pixyship.com/uploaded-dist

.PHONY: build-staging
build-staging:
	@npx update-browserslist-db@latest
	@npm run build-staging

.PHONY: deploy-staging
deploy-staging:
	@rsync -av --delete ./dist/ pixyship:/opt/staging.pixyship.com/uploaded-dist

.PHONY: build-beta
build-beta:
	@npx update-browserslist-db@latest
	@npm run build-beta

.PHONY: deploy-beta
deploy-beta:
	@rsync -av --delete ./dist/ pixyship:/opt/beta.pixyship.com/uploaded-dist
