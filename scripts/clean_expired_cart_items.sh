#!/bin/bash

# Script to clean expired cart items
# This can be added to crontab to run periodically

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Go to the project directory (parent of the script directory)
cd "$SCRIPT_DIR/.."

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the management command
python manage.py clean_expired_cart_items

# Deactivate the virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
