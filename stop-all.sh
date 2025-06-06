#!/bin/bash

# Stop backend (FastAPI/Uvicorn)
echo "Stopping backend (FastAPI/Uvicorn)..."
BACKEND_PID=$(pgrep -f "uvicorn backend.app.main:app")
if [ -n "$BACKEND_PID" ]; then
  kill $BACKEND_PID
  echo "Backend stopped (PID: $BACKEND_PID)"
else
  echo "Backend process not found."
fi

# Stop frontend (React)
echo "Stopping frontend (React)..."
FRONTEND_PID=$(pgrep -f "react-scripts start")
if [ -n "$FRONTEND_PID" ]; then
  kill $FRONTEND_PID
  echo "Frontend stopped (PID: $FRONTEND_PID)"
else
  echo "Frontend process not found."
fi

# Clear npm and pip cache
echo "Clearing npm and pip cache..."
npm cache clean --force
pip cache purge 