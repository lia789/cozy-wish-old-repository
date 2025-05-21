#!/bin/bash
# Initialize PostgreSQL database for CozyWish project
# This script creates the database and user for the CozyWish project

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Default values if not set in .env
DB_NAME=${DB_NAME:-cozywish_dev}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo "=== PostgreSQL Database Initialization ==="
echo "This script will create the database and user for the CozyWish project."
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL and try again"
    exit 1
fi

# Check if PostgreSQL server is running
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo "Error: PostgreSQL server is not running at $DB_HOST:$DB_PORT"
    echo "Please start the PostgreSQL server and try again"
    exit 1
fi

# Create database if it doesn't exist
echo "Checking if database $DB_NAME exists..."
if psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "Database $DB_NAME already exists"
else
    echo "Creating database $DB_NAME..."
    createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME
    if [ $? -eq 0 ]; then
        echo "Database $DB_NAME created successfully"
    else
        echo "Error: Failed to create database $DB_NAME"
        exit 1
    fi
fi

# Create extensions
echo "Creating PostgreSQL extensions..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS unaccent;"

echo "=== PostgreSQL Database Initialization Complete ==="
echo "You can now run migrations with: python manage.py migrate"
