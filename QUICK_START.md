# Quick Start Guide - Phase V Cloud-Native Todo App

Complete deployment guide for the event-driven, microservices-based Todo application with Kafka (Redpanda Cloud), Dapr, and Kubernetes.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                          │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Frontend │  │ Backend  │  │  Notif   │  │  Audit   │   │
│  │(Next.js) │  │(FastAPI) │  │ Service  │  │ Service  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │    Dapr Sidecars     │          │          │        │
│       └──────────┬────────────┴──────────┴──────────┘        │
│                  │                                           │
│                  ▼                                           │
│         ┌────────────────┐                                   │
│         │ Redpanda Cloud │  (Kafka)                         │
│         │   - task-events                                    │
│         │   - reminders                                      │
│         │   - task-updates                                   │
│         │   - recurring-tasks                                │
│         └────────────────┘                                   │
└──────────────────────────────────────────────────────────────┘
```

## Prerequisites

### Required Tools
- **Docker** (>= 20.10)
- **Kubernetes** (>= 1.24):
  - Minikube (local) OR
  - DOKS/GKE/AKS (cloud)
- **kubectl** (>= 1.24)
- **Dapr CLI** (>= 1.12)
- **Helm** (>= 3.10) - optional

### Accounts
- **Redpanda Cloud** account (free tier)
- **Neon PostgreSQL** database (free tier)
- **Container Registry** (Docker Hub, GHCR, or cloud provider)

## Part 1: Local Development Setup

### 1. Install Prerequisites

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install docker kubectl minikube helm
brew install dapr/tap/dapr-cli

# Start Docker Desktop
open /Applications/Docker.app

# Initialize Dapr
dapr init
```

#### Linux
```bash
# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr
dapr init
```

#### Windows
```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install tools
choco install docker-desktop kubectl minikube kubernetes-helm

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr
dapr init
```

### 2. Start Minikube

```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### 3. Install Dapr in Kubernetes

```bash
# Install Dapr control plane
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
# dapr-sidecar-injector  dapr-system  True     Running  1         1.12.0   1m
# dapr-sentry            dapr-system  True     Running  1         1.12.0   1m
# dapr-operator          dapr-system  True     Running  1         1.12.0   1m
# dapr-placement         dapr-system  True     Running  1         1.12.0   1m
```

## Part 2: Configure External Services

### 1. Set Up Redpanda Cloud (Kafka)

Follow the detailed guide: [docs/REDPANDA_SETUP.md](docs/REDPANDA_SETUP.md)

**Quick summary**:
1. Create account at https://redpanda.com/cloud
2. Create serverless cluster
3. Create topics: `task-events`, `reminders`, `task-updates`, `recurring-tasks`
4. Get credentials (bootstrap server, username, password)

### 2. Set Up Neon PostgreSQL

1. Go to [Neon Console](https://console.neon.tech/)
2. Create new project: "todo-app"
3. Create database: "todo_db"
4. Get connection string (copy from dashboard)

**Format**: `postgresql://user:password@host/dbname?sslmode=require`

## Part 3: Configure Kubernetes Secrets

### 1. Create Kafka Secrets

```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='YOUR_REDPANDA_USERNAME' \
  --from-literal=password='YOUR_REDPANDA_PASSWORD' \
  --from-literal=bootstrapServer='YOUR_CLUSTER.cloud.redpanda.com:9092'
```

### 2. Create Database Secrets

```bash
kubectl create secret generic db-secrets \
  --from-literal=databaseUrl='YOUR_NEON_CONNECTION_STRING'
```

### 3. Create API Secrets

```bash
# Generate a random JWT secret
JWT_SECRET=$(openssl rand -base64 32)

kubectl create secret generic api-secrets \
  --from-literal=jwtSecret="$JWT_SECRET" \
  --from-literal=betterAuthSecret="$JWT_SECRET" \
  --from-literal=nextPublicApiUrl='http://todo.local'
```

### 4. Verify Secrets

```bash
kubectl get secrets
# Should see: kafka-secrets, db-secrets, api-secrets
```

## Part 4: Update Dapr Components

### 1. Edit Kafka Component

Edit `k8s/dapr-components/pubsub-kafka.yaml`:

```yaml
- name: brokers
  value: "YOUR_CLUSTER.cloud.redpanda.com:9092"  # Replace with your bootstrap server
```

### 2. Apply Dapr Components

```bash
kubectl apply -f k8s/dapr-components/

# Verify components
kubectl get components
```

## Part 5: Build and Push Docker Images

### Option A: Local Minikube Registry

```bash
# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend
docker build -t todo-notification:latest ./services/notification-service
docker build -t todo-audit:latest ./services/audit-service

# Verify images
docker images | grep todo
```

### Option B: Docker Hub

```bash
# Login to Docker Hub
docker login

# Build and push images
docker build -t YOUR_USERNAME/todo-frontend:latest ./frontend
docker push YOUR_USERNAME/todo-frontend:latest

docker build -t YOUR_USERNAME/todo-backend:latest ./backend
docker push YOUR_USERNAME/todo-backend:latest

docker build -t YOUR_USERNAME/todo-notification:latest ./services/notification-service
docker push YOUR_USERNAME/todo-notification:latest

docker build -t YOUR_USERNAME/todo-audit:latest ./services/audit-service
docker push YOUR_USERNAME/todo-audit:latest

# Update deployment manifests with your Docker Hub username
sed -i 's/todo-frontend:latest/YOUR_USERNAME\/todo-frontend:latest/g' k8s/frontend/deployment.yaml
sed -i 's/todo-backend:latest/YOUR_USERNAME\/todo-backend:latest/g' k8s/backend/deployment.yaml
# ... repeat for other services
```

