#!/bin/bash
set -e

echo "🚀 Running FRIDAY Starter post-start tasks..."

# Kill any leftover server
pkill -9 -f "python app.py" || true

# Start the app in the background on port 5000
export ADMIN_PASSWORD=admin
export PORT=5000
python app.py > state/logs/server.log 2>&1 &
sleep 5

# Run smoke test
BASE_URL=http://127.0.0.1:5000 ADMIN_PASSWORD=admin python scripts/smoke_test.py || true

echo "✅ Post-start tasks complete. Logs in state/logs/server.log"
