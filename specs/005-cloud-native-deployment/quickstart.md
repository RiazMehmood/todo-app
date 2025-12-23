# Quickstart: Redpanda Cloud Integration Deployment

**Target Audience**: Developers deploying the complete Todo app with Kafka event streaming
**Prerequisites**: Minikube running, Dapr installed, Redpanda Cloud configured
**Time to Complete**: ~15 minutes

## Overview

This guide walks through deploying the complete event-driven Todo application stack:
1. Verify prerequisites
2. Create Kubernetes secrets
3. Build Docker images
4. Deploy all services
5. Test event flow end-to-end
6. Monitor via Redpanda Cloud console

## Prerequisites Checklist

Before starting, ensure you have completed:

- ✅ **Minikube**: Running and accessible (`minikube status`)
- ✅ **Dapr**: Installed in cluster (`kubectl get pods -n dapr-system`)
- ✅ **Redpanda Cloud**: Cluster created, topics configured (Steps 1-8 of `docs/REDPANDA_SETUP.md`)
- ✅ **Dapr Components**: Deployed (`kubectl get components` shows kafka-pubsub)
- ✅ **Database**: Neon PostgreSQL connection string available

**Verify Prerequisites**:
```bash
# 1. Check Minikube
minikube status
# Expected: host/kubelet/apiserver Running

# 2. Check Dapr
kubectl get pods -n dapr-system
# Expected: All pods Running (2/2)

# 3. Check Dapr components
kubectl get components
# Expected: kafka-pubsub, statestore, reminder-cron

# 4. Check Redpanda topics (optional - via web console)
# Navigate to: Redpanda Cloud → Topics
# Expected: task-events, reminders, task-updates, recurring-tasks
```

---

## Step 1: Create Kubernetes Secrets

### 1.1 Database Secret

Create secret with Neon PostgreSQL connection string:

```bash
kubectl create secret generic db-secrets \
  --from-literal=databaseUrl='postgresql://user:password@host.neon.tech/dbname?sslmode=require'
```

**Replace** with your actual Neon connection string from `.env` file.

**Verify**:
```bash
kubectl get secret db-secrets
kubectl describe secret db-secrets
# Should show: databaseUrl (72 bytes or similar)
```

### 1.2 API Secret

Create secret with Better Auth JWT signing key:

```bash
kubectl create secret generic api-secrets \
  --from-literal=betterAuthSecret='your-32-character-secret-key'
```

**Replace** with your actual secret from `.env` (`BETTER_AUTH_SECRET`).

**Verify**:
```bash
kubectl get secret api-secrets
```

### 1.3 Email Secret (Optional)

For notification service (can be dummy value for now):

```bash
kubectl create secret generic email-secrets \
  --from-literal=sendgridApiKey='placeholder-key'
```

**Note**: Email notifications are disabled by default (`EMAIL_ENABLED=false` in deployment).

### 1.4 Kafka Secret (Already Created)

Verify Redpanda credentials secret exists:

```bash
kubectl get secret kafka-secrets
# Should show: username, password, bootstrapServer
```

**If missing**, recreate from REDPANDA_SETUP.md Step 6.

---

## Step 2: Build Docker Images

### 2.1 Configure Minikube Docker Daemon

Point Docker CLI to Minikube's Docker daemon (so images are accessible):

```bash
eval $(minikube docker-env)

# Verify
docker ps | head -5
# Should show Kubernetes/Minikube containers
```

**Important**: This command only affects the current terminal session. Rerun if you open a new terminal.

### 2.2 Build Backend Image

```bash
cd /path/to/todo/backend
docker build -t todo-backend:latest .
```

**Verify**:
```bash
docker images | grep todo-backend
# todo-backend   latest   abc123def456   2 minutes ago   500MB
```

### 2.3 Build Notification Service Image

```bash
cd /path/to/todo/services/notification-service
docker build -t todo-notification:latest .
```

