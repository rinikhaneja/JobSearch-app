#!/bin/bash
set -e

# Build script for FastAPI backend

# Usage:
#   ./build.sh [clean] [build]
#   ./build.sh build clean
#   ./build.sh clean build
#   ./build.sh clean
#   ./build.sh build
#   ./build.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CLEAN=false
BUILD=false
ORDER=()

for arg in "$@"; do
  case $arg in
    clean)
      CLEAN=true
      ORDER+=(clean)
      ;;
    build)
      BUILD=true
      ORDER+=(build)
      ;;
  esac
done

# Default: if no args, just build
if [ ${#ORDER[@]} -eq 0 ]; then
  ORDER+=(build)
  BUILD=true
fi

run_clean() {
  echo "Cleaning backend..."
  find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} +
  find "$SCRIPT_DIR" -type f -name "*.pyc" -delete
  rm -rf "$SCRIPT_DIR/logs"/*
  rm -rf "$SCRIPT_DIR/uploads"/*
  echo "Backend cleaned."
}

run_build() {
  echo "Building backend..."
  pip install --upgrade pip
  pip install -r "$SCRIPT_DIR/requirements.txt"
  if [ -f "$SCRIPT_DIR/alembic.ini" ]; then
    alembic upgrade head
  fi
  echo "Backend build complete."
}

for action in "${ORDER[@]}"; do
  if [ "$action" == "clean" ]; then
    run_clean
  elif [ "$action" == "build" ]; then
    run_build
  fi
done 