#!/bin/bash

# Deploy Todo application to Minikube using Helm
# Usage: ./scripts/deploy-minikube.sh [release-name]

set -e

RELEASE_NAME=${1:-todo-app}
NAMESPACE="todo-app"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Deploying Todo application to Minikube"
echo "Release name: $RELEASE_NAME"
echo "Namespace: $NAMESPACE"

# Check prerequisites
if ! command -v minikube &> /dev/null; then
    echo "❌ Error: minikube not found. Please install Minikube first."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ Error: helm not found. Please install Helm first."
    exit 1
fi

# Check Minikube is running
if ! minikube status &> /dev/null; then
    echo "Starting Minikube..."
    minikube start --cpus=2 --memory=4096 --disk-size=20g
fi

# Enable ingress
echo "Enabling Ingress addon..."
minikube addons enable ingress

# Configure Docker environment
echo "Configuring Docker environment for Minikube..."
eval $(minikube docker-env)

# Build images
echo "Building Docker images..."
"$SCRIPT_DIR/build-images.sh" latest

# Create namespace
echo "Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Check for required secrets
if ! kubectl get secret backend-secrets -n $NAMESPACE &> /dev/null; then
    echo ""
    echo "⚠️  Warning: backend-secrets not found!"
    echo "Please create the secret first:"
    echo ""
    echo "kubectl create secret generic backend-secrets \\"
    echo "  --from-literal=database_url=\"postgresql://...\" \\"
    echo "  --from-literal=better_auth_secret=\"your-secret\" \\"
    echo "  --namespace=$NAMESPACE"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to cancel..."
fi

# Install Helm chart
echo ""
echo "Installing Helm chart..."
cd "$PROJECT_ROOT"
helm upgrade --install $RELEASE_NAME ./helm-chart \
  --namespace $NAMESPACE \
  --create-namespace \
  --wait \
  --timeout 5m

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Minikube IP: $MINIKUBE_IP"
echo ""
echo "Add to /etc/hosts:"
echo "  $MINIKUBE_IP todo.local"
echo ""
echo "Access application at: http://todo.local"
echo ""
echo "Check status:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get svc -n $NAMESPACE"
echo "  kubectl get ingress -n $NAMESPACE"

