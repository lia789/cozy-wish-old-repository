#!/bin/bash

# Set variables
SUPERUSER_EMAIL="pse.coliahabib@gmail.com"
SUPERUSER_PASSWORD="123"
DB_FILE="db.sqlite3"

echo "=== Starting database reset (keeping structure) ==="

# Change to the project root directory
cd "$(dirname "$0")/.." || exit

# Flush the database (keeps structure but removes all data)
echo "=== Flushing all data from the database ==="
python manage.py flush --no-input

# Create superuser if it doesn't exist
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
