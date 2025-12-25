# DigitalOcean Kubernetes (DOKS) Deployment Guide
# Phase V - Cloud-Native Deployment

**Cloud Provider**: DigitalOcean
**Date**: 2025-12-25
**Status**: In Progress

## Overview

Deploying the Todo application to DigitalOcean Kubernetes (DOKS) with:
- **Kubernetes**: 2-node cluster (s-2vcpu-4gb droplets)
- **Dapr**: v1.16.5 for microservices runtime
- **Redpanda Cloud**: Event streaming (Kafka-compatible)
- **Neon DB**: Serverless PostgreSQL
- **Load Balancer**: Automatic with DOKS
- **Cost**: $48/month (~$0 with $200 credit for 60 days)

---

## Phase 1: DigitalOcean Setup

### Step 1: Install doctl (DigitalOcean CLI)

**Check if already installed:**
```bash
doctl version
```

**If not installed, install it:**

**Linux:**
```bash
cd ~
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**Verify installation:**
```bash
doctl version
# Should show: doctl version 1.104.0 or higher
```

### Step 2: Authenticate with DigitalOcean

**Create API Token:**
1. Go to: https://cloud.digitalocean.com/account/api/tokens
2. Click **Generate New Token**
3. Name: `todo-phase-v-deployment`
4. Scopes: **Read and Write**
5. Copy the token (you won't see it again!)

**Authenticate doctl:**
```bash
doctl auth init
# Paste your API token when prompted
```

**Verify authentication:**
```bash
doctl account get
# Should show your DigitalOcean account details
```

### Step 3: Check Available Resources

**Check available Kubernetes versions:**
```bash
doctl kubernetes options versions
```

**Check available node sizes:**
```bash
doctl kubernetes options sizes
# Look for: s-2vcpu-4gb ($36/month per node)
```

**Check available regions:**
```bash
doctl kubernetes options regions
# Recommended: nyc1, nyc3, sfo3, fra1
```

---

## Phase 2: Create Kubernetes Cluster

### Step 1: Create DOKS Cluster

**Command:**
```bash
doctl kubernetes cluster create todo-phase-v \
  --region nyc1 \
  --version 1.31.1-do.4 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2;auto-scale=true;min-nodes=1;max-nodes=3" \
  --wait
```

**Parameters Explained:**
- `todo-phase-v` - Cluster name
- `--region nyc1` - New York datacenter (choose closest to you)
- `--version 1.31.1-do.4` - Latest stable Kubernetes
- `--node-pool` - 2 nodes, 2 vCPU, 4GB RAM each, auto-scaling 1-3
- `--wait` - Wait for cluster to be ready

**This will take 3-5 minutes.** ☕

**Expected output:**
```
Notice: Cluster is provisioning, waiting for cluster to be running
Notice: Cluster created, fetching credentials
Notice: Adding cluster credentials to kubeconfig file found in "/home/user/.kube/config"
Notice: Setting current-context to do-nyc1-todo-phase-v
ID                                      Name            Region    Version           Auto Upgrade    Status     Node Pools
<cluster-id>                            todo-phase-v    nyc1      1.31.1-do.4      false           running    worker-pool
```

### Step 2: Verify Cluster Access

**Get cluster credentials (if not auto-added):**
```bash
doctl kubernetes cluster kubeconfig save todo-phase-v
```

**Verify kubectl access:**
```bash
kubectl get nodes
```

**Expected output:**
```
NAME                   STATUS   ROLES    AGE   VERSION
worker-pool-xxxxx      Ready    <none>   2m    v1.31.1
worker-pool-yyyyy      Ready    <none>   2m    v1.31.1
```

**Create namespace:**
```bash
kubectl create namespace todo-app
kubectl config set-context --current --namespace=todo-app
```

**Cluster is ready! ✅**

---

## Phase 3: Container Registry Setup

You have two options:

### Option A: Docker Hub (Recommended - Free & Simple)

**1. Sign up/login:**
- Go to: https://hub.docker.com
- Create account or login

**2. Create access token:**
- Go to: Account Settings → Security → New Access Token
- Name: `todo-phase-v`
- Copy the token

**3. Login from terminal:**
```bash
docker login
# Username: <your-dockerhub-username>
# Password: <paste-access-token>
```

**4. Set registry prefix:**
```bash
export DOCKER_REGISTRY="<your-dockerhub-username>"
# Example: export DOCKER_REGISTRY="riazulhaq"
```

### Option B: DigitalOcean Container Registry

**1. Create registry:**
```bash
doctl registry create todo-registry --region nyc3
```

**2. Login:**
```bash
doctl registry login
```

**3. Set registry prefix:**
```bash
export DOCKER_REGISTRY="registry.digitalocean.com/todo-registry"
```

---

## Phase 4: Build & Push Docker Images

### Step 1: Build Images

**Navigate to project root:**
```bash
cd /home/riaz/Desktop/todo\ hackathon\ II/todo
```

**Build backend:**
```bash
docker build -t ${DOCKER_REGISTRY}/todo-backend:v1.0.0 \
  -f backend/Dockerfile backend/
