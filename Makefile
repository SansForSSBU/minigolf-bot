check:
	uv run ruff format --check .
	uv run ruff check .
	uv run ruff check --select TCH

test:
	uv run pytest --cov=src --cov-report=term --cov-report=xml

fix:
	uv run ruff format .
	uv run ruff check --fix
