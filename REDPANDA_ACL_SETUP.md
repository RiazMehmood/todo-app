# Redpanda Cloud ACL Configuration Guide

## Quick Start - Configure ACLs for todo-user

Your cluster: `d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
Your user: `todo-user`

---

## Method 1: Redpanda Cloud Console (Easiest)

### Step 1: Login to Redpanda Cloud

1. Go to: https://cloud.redpanda.com/
2. Login with your account
3. Select your cluster: `d54l263rcoacstirud90`

### Step 2: Create Topics (if they don't exist)

1. Navigate to **Topics** in the left sidebar
2. Click **Create Topic** button

Create these 4 topics:

| Topic Name | Partitions | Replication | Retention |
|------------|------------|-------------|-----------|
| `task-events` | 3 | 3 | 7 days |
| `reminders` | 3 | 3 | 7 days |
| `task-updates` | 3 | 3 | 7 days |
| `recurring-tasks` | 1 | 3 | 30 days |

**For each topic:**
- Topic name: `<name-from-table>`
- Partitions: `3` (or 1 for recurring-tasks)
- Replication factor: `3` (default)
- Retention: Leave default or set as above
- Click **Create**

### Step 3: Configure ACLs for Topics

1. Navigate to **Security** → **Access Control** (or **ACLs**)
2. Click **Create ACL** or **Add ACL**

**For EACH topic** (task-events, reminders, task-updates, recurring-tasks):

```
Resource Type: Topic
Resource Name: task-events  (repeat for each topic)
Pattern Type: Literal
Principal: User:todo-user
Host: *
Operation: All  (or select: Read, Write, Describe, Create)
Permission: Allow
```

Click **Create** or **Save**

**Repeat 4 times** (once for each topic)

### Step 4: Configure ACL for Consumer Group

1. Still in **Security** → **Access Control**
2. Click **Create ACL**

```
Resource Type: Group
Resource Name: todo-service-group
Pattern Type: Literal
Principal: User:todo-user
Host: *
Operation: All  (or select: Read, Describe)
Permission: Allow
```

Click **Create** or **Save**

### Step 5: Verify ACLs

In the **ACLs** page, you should see 5 ACL entries:
- 4 for topics (task-events, reminders, task-updates, recurring-tasks)
- 1 for consumer group (todo-service-group)

---

## Method 2: Using rpk CLI (Advanced)

If you prefer command-line:

### Step 1: Install rpk

```bash
# On Linux
curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip
unzip rpk-linux-amd64.zip
sudo mv rpk /usr/local/bin/

# On macOS
brew install redpanda-data/tap/redpanda
```

### Step 2: Configure rpk

Create `~/.config/rpk/rpk.yaml`:

```yaml
rpk:
  kafka_api:
    brokers:
      - d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
    sasl:
      mechanism: SCRAM-SHA-256
      user: todo-user
      password: X7MWBBD9UaGuORKu6Z28qklbtbMPuv
    tls:
      enabled: true
```

### Step 3: Create Topics

```bash
rpk topic create task-events -p 3 -r 3
rpk topic create reminders -p 3 -r 3
rpk topic create task-updates -p 3 -r 3
rpk topic create recurring-tasks -p 1 -r 3
```

### Step 4: Create ACLs

```bash
# Grant permissions for each topic
for topic in task-events reminders task-updates recurring-tasks; do
  rpk security acl create \
    --allow-principal User:todo-user \
    --operation all \
    --topic "$topic"
done

# Grant consumer group permissions
rpk security acl create \
  --allow-principal User:todo-user \
  --operation all \
  --group todo-service-group