```

**Build notification service:**
```bash
docker build -t ${DOCKER_REGISTRY}/todo-notification:v1.0.0 \
  -f notification-service/Dockerfile notification-service/
```

**Build audit service:**
```bash
docker build -t ${DOCKER_REGISTRY}/todo-audit:v1.0.0 \
  -f audit-service/Dockerfile audit-service/
```

**Build frontend (if exists):**
```bash
docker build -t ${DOCKER_REGISTRY}/todo-frontend:v1.0.0 \
  -f frontend/Dockerfile frontend/
```

### Step 2: Push Images

```bash
docker push ${DOCKER_REGISTRY}/todo-backend:v1.0.0
docker push ${DOCKER_REGISTRY}/todo-notification:v1.0.0
docker push ${DOCKER_REGISTRY}/todo-audit:v1.0.0
docker push ${DOCKER_REGISTRY}/todo-frontend:v1.0.0
```

### Step 3: Update Deployment Files

**Update image references in all deployment YAML files:**
```bash
# Backend
sed -i "s|image: todo-backend:latest|image: ${DOCKER_REGISTRY}/todo-backend:v1.0.0|g" k8s/backend/deployment.yaml

# Notification service
sed -i "s|image: todo-notification:latest|image: ${DOCKER_REGISTRY}/todo-notification:v1.0.0|g" k8s/notification-service/deployment.yaml

# Audit service
sed -i "s|image: todo-audit:latest|image: ${DOCKER_REGISTRY}/todo-audit:v1.0.0|g" k8s/audit-service/deployment.yaml

# Frontend (if exists)
sed -i "s|image: todo-frontend:latest|image: ${DOCKER_REGISTRY}/todo-frontend:v1.0.0|g" k8s/frontend/deployment.yaml
```

**Images ready! ✅**

---

## Phase 5: Neon PostgreSQL Setup

### Step 1: Create Neon Database

**1. Sign up:**
- Go to: https://neon.tech
- Click **Sign Up** (free tier)

**2. Create project:**
- Project name: `todo-phase-v`
- Region: Choose closest to `nyc1` (e.g., US East - Ohio)
- Compute size: Free tier (0.25 vCPU)

**3. Create database:**
- Database name: `todo_db`
- Owner: Default user

**4. Copy connection string:**
```
postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/todo_db?sslmode=require
```

**Save this - you'll need it!**

### Step 2: Run Database Migrations

**Test connection locally:**
```bash
psql "<your-neon-connection-string>"
# Should connect successfully
\q  # quit
```

**Run migrations:**
```bash
cd backend

# Set environment variable
export DATABASE_URL="<your-neon-connection-string>"

# Run migrations
python run_migrations.py
```

**Verify tables created:**
```bash
psql "<your-neon-connection-string>" -c "\dt"
```

**Expected output:**
```
 public | tasks              | table | user
 public | saved_searches     | table | user
 public | task_templates     | table | user
 public | time_entries       | table | user
 public | conversations      | table | user
 public | messages           | table | user
