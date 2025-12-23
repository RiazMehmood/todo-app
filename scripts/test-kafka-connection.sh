#!/bin/bash
# Test Kafka connection via Dapr Pub/Sub
# This script verifies that Dapr can publish events to Redpanda Cloud

set -e

echo "🧪 Testing Kafka connection via Dapr..."
echo ""

# Check if running in Kubernetes context
if ! kubectl get pods &>/dev/null; then
    echo "❌ Not connected to Kubernetes cluster"
    exit 1
fi

# Check Dapr components
echo "📋 Checking Dapr components..."
kubectl get components kafka-pubsub statestore reminder-cron

# Check secrets
echo ""
echo "🔐 Checking secrets..."
kubectl get secret kafka-secrets db-secrets api-secrets

# Port-forward Dapr sidecar (if backend is running)
echo ""
echo "🔌 Checking for backend pods..."
BACKEND_POD=$(kubectl get pod -l app=backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$BACKEND_POD" ]; then
    echo "⚠️  No backend pod found. You need to deploy the backend first."
    echo ""
    echo "To deploy backend:"
    echo "  1. Build Docker image: docker build -t todo-backend:latest ./backend"
    echo "  2. Load to Minikube: minikube image load todo-backend:latest"
    echo "  3. Deploy: kubectl apply -f k8s/backend/deployment.yaml"
    exit 1
fi

echo "✅ Backend pod found: $BACKEND_POD"
echo ""

# Test publishing event via kubectl exec
echo "📤 Publishing test event to Kafka via Dapr..."
kubectl exec -it "$BACKEND_POD" -c daprd -- sh -c '
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d "{
    \"event_type\": \"test\",
    \"task_id\": 999,
    \"user_id\": \"test-user\",
    \"task_data\": {
      \"title\": \"Test Event\",
      \"description\": \"Testing Kafka connection\"
    },
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"metadata\": {
      \"source\": \"test-script\",
      \"version\": \"1.0\"
    }
  }"
'

echo ""
echo "✅ Test event published successfully!"
echo ""
echo "🔍 Verify in Redpanda Cloud Console:"
echo "   1. Go to https://redpanda.com/cloud"
echo "   2. Navigate to Topics → task-events"
echo "   3. Click 'Messages' tab"
echo "   4. You should see the test event"
