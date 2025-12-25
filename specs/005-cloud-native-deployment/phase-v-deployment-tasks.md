# Phase V: Cloud Deployment Tasks

**Input**: phase-v-cloud-deployment-spec.md
**Prerequisites**: Minikube deployment working, Kubernetes manifests ready
**Tests**: End-to-end cloud deployment validation

---

## Cloud Provider Decision

**Before starting**: Choose ONE cloud provider based on your preference:

| Provider | Best For | Credit | Duration |
|----------|----------|--------|----------|
| **Google Cloud (GKE)** | Best K8s experience, excellent docs | $300 | 90 days |
| **Azure (AKS)** | Dapr integration (Microsoft product) | $200 | 30 days |
| **DigitalOcean (DOKS)** | Simplicity, lower cost | $200 | 60 days |
| **Oracle Cloud (OKE)** | Always Free tier (no expiry) | Free forever | Unlimited |

**Recommendation**: Start with **Google Cloud (GKE)** for best experience, or **Oracle Cloud** for long-term free usage.

---

## Phase 1: Cloud Infrastructure Setup (Prerequisites)

**Purpose**: Set up cloud provider account and provision Kubernetes cluster

### Cloud Provider Setup

- [ ] **CD001**: Choose cloud provider (GKE/AKS/DOKS/OKE)
- [ ] **CD002**: Create cloud provider account
- [ ] **CD003**: Verify free credits available
- [ ] **CD004**: Install cloud CLI tool (gcloud/az/doctl)
- [ ] **CD005**: Authenticate with cloud provider
- [ ] **CD006**: Create project/resource group

### Kubernetes Cluster Creation

- [ ] **CD007**: Create Kubernetes cluster (2-3 nodes, auto-scaling)
  - **GKE**: `gcloud container clusters create todo-cluster --zone=us-central1-a --num-nodes=2`
  - **AKS**: `az aks create --resource-group todo-phase-v --name todo-cluster --node-count 2`
  - **DOKS**: `doctl kubernetes cluster create todo-cluster --node-pool "size=s-2vcpu-4gb;count=2"`
- [ ] **CD008**: Get cluster credentials: `kubectl config use-context <cluster-name>`
- [ ] **CD009**: Verify cluster access: `kubectl get nodes`
- [ ] **CD010**: Create namespace: `kubectl create namespace todo-app`

**Checkpoint**: Cluster running and accessible via kubectl

---

## Phase 2: Container Registry & Image Publishing

**Purpose**: Build and push Docker images to registry

### Container Registry Setup

- [ ] **CD011**: Choose container registry (Docker Hub/GCR/ACR/DOCR)
- [ ] **CD012**: Create registry account (if not using Docker Hub)
- [ ] **CD013**: Login to registry: `docker login`

### Build and Push Images

- [ ] **CD014**: Build backend image: `docker build -t <registry>/todo-backend:v1 ./backend`
- [ ] **CD015**: Build frontend image: `docker build -t <registry>/todo-frontend:v1 ./frontend`
- [ ] **CD016**: Build notification service: `docker build -t <registry>/todo-notification:v1 ./notification-service`
- [ ] **CD017**: Build audit service: `docker build -t <registry>/todo-audit:v1 ./audit-service`
- [ ] **CD018**: Push all images to registry
- [ ] **CD019**: Update deployment YAML files with registry image paths
- [ ] **CD020**: Verify images pulled successfully: `docker pull <registry>/todo-backend:v1`

**Checkpoint**: All images available in container registry

---

## Phase 3: Dapr Installation & Configuration

**Purpose**: Install Dapr on cloud cluster and configure components

### Install Dapr

- [ ] **CD021**: Install Dapr CLI (if not already): `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash`
- [ ] **CD022**: Initialize Dapr on Kubernetes: `dapr init -k --wait`
- [ ] **CD023**: Verify Dapr installation: `dapr status -k`
- [ ] **CD024**: Check Dapr components running in `dapr-system` namespace

