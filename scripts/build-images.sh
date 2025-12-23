#!/bin/bash

# Build Docker images for Todo application
# Usage: ./scripts/build-images.sh [tag]

set -e

TAG=${1:-latest}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Building Todo application Docker images with tag: $TAG"
echo "Project root: $PROJECT_ROOT"

# Check if Minikube is running
if command -v minikube &> /dev/null; then
    if minikube status &> /dev/null; then
        echo "Minikube is running. Using Minikube's Docker daemon..."
        eval $(minikube docker-env)
    fi
fi

# Build frontend
echo ""
echo "Building frontend image..."
cd "$PROJECT_ROOT/frontend"
docker build -t todo-frontend:$TAG .

# Build backend
echo ""
echo "Building backend image..."
cd "$PROJECT_ROOT/backend"
docker build -t todo-backend:$TAG .

# Verify images
echo ""
echo "Verifying images..."
docker images | grep -E "todo-frontend|todo-backend" | grep "$TAG"

echo ""
echo "✅ Build complete!"
echo "Images:"
echo "  - todo-frontend:$TAG"
echo "  - todo-backend:$TAG"

