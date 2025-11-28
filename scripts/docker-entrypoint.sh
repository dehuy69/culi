#!/bin/bash
set -e

echo "=========================================="
echo "Culi Backend - Docker Entrypoint"
echo "=========================================="

# Wait for PostgreSQL to be ready using Python
echo "Waiting for PostgreSQL to be ready..."
python3 << EOF
import sys
import time
import psycopg2
import os

max_retries = 30
retry_count = 0
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/culi_db')

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print("PostgreSQL is ready!")
        sys.exit(0)
    except psycopg2.OperationalError:
        retry_count += 1
        if retry_count < max_retries:
            print(f"PostgreSQL is unavailable - sleeping (attempt {retry_count}/{max_retries})")
            time.sleep(1)
        else:
            print("ERROR: Could not connect to PostgreSQL after 30 attempts")
            sys.exit(1)
EOF

# Check if migrations need to be run
echo "Checking database migrations..."

# Get current migration version
CURRENT_VERSION=$(alembic current 2>&1 | grep -oP '^\s*\K[0-9a-f]+' || echo "none")

if [ "$CURRENT_VERSION" = "none" ] || [ -z "$CURRENT_VERSION" ]; then
  echo "No migrations applied. Running initial migration..."
  alembic upgrade head || {
    echo "WARNING: Migration failed. This might be normal if tables already exist."
    echo "Attempting to continue..."
  }
else
  echo "Current migration version: $CURRENT_VERSION"
  echo "Checking for pending migrations..."
  alembic upgrade head || {
    echo "WARNING: Migration upgrade failed. This might be normal if already up to date."
    echo "Attempting to continue..."
  }
fi

echo "Database migrations check completed!"
echo ""

# Start the application
echo "Starting Culi Backend API server..."
exec "$@"

