# Dapr Integration Specification

## Overview
Implement all Dapr building blocks for distributed application runtime, abstracting infrastructure complexity from application code.

## What is Dapr?

Dapr (Distributed Application Runtime) is a portable, event-driven runtime that:
- Runs as a **sidecar** next to your application
- Provides building blocks via **HTTP/gRPC APIs**
- Abstracts infrastructure (Kafka, Redis, PostgreSQL, etc.)
- Enables polyglot microservices
- Simplifies cloud-native development

## Dapr Building Blocks for Todo App

### 1. Pub/Sub (Event Streaming)
### 2. State Management (Data Persistence)
### 3. Bindings (External Systems Integration)
### 4. Secrets Management (Security)
### 5. Service Invocation (Inter-service Communication)

---

## 1. Pub/Sub Building Block

### Purpose
Abstract Kafka integration - publish/subscribe without direct kafka-python dependency

### Architecture
```
┌──────────────┐                    ┌──────────────┐
│  Backend     │   HTTP POST        │     Dapr     │
│  FastAPI     │ ───────────────────│   Sidecar    │
│              │                    │              │
└──────────────┘                    └──────┬───────┘
                                           │
                                           │ Kafka Protocol
                                           ▼
                                  ┌────────────────┐
                                  │ Redpanda Cloud │
                                  │   (Kafka)      │
                                  └────────────────┘
```

### Without Dapr (Direct Kafka)
```python
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    security_protocol="SASL_SSL",
    sasl_mechanism="SCRAM-SHA-256",
    sasl_plain_username="username",
    sasl_plain_password="password"
)

producer.send("task-events", value=event)
```

**Problems**:
- Tight coupling to Kafka
- Complex configuration
- Vendor lock-in
- Difficult to test locally

### With Dapr (Abstracted)
```python
import httpx

# Publish via Dapr sidecar
async with httpx.AsyncClient() as client:
    await client.post(
        "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
        json={"event_type": "created", "task_id": 1}
    )
```

**Benefits**:
- No Kafka library needed
- Simple HTTP API
- Can swap Kafka for RabbitMQ with config change
- Easy local testing with in-memory pub/sub

### Dapr Component Configuration

**File**: `k8s/dapr-components/pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "your-cluster.cloud.redpanda.com:9092"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: consumerGroup
      value: "todo-service-group"
```

### Publishing Events

```python
# backend/src/dapr_client.py
import httpx
from typing import Dict, Any

class DaprClient:
    def __init__(self, dapr_http_port: int = 3500):
        self.base_url = f"http://localhost:{dapr_http_port}"

    async def publish_event(self, pubsub_name: str, topic: str, data: Dict[str, Any]):
        """Publish event to Dapr Pub/Sub"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1.0/publish/{pubsub_name}/{topic}",
                json=data
            )
            response.raise_for_status()
```

### Subscribing to Events

**Subscription Configuration**:
```yaml
# backend/src/subscriptions.yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-subscription
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    default: /events/task-events
```

**Event Handler**:
```python
# backend/src/main.py
from fastapi import FastAPI

app = FastAPI()

@app.post("/events/task-events")
async def handle_task_event(event: dict):
    """Handle task events from Kafka via Dapr"""
    event_type = event["data"]["event_type"]
    task_id = event["data"]["task_id"]

    print(f"Received {event_type} event for task {task_id}")

    # Process event (e.g., log to audit, update cache, etc.)

    return {"status": "success"}
```

---

## 2. State Management Building Block

### Purpose
Store conversation history and task cache without direct database code

### Architecture
```
┌──────────────┐                    ┌──────────────┐
│  Backend     │   HTTP POST/GET    │     Dapr     │
│  FastAPI     │ ───────────────────│   Sidecar    │
│              │                    │              │
└──────────────┘                    └──────┬───────┘
                                           │
                                           │ PostgreSQL Protocol
                                           ▼
                                  ┌────────────────┐
                                  │   Neon DB      │
                                  │  (PostgreSQL)  │
                                  └────────────────┘
```

### Without Dapr (Direct DB)
```python
from sqlmodel import Session

session.add(Message(...))
session.commit()

messages = session.query(Message).filter(...).all()
```