```

### Step 5: List ACLs to Verify

```bash
rpk security acl list
```

Expected output:
```
PRINCIPAL       HOST  RESOURCE-TYPE  RESOURCE-NAME      RESOURCE-PATTERN-TYPE  OPERATION  PERMISSION  ERROR
User:todo-user  *     TOPIC          task-events        LITERAL                ALL        ALLOW
User:todo-user  *     TOPIC          reminders          LITERAL                ALL        ALLOW
User:todo-user  *     TOPIC          task-updates       LITERAL                ALL        ALLOW
User:todo-user  *     TOPIC          recurring-tasks    LITERAL                ALL        ALLOW
User:todo-user  *     GROUP          todo-service-group LITERAL                ALL        ALLOW
```

---

## Method 3: Using Kubernetes Pod with rpk

If you don't have local rpk installed:

```bash
# Create a pod with rpk
kubectl run rpk-admin --image=redpandadata/redpanda:latest --rm -it --restart=Never -- bash

# Inside the pod, configure rpk
cat > /etc/redpanda/redpanda.yaml <<EOF
rpk:
  kafka_api:
    brokers:
      - d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
    sasl:
      mechanism: SCRAM-SHA-256
      user: todo-user
      password: X7MWBBD9UaGuORKu6Z28qklbtbMPuv
    tls:
      enabled: true
EOF

# Create topics
rpk topic create task-events -p 3 -r 3
rpk topic create reminders -p 3 -r 3
rpk topic create task-updates -p 3 -r 3
rpk topic create recurring-tasks -p 1 -r 3

# Create ACLs
rpk security acl create --allow-principal User:todo-user --operation all --topic task-events
rpk security acl create --allow-principal User:todo-user --operation all --topic reminders
rpk security acl create --allow-principal User:todo-user --operation all --topic task-updates
rpk security acl create --allow-principal User:todo-user --operation all --topic recurring-tasks
rpk security acl create --allow-principal User:todo-user --operation all --group todo-service-group

# Verify
rpk security acl list

# Exit pod
exit
```

---

## Verification Steps

### Test 1: List Topics (should work now)

```bash
kubectl run kcat-test --image=edenhill/kcat:1.7.1 --rm -it --restart=Never -- \
  -b d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=todo-user \
  -X sasl.password=X7MWBBD9UaGuORKu6Z28qklbtbMPuv \
  -L
```

**Expected**: Should list all 4 topics instead of "0 topics"

### Test 2: Produce a Test Message

```bash
kubectl run kcat-test --image=edenhill/kcat:1.7.1 --rm -it --restart=Never -- \
  -b d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=todo-user \
  -X sasl.password=X7MWBBD9UaGuORKu6Z28qklbtbMPuv \
  -P -t task-events <<< '{"event":"test","timestamp":"2025-12-25"}'
```

**Expected**: Message delivered successfully (no authorization error)

### Test 3: Consume from Topic

```bash
kubectl run kcat-test --image=edenhill/kcat:1.7.1 --rm -it --restart=Never -- \
  -b d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=todo-user \
  -X sasl.password=X7MWBBD9UaGuORKu6Z28qklbtbMPuv \
  -C -t task-events -o beginning -c 1
```

**Expected**: Should show the test message

---

## After ACLs are Configured

### Enable Kafka in Kubernetes

```bash
# Re-apply Kafka component
kubectl apply -f k8s/dapr-components/pubsub-kafka.yaml

# Restart all services
kubectl rollout restart deployment backend-service
kubectl rollout restart deployment notification-service
kubectl rollout restart deployment audit-service

# Wait for pods to be ready
kubectl get pods -w
```

### Verify Dapr Kafka Integration

```bash
# Check backend Dapr logs
kubectl logs -l app=backend -c daprd | grep kafka

# Should see:
# "Component loaded: kafka-pubsub (pubsub.kafka/v1)"
```

### Check All Pods Healthy

```bash
kubectl get pods

