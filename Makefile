.PHONY: sync dev test lint format check

sync:
	uv sync

dev:
	uv run fastapi dev

test:
	uv run pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check . --fix

check: lint test