### With Dapr (Abstracted State)
```python
import httpx

# Save state
async with httpx.AsyncClient() as client:
    await client.post(
        "http://localhost:3500/v1.0/state/statestore",
        json=[{
            "key": f"conversation-{conv_id}",
            "value": {"messages": messages}
        }]
    )

# Get state
response = await client.get(
    f"http://localhost:3500/v1.0/state/statestore/conversation-{conv_id}"
)
conversation = response.json()
```

### Dapr Component Configuration

**File**: `k8s/dapr-components/state-postgresql.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection_string
```

### Use Cases

1. **Conversation State**: Store chat history
2. **Task Cache**: Cache frequently accessed tasks
3. **User Preferences**: Store user settings
4. **Session Data**: Store temporary session information

---

## 3. Bindings Building Block

### Purpose
Trigger scheduled jobs (reminder checks) without cron jobs or external schedulers

### Architecture
```
┌────────────────────┐
│   Dapr Cron        │
│   Binding          │
│  (Every 5 min)     │
└────────┬───────────┘
         │
         │ HTTP POST
         ▼
┌────────────────────┐
│   Backend API      │
│  /reminder-cron    │
│   Endpoint         │
└────────────────────┘
```

### Dapr Component Configuration

**File**: `k8s/dapr-components/binding-cron.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
  namespace: default
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "*/5 * * * *"  # Every 5 minutes
    - name: direction
      value: "input"
```

### Backend Handler

```python
# backend/src/main.py
@app.post("/reminder-cron")
async def check_reminders():
    """Triggered every 5 minutes by Dapr Cron Binding"""
    now = datetime.utcnow()
    upcoming_threshold = now + timedelta(minutes=5)

    # Find tasks due soon that need reminders
    tasks = session.query(Task).filter(
        Task.due_date.isnot(None),
        Task.reminder_sent == False,
        Task.due_date - Task.remind_before_minutes * 60 <= upcoming_threshold
    ).all()

    for task in tasks:
        # Publish reminder event to Kafka via Dapr
        await dapr_client.publish_event(
            pubsub_name="kafka-pubsub",
            topic="reminders",
            data={
                "event_type": "reminder_due",
                "task_id": task.id,
                "user_id": task.user_id,
                "title": task.title,
                "due_date": task.due_date.isoformat()
            }
        )

        task.reminder_sent = True

    session.commit()

    return {"reminders_sent": len(tasks)}
```

---

## 4. Secrets Management Building Block

### Purpose
Securely store and access API keys, database credentials, and other secrets

### Without Dapr (Environment Variables)
```python
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

**Problems**:
- Secrets in environment variables
- Difficult to rotate
- Not encrypted at rest
- Hard to audit access

### With Dapr (Secret Store)
```python
import httpx

# Get secret from Dapr
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:3500/v1.0/secrets/kubernetes-secrets/openai-api-key"
    )
    api_key = response.json()["openai-api-key"]
```

### Dapr Component Configuration

**File**: `k8s/dapr-components/secretstore-kubernetes.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

### Kubernetes Secrets

Create secrets:
```bash
kubectl create secret generic api-secrets \
  --from-literal=openai-api-key='sk-...' \
  --from-literal=better-auth-secret='secret-...'

kubectl create secret generic db-secrets \
  --from-literal=connection_string='postgresql://...'

kubectl create secret generic kafka-secrets \
  --from-literal=username='your-username' \
  --from-literal=password='your-password'
```

---

## 5. Service Invocation Building Block

### Purpose
Frontend → Backend communication with built-in retries, service discovery, and mTLS

### Without Dapr (Direct HTTP)
```typescript
// Frontend must know backend URL
const response = await fetch("http://backend-service:8000/api/chat", {
  method: "POST",
  body: JSON.stringify({message: "Add task"})
});
```

**Problems**:
- Hardcoded service URLs
- No automatic retries
- No circuit breaker
- Manual TLS configuration

### With Dapr (Service Invocation)
```typescript
// Frontend calls via Dapr sidecar
const response = await fetch(
  "http://localhost:3500/v1.0/invoke/backend-service/method/api/chat",
  {
    method: "POST",
    body: JSON.stringify({message: "Add task"})
  }
);
```

