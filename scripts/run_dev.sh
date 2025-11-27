#!/bin/bash
# Development server script

echo "Starting Culi Backend development server..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

