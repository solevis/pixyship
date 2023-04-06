.PHONY: build
build:
	@npx browserslist@latest --update-db
	@npm run build

.PHONY: deploy
deploy:
	@rsync -av --delete ./dist/ pixyship:/opt/pixyship/uploaded-dist

.PHONY: build-staging
build-staging:
	@npx browserslist@latest --update-db
	@npm run build-staging

.PHONY: deploy-staging
deploy-staging:
	@rsync -av --delete ./dist/ pixyship:/opt/staging.pixyship.com/uploaded-dist
