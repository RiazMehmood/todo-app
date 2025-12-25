# Phase V: Cloud-Native Deployment Specification

**Feature**: `005-cloud-native-deployment` - Phase V Cloud Deployment
**Branch**: `005-cloud-native-deployment`
**Date**: 2025-12-25
**Status**: Planning

## Overview

Deploy the Todo application with full event-driven architecture (Kafka/Dapr) to a production-grade cloud Kubernetes cluster (GKE/AKS/DOKS) with CI/CD, monitoring, and complete Redpanda Cloud integration.

## Current State

### ✅ Completed (Local - Minikube)
- All microservices deployed and running
- Dapr v1.16.5 installed and configured
- Local PostgreSQL working
- Backend API functional
- Dapr components configured (state, bindings, secrets)

### ❌ Blocked/Incomplete
- Kafka/Redpanda Cloud connection from Minikube (network isolation)
- Cloud Kubernetes deployment
- CI/CD pipeline
- Production database (Neon)
- Monitoring/logging infrastructure

## Objectives

### Part A: Advanced Features ✅ COMPLETE
All intermediate and advanced features implemented (Phases 1-6 from tasks.md).

### Part B: Local Deployment ✅ COMPLETE
Minikube deployment working (except Kafka - requires cloud).

### Part C: Cloud Deployment 🎯 **PRIMARY FOCUS**

Deploy to cloud Kubernetes with:
1. **Cloud Provider Setup** - GKE, AKS, or DOKS cluster
2. **Redpanda Cloud Integration** - Full event-driven architecture
3. **CI/CD Pipeline** - GitHub Actions for automated deployments
4. **Production Database** - Neon Serverless PostgreSQL
5. **Monitoring & Logging** - Observability stack
6. **Security** - Secrets management, TLS, RBAC

## Technology Stack

| Component | Technology | Status |
|-----------|------------|--------|
| Cloud Platform | GKE / AKS / DOKS | To be chosen |
| Kubernetes | Cloud-managed K8s | Pending |
| Event Streaming | Redpanda Cloud (Serverless) | Credentials ready |
| Database | Neon Serverless PostgreSQL | To be configured |
| Dapr | v1.16.5 | Ready |
| CI/CD | GitHub Actions | To be created |
| Container Registry | Docker Hub / GCR / ACR | To be setup |
| Monitoring | Prometheus + Grafana (optional) | TBD |
| Ingress | Cloud Load Balancer + Ingress | TBD |

## Cloud Provider Options

### Option 1: Google Cloud (GKE) ⭐ RECOMMENDED
**Pros:**
- $300 free credit (90 days)
- Excellent Kubernetes support (GKE Autopilot)
- Easy Dapr installation
- Good documentation

**Setup:**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Login and create project
gcloud auth login
gcloud projects create todo-phase-v --name="Todo Phase V"
gcloud config set project todo-phase-v

# Enable APIs
gcloud services enable container.googleapis.com

# Create GKE cluster
gcloud container clusters create todo-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=3
```

### Option 2: Microsoft Azure (AKS)
**Pros:**
- $200 free credit (30 days)
- Good Dapr integration (created by Microsoft)
- AKS free tier

**Setup:**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name todo-phase-v --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-phase-v \
  --name todo-cluster \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys
```

### Option 3: DigitalOcean (DOKS)
**Pros:**
- Simple and cost-effective
- Predictable pricing
- $200 credit (60 days)

**Setup:**
```bash
# Install doctl
snap install doctl

# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2"
```

### Option 4: Oracle Cloud (OKE) - Best for Long-term Free
**Pros:**
- Always Free tier (4 OCPUs, 24GB RAM)
- No credit card charge after trial
- Best for learning without time pressure

**Cons:**
- More complex setup
- Smaller community

## Redpanda Cloud Integration

### Current Credentials
- **Bootstrap Server**: `d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
- **SASL Mechanism**: SCRAM-SHA-256
- **Topics**: task-events, reminders, task-updates, recurring-tasks
- **Username/Password**: Already in k8s/secrets/secrets.yaml

### Alternative: Self-hosted Kafka Options
If Redpanda Cloud issues persist:

1. **Strimzi Operator** (In-cluster Kafka)
2. **Confluent Cloud** ($400 free credit)
3. **CloudKarafka** (Free "Developer Duck" tier)
4. **Aiven** ($300 trial credit)

## CI/CD Pipeline Requirements

### GitHub Actions Workflow
Create `.github/workflows/deploy-cloud.yml`:

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**Jobs:**
1. **Build** - Build and push Docker images
2. **Test** - Run tests (if any)
3. **Deploy to Staging** - Deploy to staging namespace
4. **Deploy to Production** - Manual approval required

### Secrets Required (GitHub)
- `CLOUD_CREDENTIALS` - GCP/Azure/DO credentials
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub token
- `REDPANDA_USERNAME` - Redpanda Cloud username
- `REDPANDA_PASSWORD` - Redpanda Cloud password
- `NEON_DATABASE_URL` - Neon connection string
- `OPENAI_API_KEY` - OpenAI API key

## Database Migration

### From Local PostgreSQL to Neon

**Current**: Local PostgreSQL in Minikube (ephemeral)
**Target**: Neon Serverless PostgreSQL (cloud-managed)

**Steps:**
1. Create Neon database
2. Run migrations against Neon
3. Update Kubernetes secrets with Neon connection string
4. Test connectivity from cloud cluster

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CLOUD KUBERNETES                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Frontend   │  │   Backend   │  │ Notification│    │
│  │  (Next.js)  │  │  (FastAPI)  │  │   Service   │    │
│  │ + Dapr      │  │  + Dapr     │  │  + Dapr     │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                 │            │
│         └────────────────┼─────────────────┘            │
│                          │                              │
│  ┌──────────────────────▼────────────────────────┐     │
│  │          DAPR COMPONENTS                      │     │
│  │  ┌─────────────┐  ┌──────────────────────┐   │     │
│  │  │   PubSub    │  │   State (PostgreSQL) │   │     │
│  │  │  (Kafka)    │  │   Secrets (K8s)      │   │     │
│  │  └─────────────┘  └──────────────────────┘   │     │
│  └────────┬──────────────────┬───────────────────┘     │
└───────────┼──────────────────┼─────────────────────────┘
            │                  │
    ┌───────▼────────┐  ┌──────▼────────┐
    │ Redpanda Cloud │  │  Neon DB      │
    │ (Kafka)        │  │ (PostgreSQL)  │
    └────────────────┘  └───────────────┘
```

