.PHONY=format
format:
	ruff format

.PHONY=test
test:
	rye test

.PHONY=lint
lint:
	ruff check

.PHONY=docker-build
docker-build:
	docker build -t solevis/pixyship-backend .

.PHONY=docker-run
docker-run:
	docker run -p 8080:8080 solevis/pixyship-backend
