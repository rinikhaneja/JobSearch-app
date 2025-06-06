#!/bin/bash
set -e

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
  echo "Cleaning frontend..."
  if npm --prefix "$SCRIPT_DIR" run | grep -q "clean"; then
    npm --prefix "$SCRIPT_DIR" run clean
  fi
  rm -rf "$SCRIPT_DIR/build/"
  rm -rf "$SCRIPT_DIR/node_modules/"
  echo "Frontend cleaned."
}

run_build() {
  echo "Building frontend..."
  npm install --prefix "$SCRIPT_DIR" --legacy-peer-deps
  npm run --prefix "$SCRIPT_DIR" build
  echo "Frontend build complete."
}

for action in "${ORDER[@]}"; do
  if [ "$action" == "clean" ]; then
    run_clean
  elif [ "$action" == "build" ]; then
    run_build
  fi
done 