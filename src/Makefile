lint:
	@echo "Lint Project"
	@echo "Usage: make lint"
	ruff check .
	mypy .
	black --check .
	isort --check-only .

fix:
	@echo "Lint and fix Project"
	@echo "Usage: make fix"
	black .
	isort .

test:
	@echo "Run tests for Project"
	@echo "Usage: make test"
	pytest -v
