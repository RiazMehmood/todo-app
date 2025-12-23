#!/bin/bash
# Quick Kafka Connection Test
# Tests Dapr Pub/Sub component without deploying full application

set -e

echo "🧪 Quick Kafka Connection Test"
echo "================================"
echo ""

# Check components
echo "📋 Step 1: Verify Dapr components are loaded..."
if kubectl get component kafka-pubsub &>/dev/null; then
    echo "✅ kafka-pubsub component found"
else
    echo "❌ kafka-pubsub component not found"
    exit 1
fi

# Check secrets
echo ""
echo "🔐 Step 2: Verify Kafka secrets exist..."
if kubectl get secret kafka-secrets &>/dev/null; then
    echo "✅ kafka-secrets found"
    kubectl get secret kafka-secrets -o jsonpath='{.data}' | grep -o '"[^"]*":' | tr -d '":' | xargs -I {} echo "   - {}"
else
    echo "❌ kafka-secrets not found"
    exit 1
fi

# Get Dapr operator pod
echo ""
echo "🔍 Step 3: Finding Dapr sidecar injector..."
DAPR_POD=$(kubectl get pod -n dapr-system -l app=dapr-sidecar-injector -o jsonpath='{.items[0].metadata.name}')
echo "✅ Found: $DAPR_POD"

echo ""
echo "📊 Component Status:"
kubectl get component kafka-pubsub -o yaml | grep -A 10 "spec:"

echo ""
echo "✅ All checks passed!"
echo ""
echo "📝 Next Steps:"
echo "  1. Build backend Docker image:"
echo "     cd backend && docker build -t todo-backend:latest ."
echo ""
echo "  2. Load image to Minikube:"
echo "     minikube image load todo-backend:latest"
echo ""
echo "  3. Deploy backend:"
echo "     kubectl apply -f k8s/backend/deployment.yaml"
echo ""
echo "  4. Test event publishing:"
echo "     ./scripts/test-kafka-connection.sh"
