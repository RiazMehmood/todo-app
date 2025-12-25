# Kafka Setup Guide - Redpanda Cloud Integration

## Current Status: ⚠️ Credentials Required

The Kafka pub/sub component is currently **disabled** because the Redpanda Cloud credentials appear to be invalid/expired.

## Issue Summary

**Error**: `kafka: client has run out of available brokers to talk to`

**Tests Performed**:
- ✅ Port 9092 is reachable from cluster (`nc -zv` succeeded)
- ✅ DNS resolution working (resolves to 34.228.206.20)
- ✅ TLS settings adjusted (`skipVerify: true` tested)
- ❌ SASL authentication fails during Kafka client initialization

**Root Cause**: The SASL username/password stored in Kubernetes secrets are likely:
- Expired (Redpanda free tier credentials have limited lifespan)
- Invalid (cluster may have been deleted/recreated)
- Incorrect (typo or wrong credentials)

## Solutions

### Option 1: Get New Redpanda Cloud Credentials (Recommended for Phase V)

1. **Create/Access Redpanda Cloud Account**:
   ```bash
   # Visit: https://cloud.redpanda.com/
   # Sign up for free tier (no credit card required)
   ```

2. **Create a New Cluster**:
   - Region: `us-east-1` (or your preferred region)
   - Tier: Serverless (free)
   - Note the bootstrap server URL

3. **Create SASL Credentials**:
   ```
   Navigate to: Cluster → Security → SASL
   Create user: todo-user (or any name)
   Save the username and password
   ```

4. **Create Required Topics**:
   ```
   Topics to create:
   - task-events
   - reminders
   - task-updates
   - recurring-tasks
   ```

5. **Update Kubernetes Secret**:
   ```bash
   kubectl delete secret kafka-secrets

   kubectl create secret generic kafka-secrets \
     --from-literal=username='<NEW_SASL_USERNAME>' \
     --from-literal=password='<NEW_SASL_PASSWORD>'
   ```

6. **Update Broker Address** (if different):
   ```bash
   # Edit k8s/dapr-components/pubsub-kafka.yaml
   # Update the brokers value:
   - name: brokers
     value: "<YOUR_CLUSTER>.cloud.redpanda.com:9092"
   ```

7. **Re-enable Kafka Component**:
   ```bash
   kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml

   # Restart services
   kubectl rollout restart deployment backend-service
   kubectl rollout restart deployment notification-service
   kubectl rollout restart deployment audit-service
   ```

### Option 2: Deploy Kafka in Kubernetes (Alternative)

If you prefer self-hosted Kafka within the cluster:

1. **Install Strimzi Operator**:
   ```bash
   kubectl create namespace kafka
   kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
   ```

2. **Deploy Kafka Cluster**:
   ```yaml
   # kafka-cluster.yaml
   apiVersion: kafka.strimzi.io/v1beta2
   kind: Kafka
   metadata:
     name: todo-kafka
     namespace: kafka
   spec:
     kafka:
       version: 3.6.0
       replicas: 1
       listeners:
         - name: plain
           port: 9092
           type: internal
           tls: false
       config:
         offsets.topic.replication.factor: 1
         transaction.state.log.replication.factor: 1
         transaction.state.log.min.isr: 1
       storage:
         type: ephemeral
     zookeeper:
       replicas: 1
       storage:
         type: ephemeral
   ```

3. **Update Dapr Component**:
   ```yaml
   # Update pubsub-kafka.yaml
   - name: brokers
     value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
   - name: authType
     value: "none"  # No SASL for internal Kafka
   - name: enableTLS
     value: "false"
   ```

### Option 3: Disable Kafka for Basic Deployment

For testing core functionality without event-driven features:

```bash
# Kafka component is already disabled
# Services will work but without:
# - Event broadcasting between services
# - Async task notifications
# - Audit log streaming
```

**Limitations**:
- No real-time notifications
- No event-driven task updates
- Audit service won't receive events
- Recurring tasks won't trigger reminders

## Verification Steps

Once credentials are updated:

1. **Check Dapr Component Status**:
   ```bash
   kubectl get components
   ```

2. **Check Backend Logs**:
   ```bash
   kubectl logs -l app=backend -c daprd | grep kafka
   ```

3. **Verify All Pods Healthy**:
   ```bash
   kubectl get pods
   # Should show 2/2 Ready for all services
   ```

4. **Test Event Publishing** (from backend):
   ```bash
   kubectl exec -it deployment/backend-service -c backend -- \
     python -c "
from dapr.clients import DaprClient
with DaprClient() as d:
    d.publish_event(
        pubsub_name='kafka-pubsub',
        topic_name='task-events',
        data='test event'
    )
print('Event published successfully')
"
   ```

## Current Configuration

**Broker**: `d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
**Username**: `todo-user` (stored in secret)
**Password**: `X7MWBBD9UaGuORKu6Z28qklbtbMPuv` (stored in secret)
**SASL Mechanism**: `SCRAM-SHA-256`
**TLS**: Enabled

**Status**: ❌ Authentication failing (credentials likely invalid)

## Phase V Requirements

Per the hackathon PDF, Phase V requires:
- ✅ Dapr deployment (working)
- ❌ Event-driven architecture with Kafka (credentials needed)
- ✅ Pub/Sub component configuration (configured, needs valid credentials)
- ✅ State management (working with PostgreSQL)
- ✅ Service invocation (working)
- ✅ Bindings (cron working)

**To complete Phase V**: Obtain valid Redpanda Cloud credentials or deploy in-cluster Kafka.

---

**Last Updated**: 2025-12-25
**Status**: Waiting for valid Kafka credentials
