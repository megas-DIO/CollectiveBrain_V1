# Makefile for CollectiveBrain

.PHONY: help install install-dev test test-cov run run-api clean docker-build docker-up docker-down lint format

help:
	@echo "CollectiveBrain - Available Commands"
	@echo "===================================="
	@echo "install          - Install dependencies"
	@echo "install-dev      - Install dev dependencies"
	@echo "test             - Run test suite"
	@echo "test-cov         - Run tests with coverage"
	@echo "run              - Run main application"
	@echo "run-api          - Run API server"
	@echo "run-example      - Run basic usage example"
	@echo "lint             - Run linters"
	@echo "format           - Format code with black"
	@echo "docker-build     - Build Docker image"
	@echo "docker-up        - Start Docker Compose stack"
	@echo "docker-down      - Stop Docker Compose stack"
	@echo "clean            - Clean generated files"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy isort

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

run:
	python collective_brain.py

run-api:
	python api.py

run-example:
	python examples/basic_usage.py

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black *.py tests/ examples/
	isort *.py tests/ examples/

docker-build:
	docker build -t collective-brain:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f collective-brain

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf build dist