**Benefits**:
- Automatic service discovery
- Built-in retries
- Circuit breaker pattern
- Automatic mTLS encryption
- Load balancing

### Configuration

**Frontend Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend-service"
        dapr.io/app-port: "3000"
    spec:
      containers:
        - name: frontend
          image: your-frontend:latest
```

**Backend Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
    spec:
      containers:
        - name: backend
          image: your-backend:latest
```

---

## Complete Dapr Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                         │
│                                                                │
│  ┌────────────────────┐       ┌────────────────────┐         │
│  │  Frontend Pod      │       │  Backend Pod       │         │
│  │ ┌────────┐┌──────┐ │       │ ┌────────┐┌──────┐ │         │
│  │ │Next.js ││ Dapr │ │       │ │FastAPI ││ Dapr │ │         │
│  │ │  App   ││Sidecar│◄┼───────┼►│+ MCP  ││Sidecar│ │         │
│  │ └────────┘└──────┘ │       │ └────────┘└──────┘ │         │
│  └────────────────────┘       └────────────────────┘         │
│                                       │                       │
│                            ┌──────────┴──────────┐            │
│                            │                     │            │
│  ┌─────────────────────────▼─────────────────────▼────────┐  │
│  │              Dapr Components                           │  │
│  │ ┌──────────────────┐  ┌─────────────────┐             │  │
│  │ │ pubsub.kafka     │──┼──► Redpanda     │             │  │
│  │ ├──────────────────┤  │    Cloud        │             │  │
│  │ │ state.postgresql │──┼──► Neon DB      │             │  │
│  │ ├──────────────────┤  │                 │             │  │
│  │ │ bindings.cron    │  │ (Cron triggers) │             │  │
│  │ ├──────────────────┤  │                 │             │  │
│  │ │ secretstores.k8s │  │ (K8s Secrets)   │             │  │
│  │ └──────────────────┘  └─────────────────┘             │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Install Dapr CLI
```bash
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
```

### Initialize Dapr on Kubernetes
```bash
dapr init -k
```

### Deploy Dapr Components
```bash
kubectl apply -f k8s/dapr-components/
```

### Run App with Dapr Sidecar (Local)
```bash
# Backend
dapr run --app-id backend-service --app-port 8000 -- uvicorn main:app

# Frontend
dapr run --app-id frontend-service --app-port 3000 -- npm run dev
```

## Benefits of Using Dapr

| Aspect | Without Dapr | With Dapr |
|--------|-------------|-----------|
| **Infrastructure** | Import libraries (kafka-python, redis, psycopg2) | Single HTTP API for all |
| **Configuration** | Connection strings in code | YAML component configs |
| **Retry Logic** | Manual implementation | Built-in with exponential backoff |
| **Service Discovery** | Hardcoded URLs | Automatic by app-id |
| **Secrets** | Environment variables | Secure secret store |
| **Vendor Lock-in** | Tight coupling | Swap backends with config change |
| **Testing** | Complex mocks | Simple HTTP mocks |

## Testing Strategy

### Unit Tests
- Mock Dapr HTTP API responses
- Test business logic independently

### Integration Tests
- Use Dapr self-hosted mode for local testing
- Test Dapr component integration

### E2E Tests
- Deploy to Minikube with Dapr
- Test complete workflows

## Monitoring

### Dapr Dashboard
```bash
dapr dashboard -k
```

### Metrics
- Request/response times
- Error rates
- Component health

### Logging
- All Dapr API calls logged
- Component errors logged
- Application logs separated from Dapr logs

## Success Criteria

- ✅ Dapr installed on Kubernetes cluster
- ✅ All 5 building blocks implemented
- ✅ Pub/Sub working with Kafka
- ✅ State management working with PostgreSQL
- ✅ Cron binding triggering reminder checks
- ✅ Secrets securely accessed from Kubernetes
- ✅ Service invocation working between frontend/backend
- ✅ Application code simplified (no direct library dependencies)
- ✅ Can swap infrastructure backends without code changes