**Verify**:
```bash
docker images | grep todo-notification
# todo-notification   latest   def456ghi789   1 minute ago   200MB
```

### 2.4 Build Audit Service Image

```bash
cd /path/to/todo/services/audit-service
docker build -t todo-audit:latest .
```

**Verify**:
```bash
docker images | grep todo-audit
# todo-audit   latest   ghi789jkl012   1 minute ago   220MB
```

**Troubleshooting**:
- **Build fails**: Check Dockerfile exists, dependencies installable
- **Image too large**: Use multi-stage builds (already implemented)
- **Permission denied**: Run `chmod +x` on scripts if needed

---

## Step 3: Deploy Services to Kubernetes

### 3.1 Deploy Backend Service

```bash
cd /path/to/todo
kubectl apply -f k8s/backend/deployment.yaml
```

**Wait for deployment**:
```bash
kubectl rollout status deployment/backend-service
# Waiting for deployment "backend-service" rollout to finish...
# deployment "backend-service" successfully rolled out
```

**Verify**:
```bash
kubectl get pods -l app=backend
# NAME                              READY   STATUS    RESTARTS   AGE
# backend-service-abc123-xyz        2/2     Running   0          30s
# backend-service-def456-uvw        2/2     Running   0          30s
```

**Note**: `2/2` means both app container and Dapr sidecar are running.

### 3.2 Deploy Notification Service

```bash
kubectl apply -f k8s/notification-service/deployment.yaml
```

**Verify**:
```bash
kubectl get pods -l app=notification
# NAME                                    READY   STATUS    RESTARTS   AGE
# notification-service-abc123-xyz         2/2     Running   0          20s
```

### 3.3 Deploy Audit Service

```bash
kubectl apply -f k8s/audit-service/deployment.yaml
```

**Verify**:
```bash
kubectl get pods -l app=audit
# NAME                              READY   STATUS    RESTARTS   AGE
# audit-service-abc123-xyz          2/2     Running   0          20s
```

### 3.4 Verify All Services

```bash
kubectl get pods
```

**Expected output**:
```
NAME                                    READY   STATUS    RESTARTS   AGE
backend-service-abc123-xyz              2/2     Running   0          2m
backend-service-def456-uvw              2/2     Running   0          2m
notification-service-abc123-xyz         2/2     Running   0          1m
audit-service-abc123-xyz                2/2     Running   0          1m
```

**Troubleshooting**:
| Status | Cause | Fix |
|--------|-------|-----|
| ImagePullBackOff | Image not found | Rebuild image with `eval $(minikube docker-env)` |
| CrashLoopBackOff | Container crashing | Check logs: `kubectl logs <pod-name> -c <container-name>` |
| 0/2 Running | Container not starting | Check events: `kubectl describe pod <pod-name>` |
| CreateContainerConfigError | Secret missing | Verify secrets exist: `kubectl get secrets` |

---

## Step 4: Test Event Flow End-to-End

### 4.1 Port-Forward Backend Service

Open backend API for local access:

```bash
kubectl port-forward service/backend-service 8000:8000
```

**Keep this terminal open**. Open a new terminal for testing.

### 4.2 Create Test Task

**Get Auth Token** (from your frontend or login flow):
```bash
export AUTH_TOKEN="your-jwt-token-here"
export USER_ID="your-user-id"
```

**Create a task**:
```bash
curl -X POST http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Kafka Integration",
    "description": "Verify events flow to Redpanda",
    "priority": "high",
    "tags": ["testing", "kafka"],
    "due_date": "2025-12-30T10:00:00Z",
    "remind_before_minutes": 30
  }'
```

**Expected response**:
```json
{
  "id": 42,
  "user_id": "user123",
  "title": "Test Kafka Integration",
  "completed": false,
  ...
}
```

### 4.3 Verify Backend Published Event

```bash
kubectl logs deployment/backend-service -c backend --tail=20 | grep "Published event"
```

**Expected output**:
```
2025-12-22 12:00:00 INFO Published event to task-events: created
```

