# Deployment Guide - Phase V

## Overview
This guide covers deployment to both local Kubernetes (Minikube) and cloud providers (DigitalOcean DOKS, Google Cloud GKE, or Azure AKS).

## Prerequisites

### Local Development
- Docker Desktop (latest version)
- Minikube
- kubectl
- Helm
- Dapr CLI

### Cloud Deployment
- One of:
  - DigitalOcean account ($200 free credit)
  - Google Cloud account ($300 free credit)
  - Azure account ($200 free credit)
- GitHub account (for CI/CD)

## Part B: Local Deployment (Minikube)

### Step 1: Install Prerequisites

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Dapr CLI
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Install kubectl-ai (optional but recommended)
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64
sudo install kubectl-ai-linux-amd64 /usr/local/bin/kubectl-ai
```

### Step 2: Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Step 3: Initialize Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k

# Verify installation
dapr status -k
```

### Step 4: Set up Local Kafka (Redpanda)

**Option A: Use Redpanda Cloud (Recommended)**
- Sign up at https://redpanda.com/cloud
- Create serverless cluster (free tier)
- Create topics: `task-events`, `reminders`, `task-updates`, `recurring-tasks`
- Get connection details

**Option B: Deploy Redpanda on Minikube**

```bash
# Add Redpanda Helm repo
helm repo add redpanda https://charts.redpanda.com
helm repo update

# Install Redpanda
helm install redpanda redpanda/redpanda \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=2Gi \
  --namespace redpanda \
  --create-namespace
```

### Step 5: Create Kubernetes Secrets

```bash
# API Secrets
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key='your-openai-api-key' \
  --from-literal=better-auth-secret='your-better-auth-secret'

# Database Secrets
kubectl create secret generic db-secrets \
  --from-literal=connection_string='your-neon-db-connection-string'

# Kafka Secrets (if using Redpanda Cloud)
kubectl create secret generic kafka-secrets \
  --from-literal=username='your-kafka-username' \
  --from-literal=password='your-kafka-password' \
  --from-literal=brokers='your-cluster.cloud.redpanda.com:9092'
```

### Step 6: Deploy Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/

# Verify components
dapr components -k
```

### Step 7: Deploy Application with Helm

```bash
# Package Helm chart
cd helm-chart
helm package todo-app

# Install
helm install todo-app ./todo-app-0.1.0.tgz \
  --set frontend.image=your-frontend-image \
  --set backend.image=your-backend-image \
  --set notificationService.image=your-notification-image \
  --set recurringTaskService.image=your-recurring-task-image

# Verify deployment
kubectl get pods
kubectl get services
```

### Step 8: Access Application Locally

```bash
# Port forward frontend
kubectl port-forward svc/frontend 3000:3000

# Port forward backend
kubectl port-forward svc/backend 8000:8000

# Access in browser
open http://localhost:3000
```

### Step 9: Test Locally

```bash
# Check Dapr dashboard
dapr dashboard -k

# View logs
kubectl logs -f deployment/backend -c backend
kubectl logs -f deployment/backend -c daprd

# Test reminder cron (should trigger every 5 minutes)
kubectl logs -f deployment/backend | grep "reminder"
```

---

## Part C: Cloud Deployment

### Choose Your Cloud Provider

#### Option 1: DigitalOcean Kubernetes (DOKS)

**Advantages**:
- Simple setup
- $200 free credit for 60 days
- Straightforward pricing
- Good for hackathon/learning

**Setup Steps**:

1. **Create DOKS Cluster**
```bash
# Install doctl (DigitalOcean CLI)
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-1.98.1-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --wait

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-cluster
```

2. **Install Dapr**
```bash
dapr init -k
```

3. **Deploy Application**
```bash
# Same as Minikube steps 5-7
kubectl create secret generic api-secrets ...
kubectl apply -f k8s/dapr-components/
helm install todo-app ./todo-app-0.1.0.tgz
```

4. **Set up LoadBalancer**
```yaml
# k8s/frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 3000
  selector:
    app: frontend
```

```bash
# Apply service
kubectl apply -f k8s/frontend-service.yaml

# Get external IP
kubectl get svc frontend

# Access app at http://<EXTERNAL-IP>
```

#### Option 2: Google Kubernetes Engine (GKE)

**Advantages**:
- $300 free credit for 90 days
- Powerful features (autopilot, workload identity)
- Industry standard

**Setup Steps**:

1. **Create GKE Cluster**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create cluster
gcloud container clusters create todo-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials todo-cluster --zone us-central1-a
```

2. **Install Dapr**
```bash
dapr init -k
```

3. **Deploy** (same as DOKS)

