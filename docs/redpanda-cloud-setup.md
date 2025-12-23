# Redpanda Cloud Setup Guide

## Overview
This guide shows you how to set up Redpanda Cloud (Serverless Kafka) for the Todo app event-driven architecture.

## Why Redpanda Cloud?
- **Free Serverless Tier**: Perfect for development and hackathons
- **Kafka-Compatible**: Uses standard Kafka APIs
- **No Infrastructure Management**: Fully managed service
- **Fast Setup**: Under 5 minutes
- **Production-Ready**: Same service used in production

## Step-by-Step Setup

### 1. Create Redpanda Cloud Account

1. Visit https://redpanda.com/cloud
2. Click "Sign Up" or "Start Free"
3. Create account with email/Google/GitHub
4. Verify your email address

### 2. Create Serverless Cluster

1. Log in to Redpanda Cloud Console
2. Click "Create Cluster"
3. Select **"Serverless"** (Free Tier)
4. Choose a cluster name (e.g., `todo-app-cluster`)
5. Select region closest to you (e.g., `us-east-1`)
6. Click "Create"
7. Wait ~2-3 minutes for cluster provisioning

### 3. Create Kafka Topics

Once cluster is ready, create the required topics:

1. Navigate to "Topics" tab
2. Click "Create Topic" for each:

| Topic Name | Partitions | Retention | Purpose |
|------------|-----------|-----------|---------|
| `task-events` | 3 | 7 days | All task CRUD operations (audit trail) |
| `task-updates` | 3 | 1 day | Real-time sync across clients |
| `reminders` | 1 | 1 day | Due date reminder notifications |
| `recurring-tasks` | 1 | 1 day | Recurring task completion processing |

**Create Topic Example**:
```
Topic Name: task-events
Partitions: 3
Retention: 7 days (604800000 ms)
Cleanup Policy: delete
```

### 4. Get Connection Credentials

1. Go to "Cluster Settings" or "Connect" tab
2. Copy the following details:

```bash
# Bootstrap Server
your-cluster.cloud.redpanda.com:9092

# SASL Mechanism
SCRAM-SHA-256

# SASL Username
your-username-here

# SASL Password
your-password-here
```

3. **Save these credentials securely** - you'll need them for Kubernetes secrets

### 5. Test Connection (Optional)

Install Redpanda CLI (`rpk`) to test connection:

```bash
# Install rpk
curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip
unzip rpk-linux-amd64.zip
sudo mv rpk /usr/local/bin/

# Test connection
rpk topic list \
  --brokers your-cluster.cloud.redpanda.com:9092 \
  --user your-username \
  --password your-password \
  --sasl-mechanism SCRAM-SHA-256
```

You should see the topics you created.

## Create Kubernetes Secrets

Once you have credentials, create Kubernetes secrets:

```bash
# Create kafka-secrets
kubectl create secret generic kafka-secrets \
  --from-literal=brokers='your-cluster.cloud.redpanda.com:9092' \
  --from-literal=username='your-username' \
  --from-literal=password='your-password'

# Verify secret was created
kubectl get secret kafka-secrets
```

## Update Dapr Component

Your Dapr Pub/Sub component (`k8s/dapr-components/pubsub-kafka.yaml`) should reference these secrets:

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
      secretKeyRef:
        name: kafka-secrets
        key: brokers
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
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: consumerGroup
      value: "todo-service-group"
```

## Environment Variables

Update your backend `.env` file:

```bash
# Enable Kafka integration
KAFKA_ENABLED=true

# Dapr sidecar URL (default)
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

## Verify Setup

1. Deploy your application to Kubernetes
2. Check Dapr component status:
```bash
kubectl get components
```

3. Check backend logs for Kafka connection:
```bash
kubectl logs -f deployment/backend -c backend | grep -i kafka
```

4. Create a task via API and verify event in Redpanda Console:
   - Go to Redpanda Cloud Console → Topics → `task-events`
   - Click "Messages"
   - You should see the published event

## Monitoring

### Redpanda Cloud Console
- View message rates and throughput
- Monitor consumer lag
- Inspect individual messages
- View topic configuration

### Metrics to Watch
- **Throughput**: Messages/second per topic
- **Consumer Lag**: How far behind consumers are
- **Error Rate**: Failed message delivery
- **Partition Distribution**: Even distribution across partitions

## Troubleshooting

### Connection Refused
- Verify bootstrap server URL is correct (include `:9092` port)
- Check firewall/network allows outbound connections on port 9092
- Verify SASL credentials are correct

### Authentication Failed
- Double-check username and password
- Verify SASL mechanism is `SCRAM-SHA-256`
- Regenerate credentials in Redpanda Console if needed

### Topics Not Found
- Verify topics were created in Redpanda Console
- Check topic names match exactly (case-sensitive)
- Ensure Dapr component references correct topic names

### Messages Not Being Published
- Check backend logs for Dapr errors
- Verify `KAFKA_ENABLED=true` in environment
- Ensure Dapr sidecar is running: `kubectl get pods -l app=backend`
- Check Dapr component is loaded: `kubectl logs deployment/backend -c daprd`

## Cost Management

### Free Tier Limits (as of 2024)
- **Throughput**: Up to 10 MB/s
- **Storage**: Up to 10 GB
- **Retention**: Up to 30 days
- **No credit card required** for serverless tier

### Monitoring Usage
- View usage in Redpanda Cloud Console → Billing
- Set up alerts for approaching limits
- Clean up test topics when not needed

## Production Considerations

### Security
- Rotate SASL credentials regularly
- Use Kubernetes secrets (never hardcode)
- Enable TLS encryption (default for Redpanda Cloud)
- Implement proper ACLs in production

### Reliability
- Use at least 3 partitions for critical topics
- Set appropriate retention based on replay needs
- Monitor consumer lag alerts
- Implement dead letter queues for failed messages

### Performance
- Tune consumer group size for throughput
- Use batching for high-volume producers
- Monitor partition distribution
- Scale partitions as traffic grows

## Alternative: Local Development

For local development without Redpanda Cloud, use Dapr's in-memory pub/sub:

```yaml
# k8s/dapr-components/pubsub-inmemory.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.in-memory
  version: v1
  metadata:
    - name: consumerID
      value: "todo-local"
```

Then toggle in backend:
```bash
KAFKA_ENABLED=true  # Still true, but using in-memory pub/sub
```

## References

- [Redpanda Cloud Documentation](https://docs.redpanda.com/docs/deploy/deployment-option/cloud/)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)
- [Redpanda vs Kafka](https://redpanda.com/redpanda-vs-kafka)
