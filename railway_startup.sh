#!/bin/bash
set -e

echo "=== Railway Startup Script [$(date)] ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Python path: $(which python)"
echo "Pip version: $(pip --version)"
echo "Installed packages:"
pip list
echo "\n=== Environment variables (sanitized) ==="
env | grep -v "SECRET\|PASSWORD\|KEY" | sort
echo "\n=== File system ==="
echo "Contents of current directory:"
ls -la
echo "\nContents of app directory:"
ls -la app/
echo "\nContents of app/models directory:"
ls -la app/models/

echo "=== Checking database connection ==="
python -c "
import sys
import os
import time
import traceback
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
try:
    print('Creating SQLAlchemy engine...')
    engine = create_engine(db_url, echo=True)
    print('Engine created successfully')
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f'Connection attempt {retry_count + 1}...')
            with engine.connect() as conn:
                print('Connection established, executing query...')
                result = conn.execute(text('SELECT 1'))
                print(f'Query result: {result.fetchall()}')
                print('Database connection successful!')
                break
        except Exception as e:
            retry_count += 1
            print(f'Database connection attempt {retry_count} failed: {str(e)}')
            print('Error details:')
            traceback.print_exc()
            if retry_count < max_retries:
                wait_time = retry_count * 2
                print(f'Retrying in {wait_time} seconds...')
                time.sleep(wait_time)
            else:
                print('All database connection attempts failed.')
                print('Continuing startup anyway...')
                print('This may cause the application to fail if database operations are required.')
except Exception as e:
    print(f'Error creating database engine: {str(e)}')
    print('Error details:')
    traceback.print_exc()
    print('Continuing startup anyway...')
"

echo "=== Starting application [$(date)] ==="
echo "Checking if app/main.py exists:"
if [ -f "app/main.py" ]; then
    echo "app/main.py exists"
    echo "Content of app/main.py:"
    head -n 20 app/main.py
    echo "...(truncated)..."
else
    echo "ERROR: app/main.py does not exist!"
    ls -la app/
fi

echo "Checking if health endpoint is defined:"
grep -n "/health" app/main.py

echo "=== Running app startup test ==="
python test_app_startup.py
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "WARNING: App startup test failed, but continuing anyway..."
fi

echo "Starting uvicorn with debug log level..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --log-level debug