#### Option 3: Azure Kubernetes Service (AKS)

**Advantages**:
- $200 free credit for 30 days
- 12 months of free services
- Strong enterprise features

**Setup Steps**:

1. **Create AKS Cluster**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create cluster
az aks create \
  --resource-group todo-rg \
  --name todo-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-cluster
```

2. **Install Dapr**
```bash
dapr init -k
```

3. **Deploy** (same as DOKS)

---

## CI/CD with GitHub Actions

### Step 1: Create Docker Registry

**Option A: Docker Hub**
```bash
docker login
```

**Option B: GitHub Container Registry**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Step 2: Create GitHub Secrets

Go to GitHub repo → Settings → Secrets → New repository secret

Add:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `KUBECONFIG` (base64 encoded kubeconfig file)
- `DIGITALOCEAN_TOKEN` (if using DOKS)

### Step 3: Create GitHub Actions Workflow

**File**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/todo-frontend:latest

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/todo-backend:latest

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig.yaml
          export KUBECONFIG=kubeconfig.yaml

      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install todo-app ./helm-chart/todo-app \
            --set frontend.image=${{ secrets.DOCKER_USERNAME }}/todo-frontend:latest \
            --set backend.image=${{ secrets.DOCKER_USERNAME }}/todo-backend:latest \
            --wait
```

---

## Monitoring & Logging

### Dapr Dashboard

```bash
# Access Dapr dashboard
dapr dashboard -k

# Port forward
kubectl port-forward svc/dapr-dashboard 8080:8080
open http://localhost:8080
```

### Kubernetes Dashboard

```bash
# Deploy Kubernetes dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Create admin user
kubectl create serviceaccount dashboard-admin-sa
kubectl create clusterrolebinding dashboard-admin-sa \
  --clusterrole=cluster-admin \
  --serviceaccount=default:dashboard-admin-sa

# Get token
kubectl create token dashboard-admin-sa

# Access dashboard
kubectl proxy
open http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

### Logging with kubectl

```bash
# View logs
kubectl logs -f deployment/backend -c backend
kubectl logs -f deployment/backend -c daprd

# View all pods
kubectl get pods

# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Monitoring with Prometheus & Grafana (Optional)

```bash
# Install Prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack

# Port forward Grafana
kubectl port-forward svc/prometheus-grafana 3000:80

# Login (admin/prom-operator)
open http://localhost:3000
```

---

## Troubleshooting

### Common Issues

**1. Pods not starting**
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**2. Dapr sidecar not injecting**
```bash
# Check annotations
kubectl get deployment <deployment-name> -o yaml | grep dapr

# Should see:
# dapr.io/enabled: "true"
# dapr.io/app-id: "backend-service"
# dapr.io/app-port: "8000"
```

**3. Kafka connection issues**
```bash
# Test connection from pod
kubectl exec -it <backend-pod> -- curl http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
```

**4. Secrets not found**
```bash
# List secrets
kubectl get secrets

# Describe secret
kubectl describe secret api-secrets
```

### Using kubectl-ai for Debugging

```bash
# Ask kubectl-ai for help
kubectl-ai "why are my pods not starting?"
kubectl-ai "how do I check dapr component status?"
kubectl-ai "scale backend to 3 replicas"
```

---

## Performance Optimization

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Resource Requests/Limits

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

## Success Criteria

### Local Deployment (Minikube)
- ✅ Application running on Minikube
- ✅ All pods healthy
- ✅ Dapr components configured
- ✅ Kafka messages flowing
- ✅ Reminders triggering every 5 minutes
- ✅ Can access app via port-forward

### Cloud Deployment
- ✅ Application deployed on DOKS/GKE/AKS
- ✅ LoadBalancer providing public IP
- ✅ Connected to Redpanda Cloud
- ✅ CI/CD pipeline deploying on git push
- ✅ Monitoring dashboard accessible
- ✅ Application accessible via public URL
- ✅ All advanced features working

---

## Cost Optimization

### Free Tier Usage
- **DigitalOcean**: $200 credit, use smallest nodes
- **GKE**: $300 credit, use e2-medium instances
- **Azure**: $200 credit, use Standard_B2s instances
- **Redpanda**: Free serverless tier (enough for hackathon)
- **Neon DB**: Free tier (enough for hackathon)

### Clean Up Resources

```bash
# Delete cluster (DOKS)
doctl kubernetes cluster delete todo-cluster

# Delete cluster (GKE)
gcloud container clusters delete todo-cluster --zone us-central1-a

# Delete cluster (AKS)
az aks delete --resource-group todo-rg --name todo-cluster
```
