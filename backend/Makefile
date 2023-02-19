.PHONY=assets
assets:
	python importer.py --assets

.PHONY=prestiges
prestiges:
	python importer.py --prestiges

.PHONY=players
players:
	python importer.py --players

.PHONY=market
market:
	python importer.py --market

.PHONY=market-first-item
market-first-item:
	python importer.py --market-first-item

.PHONY=daily-sales
daily-sales:
	python importer.py --daily-sales

.PHONY=market-messages
market-messages:
	python importer.py --market-messages

.PHONY=market-messages-first-item
market-messages-first-item:
	python importer.py --market-messages-first-item

.PHONY=pycodestyle
pycodestyle:
	pycodestyle

.PHONY=test
test:
	python -m pytest

.PHONY=lint
lint:
	flake8 . --count --show-source --statistics
