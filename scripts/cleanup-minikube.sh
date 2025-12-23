#!/bin/bash

# Clean up Todo application deployment from Minikube
# Usage: ./scripts/cleanup-minikube.sh [release-name]

set -e

RELEASE_NAME=${1:-todo-app}
NAMESPACE="todo-app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Cleaning up Todo application from Minikube"
echo "Release name: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"

# Confirm deletion
read -p "Are you sure you want to delete the deployment? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

# Uninstall Helm release
if helm list -n $NAMESPACE | grep -q $RELEASE_NAME; then
    echo "Uninstalling Helm release..."
    helm uninstall $RELEASE_NAME -n $NAMESPACE
else
    echo "Helm release not found, skipping..."
fi

# Delete namespace (removes all resources)
if kubectl get namespace $NAMESPACE &> /dev/null; then
    echo "Deleting namespace..."
    kubectl delete namespace $NAMESPACE
else
    echo "Namespace not found, skipping..."
fi

# Optional: Remove Docker images
read -p "Remove Docker images? (yes/no): " remove_images
if [ "$remove_images" == "yes" ]; then
    echo "Removing Docker images..."
    eval $(minikube docker-env) 2>/dev/null || true
    docker rmi todo-frontend:latest todo-backend:latest 2>/dev/null || true
    echo "Images removed (if they existed)."
fi

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To remove /etc/hosts entry:"
echo "  sudo sed -i '/todo.local/d' /etc/hosts"

