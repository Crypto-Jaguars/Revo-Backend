#!/bin/bash

# Start script for development environment

echo "🚀 Starting Revo Backend..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration"
fi

# Install dependencies if requirements.txt is newer than last install
if [ requirements.txt -nt .last_install ] || [ ! -f .last_install ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    touch .last_install
fi

# Run database migrations (optional - only if database is available)
echo "🗄️  Checking database migrations..."
if alembic upgrade head 2>/dev/null; then
    echo "✅ Database migrations completed"
else
    echo "⚠️  Database not available or no migrations to run. Continuing without migrations..."
fi

# Start the application
echo "🎯 Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 5500 --reload 