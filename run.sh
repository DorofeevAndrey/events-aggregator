#!/bin/bash

set -e

echo "Running migrations..."
alembic upgrade head

echo "Running provider tests..."
pytest -v

echo "Starting API..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000