### Configure Dapr Components

- [ ] **CD025**: Create Kubernetes secrets for sensitive data:
  ```bash
  kubectl create secret generic kafka-secrets \
    --from-literal=username='<REDPANDA_USERNAME>' \
    --from-literal=password='<REDPANDA_PASSWORD>' \
    --namespace=todo-app

  kubectl create secret generic db-secrets \
    --from-literal=databaseUrl='<NEON_DATABASE_URL>' \
    --namespace=todo-app

  kubectl create secret generic api-secrets \
    --from-literal=betterAuthSecret='<BETTER_AUTH_SECRET>' \
    --from-literal=openaiApiKey='<OPENAI_API_KEY>' \
    --namespace=todo-app
  ```

- [ ] **CD026**: Apply Dapr state component (PostgreSQL): `kubectl apply -f k8s/dapr-components/state-postgresql.yaml`
- [ ] **CD027**: Apply Dapr pubsub component (Kafka/Redpanda): `kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml`
- [ ] **CD028**: Apply Dapr secrets component: `kubectl apply -f k8s/dapr-components/secrets-kubernetes.yaml`
- [ ] **CD029**: Apply Dapr cron binding: `kubectl apply -f k8s/dapr-components/bindings-cron.yaml`
- [ ] **CD030**: Apply Dapr configuration: `kubectl apply -f k8s/dapr-components/config-no-mtls.yaml`
- [ ] **CD031**: Verify components: `kubectl get components -n todo-app`

**Checkpoint**: Dapr running with all components configured

---

## Phase 4: Database Setup (Neon PostgreSQL)

**Purpose**: Create and configure cloud PostgreSQL database

### Neon Database Creation

- [ ] **CD032**: Sign up for Neon (neon.tech) - Free tier
- [ ] **CD033**: Create new project: "todo-phase-v"
- [ ] **CD034**: Create database: "todo_db"
- [ ] **CD035**: Copy connection string
- [ ] **CD036**: Update Kubernetes secret with Neon URL:
  ```bash
  kubectl create secret generic db-secrets \
    --from-literal=databaseUrl='postgresql://user:pass@host.neon.tech/todo_db?sslmode=require' \
    --namespace=todo-app \
    --dry-run=client -o yaml | kubectl apply -f -
  ```

### Run Database Migrations

- [ ] **CD037**: Test connection from local machine: `psql "<NEON_CONNECTION_STRING>"`
- [ ] **CD038**: Run migrations: `python backend/run_migrations.py` (pointing to Neon)
- [ ] **CD039**: Verify tables created: `\dt` in psql
- [ ] **CD040**: Create test data (optional)

**Checkpoint**: Neon database ready with schema

---

## Phase 5: Redpanda Cloud Integration

**Purpose**: Connect Dapr pubsub to Redpanda Cloud

### Redpanda Cloud Setup

- [ ] **CD041**: Sign up for Redpanda Cloud (redpanda.com/cloud) - Free serverless tier
- [ ] **CD042**: Create serverless cluster (if not already exists)
- [ ] **CD043**: Note bootstrap server URL (already have: `d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`)
- [ ] **CD044**: Create topics:
  - `task-events`
  - `reminders`
  - `task-updates`
  - `recurring-tasks`
- [ ] **CD045**: Create SCRAM user credentials (username/password)
- [ ] **CD046**: Test connection from local machine:
  ```bash
  rpk topic list --brokers <bootstrap-server> \
    --sasl-mechanism SCRAM-SHA-256 \
    --user <username> --password <password> --tls-enabled
  ```

### Update Kafka Component

- [ ] **CD047**: Update `k8s/dapr-components/pubsub-kafka.yaml` with correct bootstrap server
- [ ] **CD048**: Apply updated component: `kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml`
- [ ] **CD049**: Check Dapr logs for Kafka connection success:
  ```bash
  kubectl logs -l app.kubernetes.io/name=dapr -n dapr-system | grep -i kafka
  ```

