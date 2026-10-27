#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate --no-input

# Load initial backup data if fixture exists
if [ -f initial_data.json ]; then
    python manage.py loaddata initial_data.json || true
fi

# Collect static files
python manage.py collectstatic --no-input