```

**Database ready! ✅**

---

## Phase 6: Install Dapr on DOKS

### Step 1: Install Dapr CLI (if not already)

```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```

**Verify:**
```bash
dapr version
```

### Step 2: Initialize Dapr on Kubernetes

```bash
dapr init -k --wait --timeout 600
```

**This will:**
- Install Dapr control plane in `dapr-system` namespace
- Install Dapr Operator, Sidecar Injector, Placement, Sentry

**Verify Dapr installation:**
```bash
dapr status -k
```

**Expected output:**
```
  NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
  dapr-sentry            dapr-system  True     Running  1         1.16.5   30s  2025-12-25 10:00.00
  dapr-operator          dapr-system  True     Running  1         1.16.5   30s  2025-12-25 10:00.00
  dapr-sidecar-injector  dapr-system  True     Running  1         1.16.5   30s  2025-12-25 10:00.00
  dapr-placement-server  dapr-system  True     Running  1         1.16.5   30s  2025-12-25 10:00.00
```

**Dapr ready! ✅**

---

## Phase 7: Create Kubernetes Secrets

**Create all required secrets:**

```bash
# 1. Redpanda Cloud credentials
kubectl create secret generic kafka-secrets \
  --from-literal=username='todo-user' \
  --from-literal=password='<REDPANDA_PASSWORD>' \
  --namespace=todo-app

# 2. Neon database URL
kubectl create secret generic db-secrets \
  --from-literal=databaseUrl='<YOUR_NEON_CONNECTION_STRING>' \
  --namespace=todo-app

# 3. API secrets
kubectl create secret generic api-secrets \
  --from-literal=betterAuthSecret='<GENERATE_RANDOM_SECRET>' \
  --from-literal=openaiApiKey='<YOUR_OPENAI_API_KEY>' \
  --namespace=todo-app
```

**Generate random secret for Better Auth:**
```bash
openssl rand -hex 32
```

**Verify secrets created:**
```bash
kubectl get secrets -n todo-app
```

**Secrets ready! ✅**

---

## Phase 8: Deploy Dapr Components

**Apply all Dapr components:**

```bash
cd /home/riaz/Desktop/todo\ hackathon\ II/todo

# 1. Dapr configuration (no mTLS for dev)
kubectl apply -f k8s/dapr-components/config-no-mtls.yaml

# 2. State store (PostgreSQL - Neon)
kubectl apply -f k8s/dapr-components/state-postgresql.yaml

# 3. Secrets store (Kubernetes)
kubectl apply -f k8s/dapr-components/secrets-kubernetes.yaml

# 4. Pub/Sub (Kafka - Redpanda Cloud)
kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml

# 5. Cron binding (for reminders)
kubectl apply -f k8s/dapr-components/bindings-cron.yaml
```

**Verify components:**
```bash
kubectl get components -n todo-app
```

**Expected output:**
```
NAME                  AGE
kafka-pubsub          10s
statestore            10s
kubernetes-secrets    10s
reminder-cron         10s
```

**Components ready! ✅**

---

## Phase 9: Deploy Application Services

**Deploy all services:**

```bash
# 1. Backend service
kubectl apply -f k8s/backend/deployment.yaml -n todo-app

# 2. Notification service
kubectl apply -f k8s/notification-service/deployment.yaml -n todo-app

# 3. Audit service
kubectl apply -f k8s/audit-service/deployment.yaml -n todo-app

# 4. Frontend (if exists)
kubectl apply -f k8s/frontend/deployment.yaml -n todo-app
```

**Wait for pods to be running:**
```bash
kubectl get pods -n todo-app -w
# Press Ctrl+C when all show 2/2 READY
```

**Expected output:**
```
NAME                                  READY   STATUS    RESTARTS   AGE
backend-service-xxxxx                 2/2     Running   0          60s
backend-service-yyyyy                 2/2     Running   0          60s
notification-service-zzzzz            2/2     Running   0          60s
audit-service-wwwww                   2/2     Running   0          60s
```

**Check logs to verify Redpanda connection:**
```bash
# Check backend Dapr logs for Kafka connection
kubectl logs -l app=backend -c daprd -n todo-app --tail=50 | grep -i kafka
```

**You should see:**
```
INFO[0000] connected to Kafka broker: d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
```

**Services deployed! ✅**

---

## Phase 10: Set Up Load Balancer & Ingress

### DOKS automatically creates a Load Balancer!

**Apply backend service (LoadBalancer type):**
```bash
kubectl apply -f k8s/backend/service.yaml -n todo-app
```

**Wait for external IP:**
```bash
kubectl get svc backend-service -n todo-app -w
```

**Expected output:**
```
NAME              TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)          AGE
backend-service   LoadBalancer   10.245.xxx.xxx   xxx.xxx.xxx.xxx  8000:30xxx/TCP   2m
```

**Copy the EXTERNAL-IP** - this is your public backend URL!

**Test access:**
```bash
curl http://<EXTERNAL-IP>:8000/health
```

**Expected response:**
```json
{"status": "healthy", "version": "3.0.0-dev", "ai_enabled": true}
```

**Load balancer ready! ✅**

---

## Phase 11: Testing

### Test 1: Health Check
```bash
export BACKEND_URL="http://<EXTERNAL-IP>:8000"
curl $BACKEND_URL/health
```

### Test 2: Create Task (requires auth token)
```bash
# Get auth token first (from your frontend or Better Auth)
export AUTH_TOKEN="<your-jwt-token>"
export USER_ID="<your-user-id>"

