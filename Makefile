.PHONY: install test lint clean run docker-build docker-run

# Variables
PYTHON = python3
PIP = pip3
PYTEST = pytest
FLAKE8 = flake8
MYPY = mypy

# Installation
install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements.txt -r requirements-dev.txt

# Testing
test:
	$(PYTEST) tests/

test-unit:
	$(PYTEST) tests/unit/

test-integration:
	$(PYTEST) tests/integration/

test-coverage:
	$(PYTEST) --cov=src tests/

# Linting and Type Checking
lint:
	$(FLAKE8) src/ tests/
	$(MYPY) src/ tests/

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.pyc" -exec rm -r {} +
	find . -type d -name "*.pyo" -exec rm -r {} +
	find . -type d -name "*.pyd" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type d -name "build" -exec rm -r {} +
	find . -type d -name "dist" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

# Running
run-web:
	$(PYTHON) -m src.web.backend.app

run-telegram:
	$(PYTHON) -m src.connectors.telegram.bot

run-threads:
	$(PYTHON) -m src.connectors.threads.bot

# Docker
docker-build:
	docker build -t langchain-agent .

docker-run:
	docker run -p 8000:8000 langchain-agent

# Development Tools
format:
	black src/ tests/
	isort src/ tests/

# Documentation
docs:
	mkdocs build

serve-docs:
	mkdocs serve

# Help
help:
	@echo "Available commands:"
	@echo "  make install         - Install dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make lint           - Run linters and type checkers"
	@echo "  make clean          - Clean up build and cache files"
	@echo "  make run-web        - Run web interface"
	@echo "  make run-telegram   - Run Telegram bot"
	@echo "  make run-threads    - Run Threads bot"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make format         - Format code"
	@echo "  make docs           - Build documentation"
	@echo "  make serve-docs     - Serve documentation locally" 