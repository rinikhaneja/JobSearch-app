#!/bin/bash

# NOTE: You do NOT need to clear npm or pip cache at start.
# Only clear cache if you are troubleshooting dependency issues or want a fresh install.

# Usage: ./start-all.sh [debug] [logfile]

LOG_LEVEL="INFO"
LOG_FILE="backend/logs/app.log"

if [[ "$1" == "debug" ]]; then
  LOG_LEVEL="DEBUG"
  shift
fi

if [[ -n "$1" ]]; then
  LOG_FILE="$1"
fi

export LOG_LEVEL
export LOG_FILE

echo "Starting application with LOG_LEVEL=$LOG_LEVEL, LOG_FILE=$LOG_FILE"

# Start the backend (FastAPI/Uvicorn)
echo "Starting backend (FastAPI/Uvicorn) on http://localhost:8000 ..."
source .venv/bin/activate
LOG_LEVEL=$LOG_LEVEL LOG_FILE=$LOG_FILE uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Build the frontend (React)
echo "Building frontend (React)..."
cd frontend
LOG_LEVEL=$LOG_LEVEL npm run build

# Start the frontend (React)
echo "Starting frontend (React) on http://localhost:3000 ..."
LOG_LEVEL=$LOG_LEVEL npm start &
FRONTEND_PID=$!
cd ..

# Wait for both processes
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait $BACKEND_PID $FRONTEND_PID 