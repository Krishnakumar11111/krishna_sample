#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

# Install backend dependencies
pip install -r requirements.txt

# Collect static files from frontend/static to backend/staticfiles
python manage.py collectstatic --no-input