**Checkpoint**: Redpanda Cloud connected from cluster

---

## Phase 6: Deploy Application Services

**Purpose**: Deploy all microservices to cloud cluster

### Deploy Backend Services

- [ ] **CD050**: Apply backend deployment: `kubectl apply -f k8s/backend/deployment.yaml -n todo-app`
- [ ] **CD051**: Apply backend service: `kubectl apply -f k8s/backend/service.yaml -n todo-app`
- [ ] **CD052**: Verify backend pods running: `kubectl get pods -l app=backend -n todo-app`
- [ ] **CD053**: Check backend logs: `kubectl logs -l app=backend -c backend -n todo-app --tail=50`
- [ ] **CD054**: Check Dapr sidecar logs: `kubectl logs -l app=backend -c daprd -n todo-app --tail=50`

### Deploy Supporting Services

- [ ] **CD055**: Apply notification service: `kubectl apply -f k8s/notification-service/deployment.yaml -n todo-app`
- [ ] **CD056**: Apply audit service: `kubectl apply -f k8s/audit-service/deployment.yaml -n todo-app`
- [ ] **CD057**: Verify all services running: `kubectl get pods -n todo-app`

### Deploy Frontend (if applicable)

- [ ] **CD058**: Apply frontend deployment: `kubectl apply -f k8s/frontend/deployment.yaml -n todo-app`
- [ ] **CD059**: Apply frontend service: `kubectl apply -f k8s/frontend/service.yaml -n todo-app`
- [ ] **CD060**: Verify frontend running: `kubectl get pods -l app=frontend -n todo-app`

**Checkpoint**: All services running with 2/2 replicas

---

## Phase 7: Ingress & External Access

**Purpose**: Expose services to the internet with load balancer

### Set Up Ingress

- [ ] **CD061**: Install ingress controller (if not pre-installed):
  - **GKE**: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml`
  - **AKS**: Use Azure Application Gateway
  - **DOKS**: Automatically included

- [ ] **CD062**: Wait for load balancer IP: `kubectl get svc -n ingress-nginx`
- [ ] **CD063**: Note external IP address
- [ ] **CD064**: Apply ingress resource: `kubectl apply -f k8s/ingress.yaml -n todo-app`
- [ ] **CD065**: Verify ingress created: `kubectl get ingress -n todo-app`

### Configure DNS (Optional)

- [ ] **CD066**: Register domain (if you have one)
- [ ] **CD067**: Create A record pointing to load balancer IP
- [ ] **CD068**: Wait for DNS propagation
- [ ] **CD069**: Test access: `curl http://<your-domain>/health`

### Configure TLS (Optional but Recommended)

- [ ] **CD070**: Install cert-manager: `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml`
- [ ] **CD071**: Create ClusterIssuer for Let's Encrypt
- [ ] **CD072**: Update ingress with TLS annotation
- [ ] **CD073**: Verify certificate issued: `kubectl get certificate -n todo-app`

**Checkpoint**: Application accessible via public URL

---

## Phase 8: CI/CD Pipeline (GitHub Actions)

**Purpose**: Automate deployments on git push

### Create GitHub Secrets

- [ ] **CD074**: Go to GitHub repo → Settings → Secrets and Variables → Actions
- [ ] **CD075**: Add secrets:
  - `CLOUD_PROVIDER_CREDENTIALS` - Service account key (JSON for GCP, credential string for others)
  - `DOCKER_USERNAME` - Docker Hub username
  - `DOCKER_PASSWORD` - Docker Hub token
  - `REDPANDA_USERNAME` - Redpanda Cloud username
  - `REDPANDA_PASSWORD` - Redpanda Cloud password
  - `NEON_DATABASE_URL` - Neon connection string
  - `OPENAI_API_KEY` - OpenAI API key
  - `BETTER_AUTH_SECRET` - Better Auth secret

