#!/bin/bash
# UAV Security ML - Startup Script
# Handles: migrations, admin creation, ML model training (first run), server start
set -e

echo "=== UAV Security ML Startup ==="

echo "[1/4] Running database migrations..."
python manage.py migrate --noinput

echo "[2/4] Ensuring admin user exists..."
python manage.py create_admin

echo "[3/4] Checking ML models..."
if [ ! -f ml_models/random_forest.pkl ]; then
    echo "  No trained models found. Generating dataset and training models..."
    echo "  This may take 2-5 minutes on first run..."
    python scripts/generate_dataset.py
    python scripts/train_models.py
    echo "  Models trained successfully!"
else
    echo "  Models already exist, skipping training."
fi

echo "[4/4] Starting Gunicorn..."
exec gunicorn uav_project.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -