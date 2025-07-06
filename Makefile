.PHONY: help format lint type-check check install-dev install-pre-commit

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-dev:  ## Install development dependencies
	uv sync --all-extras --dev

install-pre-commit:  ## Install pre-commit hooks
	uv run pre-commit install

format:  ## Format code with black
	uv run black src tests

lint:  ## Run ruff linter
	uv run ruff check src tests

lint-fix:  ## Run ruff linter and auto-fix issues
	uv run ruff check --fix src tests

check: format lint  ## Run all checks (format, lint)

test:  ## Run tests
	uv run pytest tests

test-cov:  ## Run tests with coverage
	uv run pytest tests --cov=src --cov-report=html --cov-report=term-missing 