curl -X POST $BACKEND_URL/api/$USER_ID/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d '{
    "title": "Test Cloud Deployment",
    "description": "Testing Phase V on DigitalOcean DOKS"
  }'
```

### Test 3: Verify Kafka Event Published
```bash
# Check backend Dapr logs
kubectl logs -l app=backend -c daprd -n todo-app --tail=100 | grep -i "published"
```

### Test 4: Verify Event Consumed by Audit Service
```bash
# Check audit service logs
kubectl logs -l app=audit -c audit -n todo-app --tail=50
```

### Test 5: Check Database
```bash
psql "<your-neon-connection-string>" -c "SELECT * FROM tasks;"
```

**All tests passing! ✅**

---

## Phase 12: Set Up CI/CD (GitHub Actions)

### Step 1: Create GitHub Secrets

**Go to your GitHub repo → Settings → Secrets and Variables → Actions**

**Add these secrets:**
1. `DIGITALOCEAN_ACCESS_TOKEN` - Your DO API token
2. `DOCKER_USERNAME` - Docker Hub username
3. `DOCKER_PASSWORD` - Docker Hub access token
4. `NEON_DATABASE_URL` - Neon connection string
5. `REDPANDA_USERNAME` - Redpanda username
6. `REDPANDA_PASSWORD` - Redpanda password
7. `OPENAI_API_KEY` - OpenAI API key

### Step 2: Create Workflow File

Create `.github/workflows/deploy-doks.yml` (I'll create this for you in next step)

---

## Summary of What's Running

```
DigitalOcean Kubernetes (DOKS)
├── Cluster: todo-phase-v (2 nodes, auto-scaling)
├── Dapr: v1.16.5 in dapr-system namespace
└── todo-app namespace:
    ├── backend-service (2 replicas)
    ├── notification-service (1 replica)
    ├── audit-service (1 replica)
    └── Dapr Components:
        ├── kafka-pubsub → Redpanda Cloud ✅
        ├── statestore → Neon PostgreSQL ✅
        ├── secrets → Kubernetes Secrets ✅
        └── reminder-cron → Cron binding ✅
```

**External Services:**
- **Neon DB**: Cloud PostgreSQL with all tables migrated
- **Redpanda Cloud**: Event streaming (Kafka) - WORKING! 🎉
- **DigitalOcean LoadBalancer**: Public IP for backend API

---

## Next Steps

1. ✅ Create GitHub Actions workflow for CI/CD
2. ✅ Set up monitoring (optional)
3. ✅ Configure custom domain (optional)
4. ✅ Enable TLS/SSL (optional but recommended)
5. ✅ Test end-to-end user flow

---

## Cost Breakdown

**Monthly Cost (without credit):**
- 2 x s-2vcpu-4gb nodes: $36/month
- Load Balancer: $12/month
- **Total**: $48/month

**With $200 credit**: FREE for ~4 months! 🎉

**External services (free tiers):**
- Neon DB: Free (3GB storage)
- Redpanda Cloud: Free serverless tier
- Docker Hub: Free (public images)

---

**Status**: Ready to execute deployment!
**Next**: Let me know when you're ready to start each phase, and I'll guide you through the commands.
