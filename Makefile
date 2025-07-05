.PHONY: help setup install run test lint format clean docker-build docker-up docker-down migration migrate

# Default target
help:
	@echo "🚀 Revo Backend - Available commands:"
	@echo "  setup        - Initial project setup"
	@echo "  install      - Install dependencies"
	@echo "  run          - Run the application in development mode"
	@echo "  test         - Run tests"
	@echo "  lint         - Run code linting"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean cache and temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up    - Start services with Docker Compose"
	@echo "  docker-down  - Stop Docker services"
	@echo "  migration    - Create a new database migration"
	@echo "  migrate      - Apply database migrations"

setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install:
	@source venv/bin/activate && pip install -r requirements.txt

run:
	@chmod +x scripts/start.sh
	@./scripts/start.sh

test:
	@source venv/bin/activate && pytest tests/ -v --cov=app --cov-report=html --cov-report=term

lint:
	@source venv/bin/activate && flake8 app tests
	@source venv/bin/activate && mypy --config-file pyproject.toml --strict app

format:
	@source venv/bin/activate && black app tests
	@source venv/bin/activate && isort app tests

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

docker-build:
	@docker build -t revo-backend .

docker-up:
	@docker compose up -d

docker-down:
	@docker-compose down

migration:
	@source venv/bin/activate && alembic revision --autogenerate -m "$(name)"

migrate:
	@source venv/bin/activate && alembic upgrade head 