### Create Workflow File

- [ ] **CD076**: Create `.github/workflows/deploy-cloud.yml`
- [ ] **CD077**: Add build job (build Docker images)
- [ ] **CD078**: Add push job (push to registry)
- [ ] **CD079**: Add deploy job (apply kubectl manifests)
- [ ] **CD080**: Test workflow with manual trigger
- [ ] **CD081**: Commit and push workflow file
- [ ] **CD082**: Verify GitHub Actions runs successfully

**Checkpoint**: CI/CD pipeline deploying on push

---

## Phase 9: Testing & Validation

**Purpose**: Verify complete end-to-end functionality

### Functional Testing

- [ ] **CD083**: Test backend health: `curl https://<your-url>/health`
- [ ] **CD084**: Create a task via API:
  ```bash
  curl -X POST https://<your-url>/api/<user_id>/tasks \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer <token>" \
    -d '{"title": "Test Cloud Task", "description": "Testing Phase V deployment"}'
  ```
- [ ] **CD085**: Verify task stored in Neon database
- [ ] **CD086**: Check Kafka event published:
  ```bash
  kubectl logs -l app=backend -c daprd -n todo-app | grep -i "published"
  ```
- [ ] **CD087**: Verify audit service consumed event:
  ```bash
  kubectl logs -l app=audit -c audit -n todo-app | grep -i "received"
  ```
- [ ] **CD088**: Test WebSocket connection (if implemented)
- [ ] **CD089**: Test notification service (if implemented)

### Performance Testing

- [ ] **CD090**: Run load test (100 concurrent requests)
- [ ] **CD091**: Verify response time < 500ms
- [ ] **CD092**: Check pod auto-scaling triggers
- [ ] **CD093**: Monitor resource usage: `kubectl top pods -n todo-app`

### Resilience Testing

- [ ] **CD094**: Delete a backend pod: `kubectl delete pod <pod-name> -n todo-app`
- [ ] **CD095**: Verify automatic restart
- [ ] **CD096**: Test rolling update: change image tag and apply
- [ ] **CD097**: Verify zero downtime during update

**Checkpoint**: All tests passing, system stable

---

## Phase 10: Monitoring & Observability (Optional)

**Purpose**: Set up monitoring dashboard

### Metrics Collection

- [ ] **CD098**: Install Prometheus: `helm install prometheus prometheus-community/prometheus`
- [ ] **CD099**: Install Grafana: `helm install grafana grafana/grafana`
- [ ] **CD100**: Get Grafana password: `kubectl get secret grafana -o jsonpath="{.data.admin-password}" | base64 --decode`
- [ ] **CD101**: Port-forward Grafana: `kubectl port-forward svc/grafana 3000:80`
- [ ] **CD102**: Access Grafana: `http://localhost:3000`
- [ ] **CD103**: Add Prometheus data source
- [ ] **CD104**: Import Kubernetes dashboard (ID: 6417)

### Log Aggregation (Optional)

- [ ] **CD105**: Install Loki: `helm install loki grafana/loki-stack`
- [ ] **CD106**: Add Loki data source to Grafana
- [ ] **CD107**: Query logs from all services

**Checkpoint**: Monitoring dashboard showing metrics

---

## Phase 11: Documentation & Cleanup

**Purpose**: Document deployment and clean up temporary resources

### Documentation

- [ ] **CD108**: Update README.md with:
  - Cloud deployment instructions
  - Environment variables required
  - How to run CI/CD
  - Monitoring access
- [ ] **CD109**: Create architecture diagram (cloud version)
- [ ] **CD110**: Document Redpanda topic structure
- [ ] **CD111**: Create runbook for common operations:
  - Scaling pods
  - Viewing logs
  - Rolling updates
  - Rollback procedure

