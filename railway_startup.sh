#!/bin/bash
set -e

echo "=== Railway Startup Script ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Environment variables (sanitized):"
env | grep -v "SECRET\|PASSWORD\|KEY" | sort

echo "=== Checking database connection ==="
python -c "
import sys
import os
import time
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

# Get database URL from environment
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print('ERROR: DATABASE_URL environment variable not set')
    sys.exit(1)

# Parse the URL to display info without credentials
parsed = urlparse(db_url)
safe_url = f'{parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}'
print(f'Attempting to connect to database: {safe_url}')

# Try to connect to the database
engine = create_engine(db_url)
max_retries = 5
retry_count = 0

while retry_count < max_retries:
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print('Database connection successful!')
            break
    except Exception as e:
        retry_count += 1
        print(f'Database connection attempt {retry_count} failed: {str(e)}')
        if retry_count < max_retries:
            wait_time = retry_count * 2
            print(f'Retrying in {wait_time} seconds...')
            time.sleep(wait_time)
        else:
            print('All database connection attempts failed.')
            print('Continuing startup anyway...')
"

echo "=== Starting application ==="
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
