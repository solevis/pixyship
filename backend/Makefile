.PHONY=assets
assets:
	rye run python importer.py --assets

.PHONY=prestiges
prestiges:
	rye run python importer.py --prestiges

.PHONY=players
players:
	rye run python importer.py --players

.PHONY=market
market:
	rye run python importer.py --market

.PHONY=market-first-item
market-first-item:
	rye run python importer.py --market-first-item

.PHONY=daily-sales
daily-sales:
	rye run python importer.py --daily-sales

.PHONY=market-messages
market-messages:
	rye run python importer.py --market-messages

.PHONY=market-messages-first-item
market-messages-first-item:
	rye run python importer.py --market-messages-first-item

.PHONY=format
format:
	rye fmt

.PHONY=test
test:
	rye test

.PHONY=lint
lint:
	rye lint
