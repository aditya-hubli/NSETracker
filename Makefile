# ==============================================
# EVENT-DRIVEN DATA PLATFORM - MAKEFILE
# ==============================================
.PHONY: help install install-dev lint format test test-cov clean docker-up docker-down

# Default target
help:
	@echo "Event-Driven Data Platform - Available Commands"
	@echo "================================================"
	@echo "install       Install production dependencies"
	@echo "install-dev   Install development dependencies"
	@echo "lint          Run linter (ruff)"
	@echo "format        Format code (ruff)"
	@echo "test          Run tests"
	@echo "test-cov      Run tests with coverage"
	@echo "clean         Clean build artifacts"
	@echo "docker-up     Start all services"
	@echo "docker-down   Stop all services"
	@echo "schema        Apply database schema to Supabase"

# ==============================================
# INSTALLATION
# ==============================================
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pre-commit install

# ==============================================
# CODE QUALITY
# ==============================================
lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

type-check:
	mypy services/ shared/

# ==============================================
# TESTING
# ==============================================
test:
	pytest

test-cov:
	pytest --cov=services --cov=shared --cov-report=html --cov-report=xml --cov-report=term-missing

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

# ==============================================
# DOCKER
# ==============================================
docker-up:
	docker-compose -f infra/docker-compose.yml up -d

docker-down:
	docker-compose -f infra/docker-compose.yml down

docker-logs:
	docker-compose -f infra/docker-compose.yml logs -f

docker-build:
	docker-compose -f infra/docker-compose.yml build

# ==============================================
# DATABASE
# ==============================================
schema:
	@echo "Apply schema to Supabase using SQL Editor"
	@echo "Copy infra/supabase/schema.sql and run in Supabase SQL Editor"

seed:
	@echo "Apply seed data to Supabase using SQL Editor"
	@echo "Copy infra/supabase/seed.sql and run in Supabase SQL Editor"

# ==============================================
# SERVICES (Local Development)
# ==============================================
run-user-service:
	cd services/user-service && uvicorn main:app --reload --port 8001

run-order-service:
	cd services/order-service && uvicorn main:app --reload --port 8002

run-payment-service:
	cd services/payment-service && uvicorn main:app --reload --port 8003

run-analytics-api:
	cd services/analytics-api && uvicorn main:app --reload --port 8000

run-stream-processor:
	cd services/stream-processor && python processor.py

run-dashboard:
	cd services/dashboard && npm run dev

# ==============================================
# CLEANUP
# ==============================================
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true

# ==============================================
# CI/CD HELPERS
# ==============================================
ci-lint:
	ruff check . --output-format=github
	ruff format --check .

ci-test:
	pytest --cov=services --cov=shared --cov-report=xml --junitxml=test-results.xml
