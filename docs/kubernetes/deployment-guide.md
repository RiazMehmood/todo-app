# Kubernetes Deployment Guide

Step-by-step guide to deploy the Todo application to Minikube.

## Prerequisites

- Minikube installed and running (see [setup-minikube.md](setup-minikube.md))
- Helm 3.x installed
- Docker images built and available to Minikube

## Step 1: Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --cpus=2 --memory=4096 --disk-size=20g

# Enable Ingress addon
minikube addons enable ingress

# Verify cluster is running
kubectl get nodes
```

## Step 2: Configure Docker Environment

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify connection
docker ps
```

## Step 3: Build Docker Images

```bash
# Build frontend image
cd frontend
docker build -t todo-frontend:latest .

# Build backend image
cd ../backend
docker build -t todo-backend:latest .

# Verify images
docker images | grep todo
```

## Step 4: Create Namespace

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Verify namespace
kubectl get namespace todo-app
```

## Step 5: Create Secrets

**Important**: Replace placeholder values with actual secrets!

```bash
# Create backend secrets
kubectl create secret generic backend-secrets \
  --from-literal=database_url="postgresql://user:pass@host:5432/dbname" \
  --from-literal=better_auth_secret="your-jwt-secret-here" \
  --namespace=todo-app

# Verify secret
kubectl get secret backend-secrets -n todo-app
```

## Step 6: Deploy Using Raw Kubernetes Manifests

### Option A: Deploy All at Once

```bash
# Apply all manifests
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/postgres/  # Optional if using in-cluster DB
kubectl apply -f k8s/ingress.yaml
```

### Option B: Deploy Using Helm Chart (Recommended)

```bash
# Install Helm chart
helm install todo-app ./helm-chart \
  --namespace todo-app \
  --create-namespace \
  --set backend.secrets.database_url="postgresql://user:pass@host:5432/dbname" \
  --set backend.secrets.better_auth_secret="your-jwt-secret-here"

# Verify installation
helm list -n todo-app
```

## Step 7: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Wait for all pods to be ready (should take 1-3 minutes)
kubectl wait --for=condition=ready pod -l app=todo-app -n todo-app --timeout=300s

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app
```

## Step 8: Configure Local Access

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Add to /etc/hosts (Linux/macOS)
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts

# Windows: Edit C:\Windows\System32\drivers\etc\hosts manually
```

## Step 9: Access Application

```bash
# Open in browser
# Linux/macOS
open http://todo.local
# or
xdg-open http://todo.local

# Or use Minikube service
minikube service frontend-service -n todo-app
```

## Step 10: Verify Functionality

1. Open http://todo.local in browser
2. Create a new account
3. Log in
4. Create a todo task
5. Verify task appears in list
6. Update task
7. Delete task

## Upgrading Deployment

### Using Helm

```bash
# Upgrade with new image tag
helm upgrade todo-app ./helm-chart \
  --set frontend.image.tag=v2.1.0 \
  --set backend.image.tag=v2.1.0

# Rollback if needed
helm rollback todo-app
```

### Using kubectl

```bash
# Update image in deployment
kubectl set image deployment/frontend frontend=todo-frontend:v2.1.0 -n todo-app
kubectl set image deployment/backend backend=todo-backend:v2.1.0 -n todo-app

# Watch rollout
kubectl rollout status deployment/frontend -n todo-app
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n todo-app

# Describe pod for details
kubectl describe pod <pod-name> -n todo-app

# View logs
kubectl logs <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --previous  # Previous container logs
```

### Services Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n todo-app

# Test service from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend-service:8000/health
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress -n todo-app

# Check ingress controller
kubectl get pods -n ingress-nginx

# Verify /etc/hosts entry
cat /etc/hosts | grep todo.local
```

## Cleanup

```bash
# Delete Helm release
helm uninstall todo-app -n todo-app

# Or delete using kubectl
kubectl delete -f k8s/

# Delete namespace (removes everything)
kubectl delete namespace todo-app
```

