.PHONY: help build run frontend assets update-browsers

.DEFAULT_GOAL := all

assets:
	python importer.py --assets

prestiges:
	python importer.py --prestiges

players:
	python importer.py --players

market:
	python importer.py --market

market-first-item:
	python importer.py --market-first-item

daily-sales:
	python importer.py --daily-sales

market-messages:
	python importer.py --market-messages

market-messages-first-item:
	python importer.py --market-messages-first-item

pycodestyle:
	pycodestyle

test:
	python -m pytest

lint:
	flake8 . --count --show-source --statistics
