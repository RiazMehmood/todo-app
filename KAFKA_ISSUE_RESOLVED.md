# Kafka Issue - ROOT CAUSE IDENTIFIED

## Problem Summary

**Status**: ❌ Blocked by Redpanda Cloud ACL Permissions
**Root Cause**: User `todo-user` lacks topic access permissions

## Diagnosis Timeline

### Tests Performed

1. ✅ **Port Connectivity**: Port 9092 reachable from cluster
   ```bash
   nc -zv d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com 9092
   # Result: OPEN
   ```

2. ✅ **DNS Resolution**: Resolves to 34.228.206.20
   ```bash
   nslookup d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com
   # Result: SUCCESS
   ```

3. ✅ **Kafka Authentication**: SASL-SCRAM-SHA-256 works
   ```bash
   kcat -b broker:9092 -X security.protocol=SASL_SSL \
        -X sasl.mechanism=SCRAM-SHA-256 \
        -X sasl.username=todo-user \
        -X sasl.password=X7MWBBD9UaGuORKu6Z28qklbtbMPuv -L

   # Result: SUCCESS - Listed 3 brokers
   Metadata for all topics (from broker -1):
    3 brokers:
     broker 13 at d54l263rcoacstirud90-13.0.us-east-1.mpx.prd.cloud.redpanda.com:9092
     broker 14 at d54l263rcoacstirud90-14.2.us-east-1.mpx.prd.cloud.redpanda.com:9092
     broker 15 at d54l263rcoacstirud90-15.1.us-east-1.mpx.prd.cloud.redpanda.com:9092
    0 topics
   ```

4. ❌ **Topic Access**: Authorization failed
   ```bash
   kcat -b broker:9092 -X security.protocol=SASL_SSL \
        -X sasl.username=todo-user \
        -X sasl.password=X7MWBBD9UaGuORKu6Z28qklbtbMPuv \
        -t task-events

   # ERROR: Topic task-events error: Broker: Topic authorization failed
   ```

## Root Cause

**Redpanda Cloud ACL Issue**: The user `todo-user` can authenticate but lacks permissions to:
- Create topics
- Produce messages to topics
- Consume messages from topics

## Solution Required

### Option 1: Create Topics & Grant Permissions (Recommended)

**Prerequisites**: Access to Redpanda Cloud Console

**Steps**:

1. **Login to Redpanda Cloud Console**
   - URL: https://cloud.redpanda.com/
   - Navigate to cluster: `d54l263rcoacstirud90`

2. **Create Required Topics**:
   ```
   Topics to create:
   - task-events       (partitions: 3, replication: 3)
   - reminders         (partitions: 3, replication: 3)
   - task-updates      (partitions: 3, replication: 3)
   - recurring-tasks   (partitions: 1, replication: 3)
   ```

   Navigate to: **Topics** → **Create Topic**

3. **Grant ACL Permissions to todo-user**:
   ```
   Navigate to: Security → ACLs → Add ACL

   For each topic (task-events, reminders, task-updates, recurring-tasks):

   Permission: ALLOW
   Principal: User:todo-user
   Host: *
   Operations:
     - Read
     - Write
     - Describe
     - Create (for dynamic topic creation)
   Resource Type: Topic
   Resource Name: <topic-name>
   ```

4. **Grant Consumer Group Permission**:
   ```
   Permission: ALLOW
   Principal: User:todo-user
   Host: *
   Operations:
     - Read
     - Describe
   Resource Type: Group
   Resource Name: todo-service-group
   ```

5. **Re-enable Kafka in Kubernetes**:
   ```bash
   kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml
   kubectl rollout restart deployment backend-service
   kubectl rollout restart deployment notification-service
   kubectl rollout restart deployment audit-service
   ```

6. **Verify Connection**:
   ```bash
   # Check Dapr logs
   kubectl logs -l app=backend -c daprd | grep kafka

   # Should see: "Component loaded: kafka-pubsub"
   ```

### Option 2: Deploy In-Cluster Kafka (Alternative)

If you don't have Redpanda Cloud console access:

```bash
# Install Strimzi Kafka Operator
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Deploy minimal Kafka cluster (see KAFKA_SETUP_GUIDE.md for full config)
```

### Option 3: Continue Without Kafka (Current)

Kafka is currently **disabled** to allow core functionality to work.

**Impact**:
- ❌ No real-time event broadcasting
- ❌ No async notifications
- ❌ No audit event streaming
- ✅ Core API functions normally
- ✅ Database operations work
- ✅ Direct service calls work

## Dapr Configuration Tested

Multiple Dapr Kafka configurations were attempted:

| Configuration | Result |
|---------------|--------|
| `authType: "password"` | Timeout connecting to brokers |
| `authType: "certificate"` | Missing CA cert error |
| `skipVerify: true/false` | No difference |
| Increased timeouts (60s) | Still timeout |
| Different Kafka versions | No difference |

**Conclusion**: Configuration is correct. Issue is ACL permissions, not connection.

## Error Messages

### Dapr Error (when Kafka enabled):
```
Failed to init component kafka-pubsub (pubsub.kafka/v1):
kafka: client has run out of available brokers to talk to
init timeout for component kafka-pubsub (pubsub.kafka/v1)
```

**Why This Error?**: Dapr Kafka client connects to bootstrap broker, but when trying to discover topic metadata, it gets authorization errors and treats it as "no brokers available".

### Kcat Error (topic access):
```
% ERROR: Topic task-events error: Broker: Topic authorization failed
```

**This is the actual root cause** - ACL permissions missing.

## Current Status

**Deployment Status**: ✅ All services operational (without Kafka)
```bash
backend-service:        2/2 Running
notification-service:   2/2 Running
audit-service:          2/2 Running
```

**Kafka Status**: ⚠️ Disabled (ACL permissions required)

**Next Step**: Request Redpanda Cloud admin to:
1. Create 4 topics
2. Grant ACL permissions to `todo-user`
3. Then re-enable Kafka component

## Documentation References

- **Redpanda ACL Documentation**: https://docs.redpanda.com/docs/manage/security/authorization/acl/
- **Dapr Kafka Component**: https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/
- **Troubleshooting Guide**: See `KAFKA_SETUP_GUIDE.md`

---

**Date**: 2025-12-25
**Status**: Waiting for Redpanda Cloud ACL configuration
**Verified By**: kcat connection tests