**If not found**:
- Check `KAFKA_ENABLED` is true: `kubectl describe deployment backend-service | grep KAFKA_ENABLED`
- Check Dapr sidecar logs: `kubectl logs deployment/backend-service -c daprd | grep publish`

### 4.4 Verify Redpanda Received Event

1. Open **Redpanda Cloud Console** (https://cloud.redpanda.com)
2. Navigate to: **Topics** → **task-events**
3. Click **Messages** tab
4. **Expected**: New message with:
   - `event_type`: "created"
   - `task_id`: 42
   - `task_data`: Full task object

**Screenshot Expected**:
```
Messages (1)
┌─────────────────────────────────────────────┐
│ Offset: 123                                 │
│ Partition: 0                                │
│ Timestamp: 2025-12-22 12:00:00              │
│ Key: user123                                │
│ Value:                                      │
│ {                                           │
│   "event_type": "created",                  │
│   "task_id": 42,                            │
│   ...                                       │
│ }                                           │
└─────────────────────────────────────────────┘
```

### 4.5 Verify Audit Service Consumed Event

```bash
kubectl logs deployment/audit-service -c audit --tail=20 | grep "Received event"
```

**Expected output**:
```
2025-12-22 12:00:01 INFO Received event: created for task_id=42
2025-12-22 12:00:01 INFO Saved audit log to database
```

**If not found**:
- Check Dapr subscription logs: `kubectl logs deployment/audit-service -c daprd | grep subscribe`
- Check Dapr component: `kubectl get component kafka-pubsub -o yaml`

### 4.6 Verify Audit Database Record

Port-forward audit service API:

```bash
kubectl port-forward service/audit-service 8001:8001
```

Query audit trail:

```bash
curl http://localhost:8001/api/audit/tasks/42 | jq
```

**Expected response**:
```json
[
  {
    "id": 1,
    "event_type": "created",
    "task_id": 42,
    "user_id": "user123",
    "task_data": {
      "id": 42,
      "title": "Test Kafka Integration",
      ...
    },
    "timestamp": "2025-12-22T12:00:00Z",
    "source": "backend-api"
  }
]
```

---

## Step 5: Test Additional Event Flows

### 5.1 Test Task Update Event

```bash
curl -X PUT http://localhost:8000/api/$USER_ID/tasks/42 \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "priority": "medium"
  }'
```

**Verify**:
1. Backend logs: `Published event to task-events: updated`
2. Backend logs: `Published event to task-updates: task_updated`
3. Redpanda: 2 new messages (task-events + task-updates topics)
4. Audit service logs: `Received event: updated for task_id=42`

### 5.2 Test Task Completion Event

```bash
curl -X PATCH http://localhost:8000/api/$USER_ID/tasks/42/complete \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Verify**:
1. Backend logs: `Published event to task-events: completed`
2. Redpanda task-events topic: New "completed" message
3. Audit service: New audit log entry

### 5.3 Test Task Deletion Event

```bash
curl -X DELETE http://localhost:8000/api/$USER_ID/tasks/42 \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

**Verify**:
1. Backend logs: `Published event to task-events: deleted`
2. Redpanda: "deleted" message with full task snapshot
3. Audit service: Deletion audit log

### 5.4 Test Reminder Event (Future)

**Note**: Reminder events require a cron service to check due dates and publish events. Implementation deferred to future work.

**Manual test**:
```python
# Simulate cron service publishing reminder
import httpx

event = {
    "event_type": "reminder_due",
    "task_id": 42,
    "user_id": "user123",
    "title": "Test Task",
    "due_date": "2025-12-30T10:00:00Z",
    "remind_before_minutes": 30,
    ...
}

# Publish via Dapr
httpx.post("http://localhost:3500/v1.0/publish/kafka-pubsub/reminders", json=event)
```

**Verify**: Notification service logs show "Sending reminder: Test Task"

---

## Step 6: Monitor System Health

### 6.1 Redpanda Cloud Console Monitoring

1. **Navigate to**: Redpanda Cloud → Your Cluster → **Overview**
2. **Monitor**:
   - **Throughput**: Messages/second (should be >0 during testing)
   - **Storage**: Used vs 10GB limit (should be minimal for testing)
   - **Consumer Lag**: Navigate to **Consumer Groups** → `todo-service-group`
     - Expected: Lag = 0 or low (<10 messages)

3. **Per-Topic Metrics**: Topics → [topic-name] → **Metrics**
   - **task-events**: Steady increase during testing
   - **task-updates**: Increase on every update
   - **reminders**: 0 (no cron service yet)
   - **recurring-tasks**: 0 (no recurring tasks completed yet)

### 6.2 Kubernetes Service Health

```bash
# Check all pods running
kubectl get pods

# Check pod resource usage
kubectl top pods

# Check service endpoints
kubectl get endpoints
```

### 6.3 Real-Time Log Monitoring

**Open 3 terminal windows**:

**Terminal 1 - Backend logs**:
```bash
kubectl logs -f deployment/backend-service -c backend | grep -E "Published|ERROR"
```

**Terminal 2 - Audit service logs**:
```bash
kubectl logs -f deployment/audit-service -c audit | grep -E "Received|ERROR"
```

**Terminal 3 - Dapr logs (optional)**:
```bash
kubectl logs -f deployment/backend-service -c daprd | grep -E "publish|subscribe"
```

**Perform operations** (create/update/delete tasks) and watch logs in real-time.

---

## Troubleshooting Guide

### Issue: Backend not publishing events

**Symptoms**: No "Published event" logs, Redpanda topics empty

**Diagnosis**:
```bash
# Check KAFKA_ENABLED
kubectl get deployment backend-service -o yaml | grep KAFKA_ENABLED
# Should show: value: "true"

# Check Dapr sidecar
kubectl get pods -l app=backend
# Should show: 2/2 Running

# Check Dapr component
kubectl get component kafka-pubsub
# Should exist

# Check Dapr logs
kubectl logs deployment/backend-service -c daprd --tail=50
# Look for errors like "connection refused" or "authentication failed"
```

**Fixes**:
1. Verify `KAFKA_ENABLED=true` in deployment.yaml
2. Verify kafka-secrets exists: `kubectl get secret kafka-secrets`
3. Verify Redpanda bootstrap server is correct in pubsub-kafka.yaml
4. Restart backend pods: `kubectl rollout restart deployment/backend-service`

---

### Issue: Audit service not consuming events

**Symptoms**: Events in Redpanda but no audit service logs

**Diagnosis**:
```bash
# Check subscription
kubectl logs deployment/audit-service -c daprd | grep subscribe
# Should show: "app is subscribed to [task-events]"

# Check consumer group lag
# Navigate to Redpanda Cloud → Consumer Groups → todo-service-group
# Look for high lag (>10 messages)

# Check database connection
kubectl logs deployment/audit-service -c audit | grep -E "database|ERROR"
```

**Fixes**:
1. Verify audit service has correct `dapr.io/app-id` annotation
2. Verify `DAPR_PUBSUB_NAME=kafka-pubsub` environment variable
3. Verify database secret exists: `kubectl get secret db-secrets`
4. Check database is accessible from pod: `kubectl exec -it <audit-pod> -c audit -- curl http://DATABASE_HOST`
5. Restart audit service: `kubectl rollout restart deployment/audit-service`

---

### Issue: Pods stuck in CrashLoopBackOff

**Diagnosis**:
```bash
# Get pod name
kubectl get pods

# Check logs
kubectl logs <pod-name> -c <container-name>

# Check events
kubectl describe pod <pod-name>
```

**Common causes**:
- **Missing secret**: Check secrets exist
- **Database connection error**: Verify DATABASE_URL is correct
- **Image pull error**: Rebuild image with `eval $(minikube docker-env)`
- **Port conflict**: Verify no port conflicts in deployment

---

### Issue: High consumer lag in Redpanda

**Symptoms**: Consumer lag >100 messages and growing

**Diagnosis**:
```bash
# Check consumer pods running
kubectl get pods -l app=audit
kubectl get pods -l app=notification

# Check consumer logs for errors
kubectl logs deployment/audit-service -c audit --tail=100
```

**Fixes**:
1. Scale up consumers: `kubectl scale deployment/audit-service --replicas=2`
2. Check for processing errors in logs
3. Verify database is not overloaded (slow writes causing backlog)
4. Restart consumers to reset offset (caution: may reprocess messages)

---

## Success Criteria

✅ **Deployment Complete** when:
1. All pods show `2/2 Running` status
2. Backend publishes events successfully (visible in logs)
3. Redpanda Cloud console shows messages in all topics
4. Audit service consumes events and writes to database
5. Audit API returns records for test tasks
6. Consumer lag remains <10 messages

✅ **Ready for Production** when:
1. All success criteria above met
2. Performance meets targets (<50ms publish overhead, <1s consumption latency)
3. No error logs in any service
4. Monitoring dashboards show healthy metrics

---

## Next Steps

After successful deployment:

1. **Enable Reminder Cron Service** (future work):
   - Create cron service to check due dates
   - Publish reminder events 30 minutes before due date
   - Verify notification service sends emails

2. **Add Recurring Task Service** (future work):
   - Consume recurring-tasks topic
   - Auto-create next task occurrence
   - Publish new task-events

3. **Add Integration Tests**:
   - Automated tests for event flows
   - Contract tests for event schemas
   - Load tests for performance validation

4. **Production Deployment**:
   - Deploy to cloud Kubernetes (DOKS/GKE/AKS)
   - Configure production secrets (Sealed Secrets, Vault)
   - Set up monitoring (Prometheus, Grafana, alerts)
   - Configure CI/CD pipelines

5. **Monitoring & Observability**:
   - Integrate Jaeger for distributed tracing
   - Set up Prometheus metrics scraping
   - Create Grafana dashboards
   - Configure alerts for consumer lag, errors

---

## Reference Commands

### Useful kubectl Commands

```bash
# Get all resources
kubectl get all

# Describe pod for debugging
kubectl describe pod <pod-name>

# Get logs (last 50 lines)
kubectl logs <pod-name> -c <container-name> --tail=50

# Follow logs real-time
kubectl logs -f deployment/<deployment-name> -c <container-name>

# Execute command in pod
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash

# Port forward service
kubectl port-forward service/<service-name> <local-port>:<service-port>

# Restart deployment
kubectl rollout restart deployment/<deployment-name>

# Scale deployment
kubectl scale deployment/<deployment-name> --replicas=3

# Delete and recreate
kubectl delete -f <manifest.yaml>
kubectl apply -f <manifest.yaml>
```

### Useful Dapr Commands

```bash
# List Dapr components
kubectl get components

# Describe Dapr component
kubectl describe component <component-name>

# Check Dapr sidecar injected
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].name}'
# Should show: <app-name> daprd

# Dapr dashboard (if installed)
dapr dashboard -k
```

### Useful Docker Commands (within Minikube)

```bash
# Use Minikube Docker daemon
eval $(minikube docker-env)

# List images
docker images | grep todo

# Build image
docker build -t <image-name>:<tag> .

# Remove image (force rebuild)
docker rmi <image-name>:<tag>

# Check container logs (if pod crashes immediately)
docker logs <container-id>
```

---

**Quickstart Complete!** You now have a fully functional event-driven Todo application with Kafka streaming via Redpanda Cloud.

For questions or issues, see:
- **Redpanda Setup Guide**: `docs/REDPANDA_SETUP.md`
- **Architecture Overview**: `specs/005-cloud-native-deployment/overview.md`
- **Data Model**: `specs/004-kubernetes-deployment/data-model.md`
