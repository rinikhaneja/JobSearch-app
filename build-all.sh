#!/bin/bash
set -e

# Usage:
#   ./build-all.sh [clean] [build]
#   ./build-all.sh build clean (will run clean then build)
#   ./build-all.sh clean build
#   ./build-all.sh clean
#   ./build-all.sh build
#   ./build-all.sh

CLEAN=false
BUILD=false
ORDER=()

for arg in "$@"; do
  case $arg in
    clean)
      CLEAN=true
      ;;
    build)
      BUILD=true
      ;;
  esac
done

# If both are present, always clean first then build
if $CLEAN && $BUILD; then
  ORDER=(clean build)
elif $CLEAN; then
  ORDER=(clean)
elif $BUILD; then
  ORDER=(build)
fi

# Default: if no args, just build
if [ ${#ORDER[@]} -eq 0 ]; then
  ORDER=(build)
fi

# Build all modules: backend and frontend

if [ "$1" == "clean" ]; then
  echo "Cleaning backend..."
  (cd backend && ./build.sh clean)
  echo "Cleaning frontend..."
  (cd frontend && ./build.sh clean)
  echo "All modules cleaned."
  exit 0
fi

# Backend
if [ -f backend/build.sh ]; then
  echo "Running backend/build.sh ${ORDER[*]} ..."
  (cd backend && ./build.sh "${ORDER[@]}")
else
  echo "backend/build.sh not found!"
  exit 1
fi

# Frontend
if [ -f frontend/build.sh ]; then
  echo "Running frontend/build.sh ${ORDER[*]} ..."
  (cd frontend && ./build.sh "${ORDER[@]}")
else
  echo "frontend/build.sh not found!"
  exit 1
fi

echo "Full application build/clean complete." 