#!/bin/bash

echo "�� Starting Issues Tracker Application..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import time
import psycopg2
from app.core.config import settings
max_retries = 30
for i in range(max_retries):
    try:
        conn = psycopg2.connect(settings.database_url)
        conn.close()
        print('✅ Database connected successfully')
        break
    except Exception as e:
        print(f'⏳ Database not ready, retrying... ({i+1}/{max_retries})')
        time.sleep(2)
        if i == max_retries - 1:
            print('❌ Failed to connect to database')
            exit(1)
"

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

# Create demo users if they don't exist
echo "👤 Setting up demo users..."
python create_demo_users.py || echo "⚠️ Demo users may already exist"

echo "🌟 Starting web server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
