#!/bin/bash

# FRIDAY Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 Starting FRIDAY deployment..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p state/logs
mkdir -p state/uploads
mkdir -p state/outputs/videos
mkdir -p state/outputs/thumbs
mkdir -p state/assets
mkdir -p state/templates
mkdir -p state/exports

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Build frontend (if exists)
if [ -f "package.json" ]; then
    echo "🎨 Building frontend..."
    npm install
    npm run build
fi

# Set permissions
echo "🔐 Setting permissions..."
chmod -R 755 state/

# Health check
echo "🏥 Running health check..."
python -c "
import sys
sys.path.append('.')
from app import app
with app.test_client() as client:
    response = client.get('/health')
    if response.status_code == 200:
        print('✅ Health check passed')
    else:
        print(f'❌ Health check failed: {response.status_code}')
        sys.exit(1)
"

echo "✅ Deployment completed successfully!"
echo "🌐 You can now start the application with:"
echo "   python app.py"
echo "   or"
echo "   gunicorn app:app --bind 0.0.0.0:8000"
