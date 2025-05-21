#!/bin/bash

# Set variables
SUPERUSER_EMAIL="pse.coliahabib@gmail.com"
SUPERUSER_PASSWORD="123"
DB_FILE="db.sqlite3"

echo "=== Starting full database reset ==="

# Change to the project root directory
cd "$(dirname "$0")/.." || exit

# Delete the SQLite database file if it exists
echo "=== Removing SQLite database file ==="
if [ -f "$DB_FILE" ]; then
    rm "$DB_FILE"
    echo "Database file removed."
else
    echo "Database file does not exist, nothing to remove."
fi

# Delete all migration files except __init__.py and pycache files
echo "=== Deleting migration files and pycache files ==="
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Make fresh migrations
echo "=== Making fresh migrations ==="
python manage.py makemigrations
python manage.py migrate

# Create superuser
echo "=== Creating superuser ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(email='$SUPERUSER_EMAIL').exists():
    User.objects.create_superuser('$SUPERUSER_EMAIL', '$SUPERUSER_PASSWORD');
    print('Superuser created successfully');
else:
    print('Superuser already exists');
"

echo "=== Database reset completed successfully ==="