### Cleanup (After Testing)

- [ ] **CD112**: Delete test resources (if any)
- [ ] **CD113**: Verify no unused persistent volumes
- [ ] **CD114**: Check for orphaned load balancers
- [ ] **CD115**: Review cloud provider billing dashboard
- [ ] **CD116**: Set up budget alerts

**Checkpoint**: Documentation complete, no wasteful resources

---

## Final Acceptance Checklist

Deployment is **COMPLETE** when ALL of these are ✅:

- [ ] ✅ Kubernetes cluster running in cloud (GKE/AKS/DOKS)
- [ ] ✅ Dapr installed and all components working
- [ ] ✅ All services deployed with 2/2 replicas
- [ ] ✅ Neon PostgreSQL connected and migrations applied
- [ ] ✅ Redpanda Cloud connected and events flowing
- [ ] ✅ Backend API accessible via public URL
- [ ] ✅ Frontend accessible via public URL (if deployed)
- [ ] ✅ CI/CD pipeline deploying on git push
- [ ] ✅ TLS enabled (optional but recommended)
- [ ] ✅ End-to-end test passing (create task → event published → consumed)
- [ ] ✅ Zero downtime during rolling updates
- [ ] ✅ Monitoring dashboard showing metrics (optional)
- [ ] ✅ Documentation updated

---

## Troubleshooting Guide

### Common Issues

**1. Pods stuck in `Pending` state**
```bash
kubectl describe pod <pod-name> -n todo-app
# Check for: insufficient CPU/memory, image pull errors
```

**2. Cannot connect to Redpanda Cloud**
```bash
kubectl logs -l app=backend -c daprd -n todo-app | grep -i kafka
# Check: credentials, firewall rules, topic names
```

**3. Database connection failures**
```bash
kubectl exec -it <backend-pod> -n todo-app -c backend -- env | grep DATABASE
# Verify: connection string format, SSL mode, Neon IP whitelist
```

**4. CI/CD pipeline fails**
- Check GitHub Actions logs
- Verify all secrets are set correctly
- Test kubectl commands locally first

**5. 502 Bad Gateway from Ingress**
```bash
kubectl get pods -n todo-app
kubectl logs -l app=backend -n todo-app
# Check: pod health, readiness probes
```

---

## Estimated Timeline

| Phase | Tasks | Time | Cumulative |
|-------|-------|------|------------|
| 1. Cloud Setup | CD001-CD010 | 1-2h | 2h |
| 2. Container Registry | CD011-CD020 | 1-2h | 4h |
| 3. Dapr Setup | CD021-CD031 | 1-2h | 6h |
| 4. Database | CD032-CD040 | 1h | 7h |
| 5. Redpanda | CD041-CD049 | 1-2h | 9h |
| 6. Deploy Services | CD050-CD060 | 1h | 10h |
| 7. Ingress/TLS | CD061-CD073 | 2-3h | 13h |
| 8. CI/CD | CD074-CD082 | 2-3h | 16h |
| 9. Testing | CD083-CD097 | 2h | 18h |
| 10. Monitoring | CD098-CD107 | 2h (opt) | 20h |
| 11. Docs | CD108-CD116 | 1h | 21h |

**Total**: 15-21 hours over 3-4 days

---

## Dependencies

**Must have before starting:**
- ✅ Minikube deployment working (reference)
- ✅ Kubernetes manifests ready
- ✅ Dapr components defined
- ⏳ Cloud provider account
- ⏳ Credit card for cloud signup (no charge during trial)
- ⏳ GitHub repository
- ⏳ Docker Hub account

**External services needed:**
- Cloud provider (GCP/Azure/DO/Oracle)
- Neon database account
- Redpanda Cloud account
- Docker Hub (or GCR/ACR)

---

**Status**: Ready for execution
**Next Step**: Choose cloud provider and start CD001

Good luck with your cloud deployment! 🚀
