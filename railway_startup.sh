#!/bin/bash
set -e

echo "=== Railway Startup Script ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables (sanitized):"
env | grep -v "SECRET\|PASSWORD\|KEY" | sort

echo "=== Skipping database connection check ==="
echo "Database connection check will be performed by the application if needed."

echo "=== Starting application ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
