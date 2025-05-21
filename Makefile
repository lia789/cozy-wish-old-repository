.DEFAULT_GOAL := help

.PHONY: help full-reset-db accounts-app-db-import venues-app-db-import run-dev run-test run-staging run-prod setup-env setup-dev-environment test lint format makemigrations migrate shell collectstatic superuser

# Help command
help:
	@echo "Available commands:"
	@echo ""
	@echo "Environment:"
	@echo "  setup-env              - Set up environment variables from .env.example"
	@echo "  run-dev                - Run development server with development settings"
	@echo "  run-test               - Run development server with test settings"
	@echo "  run-staging            - Run development server with staging settings"
	@echo "  run-prod               - Run development server with production settings"
	@echo ""
	@echo "Setup:"
	@echo "  setup-dev-environment  - Set up complete development environment"
	@echo "  full-reset-db          - Reset database and migrations"
	@echo "  accounts-app-db-import - Import dummy data for accounts app"
	@echo "  venues-app-db-import   - Import dummy data for venues app"
	@echo ""
	@echo "Development:"
	@echo "  test                   - Run tests"
	@echo "  lint                   - Run linting"
	@echo "  format                 - Run code formatting"
	@echo "  makemigrations         - Create database migrations"
	@echo "  migrate                - Apply database migrations"
	@echo "  shell                  - Start Django shell"
	@echo "  collectstatic          - Collect static files"
	@echo "  superuser              - Create superuser"
	@echo ""

# Environment variables
PYTHON = python
MANAGE = $(PYTHON) manage.py

# Environment settings
run-dev:
	@echo "Running development server..."
	@export DJANGO_ENVIRONMENT=development && $(MANAGE) runserver

run-test:
	@echo "Running with test settings..."
	@export DJANGO_ENVIRONMENT=testing && $(MANAGE) runserver

run-staging:
	@echo "Running with staging settings..."
	@export DJANGO_ENVIRONMENT=staging && $(MANAGE) runserver

run-prod:
	@echo "Running with production settings..."
	@export DJANGO_ENVIRONMENT=production && $(MANAGE) runserver

# Environment setup
setup-env:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env file with your settings"; \
	else \
		echo ".env file already exists"; \
	fi

# Database operations
full-reset-db:
	@echo "Running full database reset..."
	@echo "This will drop the database, delete migrations, and create a new database with a superuser."
	@$(MANAGE) flush --no-input
	@find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	@find . -path "*/migrations/*.pyc" -delete
	@$(MANAGE) makemigrations
	@$(MANAGE) migrate
	@$(MANAGE) create_superuser

# Accounts app data import
accounts-app-db-import:
	@echo "Importing accounts_app dummy data..."
	@$(MANAGE) import_accounts_dummy_data

# Venues app data import
venues-app-db-import:
	@echo "Importing venues_app dummy data..."
	@$(MANAGE) import_venues_dummy_data

# Combined operations
setup-dev-environment: setup-env full-reset-db accounts-app-db-import venues-app-db-import
	@echo "Development environment setup complete!"

# Testing
test:
	@echo "Running tests..."
	@export DJANGO_ENVIRONMENT=testing && $(MANAGE) test

# Linting and formatting
lint:
	@echo "Running linting..."
	@flake8 .

format:
	@echo "Running formatting..."
	@black .
	@isort .

# Migrations
makemigrations:
	@echo "Making migrations..."
	@$(MANAGE) makemigrations

migrate:
	@echo "Running migrations..."
	@$(MANAGE) migrate

# Shell
shell:
	@echo "Starting shell..."
	@$(MANAGE) shell_plus --ipython

# Collect static files
collectstatic:
	@echo "Collecting static files..."
	@$(MANAGE) collectstatic --noinput

# Create superuser
superuser:
	@echo "Creating superuser..."
	@$(MANAGE) createsuperuser