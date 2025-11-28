.PHONY: help install dev test test-cov lint format format-check clean run docker-build docker-up docker-down docker-logs db-upgrade db-downgrade docker-test

COMPOSE ?= docker compose

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install --no-interaction

dev: ## Install dependencies including dev dependencies
	poetry install --no-interaction --with dev

test: ## Run all tests
	poetry run pytest

test-unit: ## Run unit tests only
	poetry run pytest tests/unit -v

test-integration: ## Run integration tests only
	poetry run pytest tests/integration -v

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=app --cov-report=term-missing --cov-report=html

test-cov-unit: ## Run unit tests with coverage
	poetry run pytest tests/unit --cov=app --cov-report=term-missing

test-cov-integration: ## Run integration tests with coverage
	poetry run pytest tests/integration --cov=app --cov-report=term-missing

db-upgrade: ## Apply alembic migrations (Docker Compose)
	$(COMPOSE) run --rm api poetry run alembic upgrade head

db-downgrade: ## Roll back alembic migrations (Docker Compose, example steps=1)
	$(COMPOSE) run --rm api poetry run alembic downgrade -1

db-upgrade-local: ## Apply alembic migrations locally (no Docker, e.g. for SQLite)
	poetry run alembic upgrade head

db-downgrade-local: ## Roll back alembic migrations locally (no Docker, example steps=1)
	poetry run alembic downgrade -1
docker-test: ## Run tests inside the api container
	$(COMPOSE) run --rm api poetry run pytest

lint: ## Run linting with ruff
	poetry run ruff check .

lint-fix: ## Fix linting issues with ruff
	poetry run ruff check . --fix

format: ## Format code with ruff
	poetry run ruff format .

format-check: ## Check code formatting without modifying files
	poetry run ruff format --check .

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

run: ## Run the FastAPI application
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	$(COMPOSE) build

docker-up: ## Start Docker containers
	$(COMPOSE) up -d

docker-down: ## Stop Docker containers
	$(COMPOSE) down

docker-logs: ## View Docker container logs
	$(COMPOSE) logs -f

lock: ## Update poetry.lock file
	poetry lock --no-update

update: ## Update dependencies
	poetry update
