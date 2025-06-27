#!/bin/bash
set -e

# Run Django database migrations
echo "Applying database migrations..."
python manage.py migrate

# Optional: create admin user if command exists
if python manage.py createadmin; then
  echo "Admin user created or already exists."
else
  echo "Skipping createadmin command (not defined or errored)."
fi

# Start Gunicorn server on Railway's required port (8080)
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080
