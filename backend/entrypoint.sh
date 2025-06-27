#!/bin/bash
set -e

echo "Applying database migrations..."
python manage.py migrate

# Optional: Create admin user if command exists
if python manage.py createadmin; then
  echo "Admin user created or already exists."
else
  echo "Skipping createadmin command (not defined or errored)."
fi

# Start Gunicorn with increased timeout and multiple workers
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 2 \
    --timeout 120 \
    --log-level info