## Part 6: Deploy Application

### 1. Deploy All Services

```bash
# Deploy secrets (if using YAML instead of kubectl create)
kubectl apply -f k8s/secrets/

# Deploy Dapr components
kubectl apply -f k8s/dapr-components/

# Deploy services
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/notification-service/
kubectl apply -f k8s/audit-service/

# Deploy ingress
kubectl apply -f k8s/ingress.yaml
```

### 2. Verify Deployments

```bash
# Check pods
kubectl get pods

# Expected output:
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-service-xxxxx                  2/2     Running   0          1m
# frontend-service-xxxxx                 1/1     Running   0          1m
# notification-service-xxxxx             2/2     Running   0          1m
# audit-service-xxxxx                    2/2     Running   0          1m

# Check services
kubectl get svc

# Check Dapr components
dapr components -k
```

### 3. Wait for Pods to be Ready

```bash
kubectl wait --for=condition=ready pod -l app=backend --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=300s
```

## Part 7: Access the Application

### Minikube Local Access

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Access application
open http://todo.local
```

### Port Forwarding (Alternative)

```bash
# Forward frontend
kubectl port-forward svc/frontend-service 3000:3000 &

# Forward backend
kubectl port-forward svc/backend-service 8000:8000 &

# Access
open http://localhost:3000
```

## Part 8: Verify Event-Driven Architecture

### 1. Check Backend Logs

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')

# View logs (main container)
kubectl logs $BACKEND_POD -c backend

# View Dapr sidecar logs
kubectl logs $BACKEND_POD -c daprd
```

### 2. Create a Test Task

```bash
# Get user token (login first via UI)
# Then create task via API
curl -X POST http://todo.local/api/YOUR_USER_ID/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test task",
    "priority": "high",
    "tags": ["test"]
  }'
```

### 3. Verify Kafka Events

Check Redpanda Cloud console:
1. Go to Topics → `task-events`
2. Should see new message with event_type: "created"

### 4. Check Audit Service

```bash
# Get audit service pod
AUDIT_POD=$(kubectl get pods -l app=audit -o jsonpath='{.items[0].metadata.name}')

# Check logs
kubectl logs $AUDIT_POD -c audit

# Query audit API
kubectl port-forward svc/audit-service 8001:8001 &
curl http://localhost:8001/api/audit/events
```

## Part 9: Monitoring and Troubleshooting

### View All Logs

```bash
# All pods
kubectl logs -l app=backend --tail=50
kubectl logs -l app=frontend --tail=50
kubectl logs -l app=notification --tail=50
kubectl logs -l app=audit --tail=50
```

### Common Issues

#### Pods Not Starting
```bash
# Describe pod for events
kubectl describe pod <pod-name>

# Check image pull
kubectl get events --sort-by='.lastTimestamp'
```

#### Dapr Sidecar Issues
```bash
# Check Dapr components
kubectl get components

# Restart Dapr control plane
kubectl rollout restart deployment -n dapr-system
```

#### Kafka Connection Issues
```bash
# Test from backend pod
kubectl exec -it $BACKEND_POD -c backend -- python -c "
import httpx
response = httpx.post('http://localhost:3500/v1.0/publish/kafka-pubsub/task-events', json={'test': 'value'})
print(response.status_code)
"
```

## Part 10: Development Workflow

### Make Code Changes

1. Update code locally
2. Rebuild Docker image
3. Push to registry (if using remote)
4. Restart deployment

```bash
# Rebuild and update
docker build -t todo-backend:latest ./backend
kubectl rollout restart deployment backend-service

# Watch rollout
kubectl rollout status deployment backend-service
```

### Hot Reload (Development)

Use Skaffold for automatic rebuilds:

```bash
# Install Skaffold
brew install skaffold  # macOS
# or curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64

# Run with hot reload
skaffold dev
```

## Next Steps

- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Set up log aggregation (Loki)
- [ ] Enable distributed tracing (Jaeger)
- [ ] Deploy to cloud (DOKS, GKE, or AKS)
- [ ] Configure TLS/SSL certificates
- [ ] Set up custom domain

## Useful Commands

```bash
# View all resources
kubectl get all

# Delete everything
kubectl delete -f k8s/backend/
kubectl delete -f k8s/frontend/
kubectl delete -f k8s/notification-service/
kubectl delete -f k8s/audit-service/
kubectl delete -f k8s/ingress.yaml
kubectl delete -f k8s/dapr-components/

# Uninstall Dapr
dapr uninstall -k

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Support and Resources

- [Phase V Progress](./PHASE_V_PROGRESS.md)
- [Redpanda Setup Guide](./docs/REDPANDA_SETUP.md)
- [Frontend Guidelines](./frontend/CLAUDE.md)
- [Backend Guidelines](./backend/CLAUDE.md)
- [Dapr Documentation](https://docs.dapr.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