# Expected:
# backend-service-xxx        2/2     Running
# notification-service-xxx   2/2     Running
# audit-service-xxx          2/2     Running
```

---

## Detailed ACL Permissions Explained

### Topic ACLs (for task-events, reminders, task-updates, recurring-tasks)

| Operation | Purpose | Required By |
|-----------|---------|-------------|
| **Read** | Consume messages from topic | notification-service, audit-service |
| **Write** | Produce messages to topic | backend-service |
| **Describe** | Get topic metadata (partitions, etc.) | All services |
| **Create** | Auto-create topics (if enabled) | Optional |

### Consumer Group ACL (for todo-service-group)

| Operation | Purpose | Required By |
|-----------|---------|-------------|
| **Read** | Join consumer group, commit offsets | notification-service, audit-service |
| **Describe** | Get consumer group metadata | All consumers |

### Host Setting

- **Host: `*`** - Allows access from any IP address
- **Host: `10.0.0.0/8`** - Restrict to specific IP range (if needed)

---

## Troubleshooting

### Error: "Topic authorization failed"

**Cause**: ACL not created or incorrect principal

**Solution**:
```bash
# Check ACLs
rpk security acl list

# Verify principal format is "User:todo-user" (case-sensitive)
```

### Error: "Group authorization failed"

**Cause**: Consumer group ACL missing

**Solution**:
```bash
rpk security acl create \
  --allow-principal User:todo-user \
  --operation all \
  --group todo-service-group
```

### Topics don't show up

**Cause**: Topics not created yet

**Solution**:
```bash
# List existing topics
rpk topic list

# Create missing topics
rpk topic create <topic-name> -p 3 -r 3
```

### ACLs not working after creation

**Cause**: ACL cache delay (usually seconds)

**Solution**: Wait 5-10 seconds and retry

---

## Production Best Practices

### Minimal Permissions (Instead of "All")

For better security, grant only required operations:

**For backend-service (producer)**:
```bash
rpk security acl create \
  --allow-principal User:todo-user \
  --operation write,describe \
  --topic task-events
```

**For notification/audit services (consumers)**:
```bash
rpk security acl create \
  --allow-principal User:todo-user \
  --operation read,describe \
  --topic reminders

rpk security acl create \
  --allow-principal User:todo-user \
  --operation read,describe \
  --group todo-service-group
```

### Separate Users for Different Services

Create separate SASL users:
- `todo-producer` - Write-only for backend
- `todo-consumer` - Read-only for notification/audit

### Enable Audit Logging

In Redpanda Cloud console:
- Enable audit logging to track ACL usage
- Monitor for unauthorized access attempts

---

## Quick Reference

### Required ACLs Summary

```
Resource Type | Resource Name      | Principal      | Operations      | Permission
------------- | ------------------ | -------------- | --------------- | ----------
Topic         | task-events        | User:todo-user | All (or R,W,D)  | Allow
Topic         | reminders          | User:todo-user | All (or R,W,D)  | Allow
Topic         | task-updates       | User:todo-user | All (or R,W,D)  | Allow
Topic         | recurring-tasks    | User:todo-user | All (or R,W,D)  | Allow
Group         | todo-service-group | User:todo-user | All (or R,D)    | Allow
```

### One-Line ACL Setup (using rpk)

```bash
# All topics
for t in task-events reminders task-updates recurring-tasks; do rpk security acl create --allow-principal User:todo-user --operation all --topic $t; done

# Consumer group
rpk security acl create --allow-principal User:todo-user --operation all --group todo-service-group
```

---

## Support Resources

- **Redpanda ACL Docs**: https://docs.redpanda.com/docs/manage/security/authorization/acl/
- **rpk ACL Reference**: https://docs.redpanda.com/docs/reference/rpk/rpk-security/rpk-security-acl/
- **Kafka ACL Concepts**: https://kafka.apache.org/documentation/#security_authz

---

**Created**: 2025-12-25
**Cluster**: d54l263rcoacstirud90.any.us-east-1.mpx.prd.cloud.redpanda.com
**User**: todo-user
**Status**: Ready to configure
