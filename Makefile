.PHONY: help install dev test test-cov lint format format-check clean run docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install --no-interaction

dev: ## Install dependencies including dev dependencies
	poetry install --no-interaction --with dev

test: ## Run tests
	poetry run pytest

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=app --cov-report=term-missing --cov-report=html

lint: ## Run linting with ruff
	poetry run ruff check .

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
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker container logs
	docker-compose logs -f

lock: ## Update poetry.lock file
	poetry lock --no-update

update: ## Update dependencies
	poetry update