## Non-Functional Requirements

### Performance
- API response time: < 200ms (p95)
- Event processing latency: < 100ms
- WebSocket broadcast: < 2 seconds

### Scalability
- Support horizontal pod autoscaling (HPA)
- Auto-scale 1-5 replicas based on CPU/memory
- Handle 100+ concurrent WebSocket connections

### Security
- TLS for all external traffic
- Kubernetes RBAC enabled
- Secrets encrypted at rest
- Network policies between services

### Availability
- 99.9% uptime target
- Rolling updates with zero downtime
- Health checks and readiness probes
- Graceful shutdown handling

## Acceptance Criteria

### ✅ Cloud Deployment Complete When:
1. [ ] Kubernetes cluster provisioned and accessible
2. [ ] All services deployed and running (2/2 replicas)
3. [ ] Dapr installed and all components working
4. [ ] Redpanda Cloud connected and publishing/consuming events
5. [ ] Neon database connected and migrations applied
6. [ ] CI/CD pipeline deploying on git push
7. [ ] Frontend accessible via public URL with TLS
8. [ ] Backend API accessible via public URL with TLS
9. [ ] Real-time features working (WebSocket, notifications)
10. [ ] Monitoring dashboard showing metrics
11. [ ] Zero downtime during rolling updates
12. [ ] End-to-end test passing (create task → event published → notification sent)

## Testing Strategy

### Manual Testing Checklist
1. **Basic CRUD** - Create, read, update, delete tasks via API
2. **Event Publishing** - Task created → event in Kafka
3. **Event Consumption** - Audit service logs event
4. **WebSocket** - Real-time task updates
5. **Notifications** - Due date reminder sent
6. **Database Persistence** - Data survives pod restart
7. **Scaling** - Scale to 5 replicas and back

### Load Testing (Optional)
- 100 concurrent users
- 1000 tasks created
- 500 events published/consumed
- Response time < 500ms

## Rollback Plan

If cloud deployment fails:
1. Keep Minikube deployment as fallback
2. Document all errors
3. Revert to local testing
4. Address issues and retry

## Cost Estimates

### GKE (Google Cloud)
- **Free Credit**: $300 (90 days)
- **Monthly Cost** (after credit):
  - 2 x e2-medium nodes: ~$50/month
  - Load balancer: ~$18/month
  - **Total**: ~$68/month

### AKS (Azure)
- **Free Credit**: $200 (30 days)
- **Monthly Cost** (after credit):
  - 2 x Standard_B2s nodes: ~$60/month
  - Load balancer: ~$20/month
  - **Total**: ~$80/month

### DOKS (DigitalOcean)
- **Free Credit**: $200 (60 days)
- **Monthly Cost** (after credit):
  - 2 x s-2vcpu-4gb nodes: ~$36/month
  - Load balancer: ~$12/month
  - **Total**: ~$48/month

### External Services
- **Neon DB**: Free tier (3GB storage)
- **Redpanda Cloud**: Free serverless tier
- **Docker Hub**: Free (public images)

**Estimated Total**: $0-$80/month depending on provider (free during trial period)

## Timeline

1. **Day 1**: Cloud provider setup + cluster creation (2-3 hours)
2. **Day 1**: Install Dapr + deploy services (2-3 hours)
3. **Day 2**: Redpanda Cloud integration + testing (3-4 hours)
4. **Day 2**: Neon database setup + migration (1-2 hours)
5. **Day 3**: CI/CD pipeline creation (2-3 hours)
6. **Day 3**: Monitoring setup (optional) (2-3 hours)
7. **Day 4**: End-to-end testing + documentation (3-4 hours)

**Total**: 3-4 days (15-20 hours)

## Dependencies

### Required Before Starting
- ✅ Minikube deployment working
- ✅ Kubernetes manifests ready
- ✅ Dapr components configured
- ✅ Redpanda Cloud credentials
- ⏳ Cloud provider account with credits
- ⏳ GitHub repository set up
- ⏳ Neon database created

### External Dependencies
- Cloud provider (GCP/Azure/DO)
- Redpanda Cloud availability
- Neon database availability
- Docker Hub availability

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Redpanda Cloud connection fails | Medium | High | Use alternative (Strimzi, Confluent) |
| Free credits exhausted | Low | Medium | Oracle Cloud Always Free tier |
| Database migration issues | Low | Medium | Test locally first, backup data |
| CI/CD pipeline breaks deployment | Medium | High | Manual rollback procedure |
| Services crash in production | Low | High | Health checks, auto-restart |

## Next Steps

1. **Choose cloud provider** (Recommend: GKE for best K8s experience)
2. **Create cloud account** and verify credits
3. **Generate deployment tasks** using `/sp.tasks`
4. **Execute deployment** following task checklist
5. **Test and validate** all acceptance criteria
6. **Document learnings** for future deployments

---

**Status**: Ready for task generation and implementation
**Estimated Effort**: 15-20 hours over 3-4 days
**Success Rate**: High (all prerequisites met)
