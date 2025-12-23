# Redpanda Cloud Setup Guide - Phase V

## Overview

Redpanda Cloud provides a Kafka-compatible streaming platform with a free serverless tier, perfect for this project. This guide walks you through setting up Redpanda Cloud for the Todo app's event-driven architecture.

## Why Redpanda?

- **Kafka-Compatible**: Use existing Kafka clients and tools
- **No ZooKeeper**: Simpler architecture, easier operations
- **Free Serverless Tier**: Up to 10 GB/month storage, 10 MB/s throughput
- **Fast Setup**: Under 5 minutes to get started
- **Cloud-Native**: Built for Kubernetes and containerized workloads

## Step 1: Create Redpanda Cloud Account

1. Go to [Redpanda Cloud](https://redpanda.com/cloud)
2. Click "Start Free" or "Sign Up"
3. Create account with email/Google/GitHub
4. Verify your email address

## Step 2: Create Serverless Cluster

1. After login, click "Create Cluster"
2. Select **Serverless** tier (free)
3. Configure cluster:
   - **Name**: `todo-cluster` (or your preference)
   - **Cloud Provider**: AWS (recommended for free tier)
   - **Region**: Choose closest to your deployment (e.g., `us-east-1`)
4. Click "Create Cluster"
5. Wait 2-3 minutes for cluster provisioning

## Step 3: Create Kafka Topics

Once your cluster is ready:

1. Go to **Topics** tab
2. Create the following topics:

### Topic 1: task-events
- **Name**: `task-events`
- **Partitions**: 3
- **Retention**: 7 days
- **Cleanup Policy**: Delete
- **Purpose**: Audit trail for all task operations

### Topic 2: reminders
- **Name**: `reminders`
- **Partitions**: 2
- **Retention**: 24 hours
- **Cleanup Policy**: Delete
- **Purpose**: Due date reminder notifications

### Topic 3: task-updates
- **Name**: `task-updates`
- **Partitions**: 3
- **Retention**: 1 hour
- **Cleanup Policy**: Delete
- **Purpose**: Real-time sync across clients

### Topic 4: recurring-tasks
- **Name**: `recurring-tasks`
- **Partitions**: 2
- **Retention**: 24 hours
- **Cleanup Policy**: Delete
- **Purpose**: Recurring task completion processing

## Step 4: Get Connection Credentials

1. Go to **Security** tab
2. Click "Create User" or use default user
3. Note the following credentials:
   - **Bootstrap Server**: e.g., `todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092`
   - **SASL Username**: Your username (e.g., `todo-user`)
   - **SASL Password**: Generated password (e.g., `xyzabc123...`)
   - **SASL Mechanism**: `SCRAM-SHA-256`

**IMPORTANT**: Save these credentials securely! You'll need them for Kubernetes secrets.

## Step 5: Test Connection (Optional)

Test your Redpanda cluster using `rpk` (Redpanda CLI):

```bash
# Install rpk
brew install redpanda-data/tap/redpanda

# Or download from https://docs.redpanda.com/current/get-started/rpk-install/

# Test connection
rpk topic list \
  --brokers todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092 \
  --user todo-user \
  --password 'your-password' \
  --sasl-mechanism SCRAM-SHA-256 \
  --tls-enabled

# Produce a test message
echo "test message" | rpk topic produce task-events \
  --brokers todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092 \
  --user todo-user \
  --password 'your-password' \
  --sasl-mechanism SCRAM-SHA-256 \
  --tls-enabled

# Consume messages
rpk topic consume task-events \
  --brokers todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092 \
  --user todo-user \
  --password 'your-password' \
  --sasl-mechanism SCRAM-SHA-256 \
  --tls-enabled
```

## Step 6: Configure Kubernetes Secrets

Create Kubernetes secret with your Redpanda credentials:

```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='YOUR_REDPANDA_USERNAME' \
  --from-literal=password='YOUR_REDPANDA_PASSWORD' \
  --from-literal=bootstrapServer='YOUR_CLUSTER.cloud.redpanda.com:9092'
```

**Example**:
```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username='todo-user' \
  --from-literal=password='xyzabc123secretpassword' \
  --from-literal=bootstrapServer='todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092'
```

Verify secret creation:
```bash
kubectl get secret kafka-secrets
kubectl describe secret kafka-secrets
```

## Step 7: Update Dapr Component

Update `k8s/dapr-components/pubsub-kafka.yaml` with your bootstrap server:

```yaml
metadata:
  - name: brokers
    value: "todo-cluster-abc123.us-east-1.cloud.redpanda.com:9092"  # Replace with your server
```

## Step 8: Deploy Dapr Components

```bash
# Apply all Dapr components
kubectl apply -f k8s/dapr-components/

# Verify Dapr components
kubectl get components

# Should see: kafka-pubsub, statestore, secrets-kubernetes, reminder-cron
```

## Step 9: Enable Kafka in Backend

Set environment variable to enable Kafka event publishing:

```bash
# In backend deployment (k8s/backend/deployment.yaml)
env:
- name: KAFKA_ENABLED
  value: "true"  # Change from false to true
```

Or set via ConfigMap:
```bash
kubectl create configmap backend-config --from-literal=KAFKA_ENABLED=true
```

## Step 10: Monitor Kafka Topics

Monitor your topics in Redpanda Cloud console:

1. Go to **Topics** tab
2. Click on a topic (e.g., `task-events`)
3. View:
   - **Messages**: Real-time message flow
   - **Metrics**: Throughput, latency, consumer lag
   - **Consumers**: Active consumer groups

## Troubleshooting

### Connection Refused
- **Issue**: Cannot connect to Redpanda cluster
- **Fix**: Verify bootstrap server URL is correct
- **Fix**: Ensure TLS is enabled (`enableTLS: true`)
- **Fix**: Check firewall/network security groups

### Authentication Failed
- **Issue**: SASL authentication error
- **Fix**: Verify username and password are correct
- **Fix**: Ensure SASL mechanism matches (`SCRAM-SHA-256`)
- **Fix**: Recreate Kubernetes secret with correct credentials

### Topic Not Found
- **Issue**: Producer/consumer cannot find topic
- **Fix**: Create topic in Redpanda Cloud console
- **Fix**: Verify topic name matches exactly (case-sensitive)

### Consumer Lag Growing
- **Issue**: Messages piling up, not being consumed
- **Fix**: Check consumer pods are running: `kubectl get pods`
- **Fix**: Check consumer logs: `kubectl logs <pod-name>`
- **Fix**: Verify Dapr sidecar is enabled in deployment
- **Fix**: Check Dapr component configuration

### Messages Not Appearing
- **Issue**: Backend publishes but no messages in topic
- **Fix**: Verify `KAFKA_ENABLED=true` in backend
- **Fix**: Check backend logs for Dapr connection errors
- **Fix**: Ensure Dapr sidecar is running: `kubectl get pods -o wide`
- **Fix**: Test Dapr Pub/Sub: `dapr publish --pubsub kafka-pubsub --topic task-events --data '{"test": true}'`

## Monitoring Dashboard

Redpanda Cloud provides built-in monitoring:

1. **Overview**: Cluster health, throughput, storage
2. **Topics**: Per-topic metrics and message rates
3. **Consumers**: Consumer group lag and offsets
4. **Alerts**: Set up alerts for critical metrics

Recommended alerts:
- Consumer lag > 1000 messages
- Disk usage > 80%
- Error rate > 1%

## Cost Management (Free Tier Limits)

Free Serverless tier includes:
- **Storage**: 10 GB/month
- **Throughput**: 10 MB/s
- **Connections**: 100 concurrent
- **Retention**: Up to 7 days

**Tips to stay within limits**:
- Set appropriate retention periods (1-7 days)
- Use compact retention for state topics
- Monitor storage usage in dashboard
- Delete old topics when not needed

## Next Steps

After Redpanda is configured:

1. ✅ Kafka cluster created and topics configured
2. ✅ Kubernetes secrets created
3. ✅ Dapr components deployed
4. → Deploy microservices: `kubectl apply -f k8s/`
5. → Verify event flow in Redpanda console
6. → Test end-to-end: create task → see events

## References

- [Redpanda Cloud Documentation](https://docs.redpanda.com/cloud/)
- [Redpanda Quickstart](https://docs.redpanda.com/current/get-started/quick-start/)
- [RPK CLI Reference](https://docs.redpanda.com/current/reference/rpk/)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
