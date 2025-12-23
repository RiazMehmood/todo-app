# kubectl-ai and kagent Usage Guide

Guide for using AI-powered tools to manage Kubernetes clusters.

## kubectl-ai

kubectl-ai is a kubectl plugin that translates natural language queries into kubectl commands using AI.

### Installation

#### Using Krew (Recommended)

```bash
# Install Krew if not already installed
(
  set -x; cd "$(mktemp -d)" &&
  OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
  ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
  KREW="krew-${OS}_${ARCH}" &&
  curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
  tar zxvf "${KREW}.tar.gz" &&
  ./"${KREW}" install krew
)

# Add Krew to PATH
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

# Install kubectl-ai
kubectl krew install ai
```

#### Manual Installation

```bash
# Download kubectl-ai
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-linux-amd64

# Make executable and move to PATH
chmod +x kubectl-ai-linux-amd64
sudo mv kubectl-ai-linux-amd64 /usr/local/bin/kubectl-ai
```

### Configuration

kubectl-ai requires an AI provider API key:

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or set Anthropic API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or use Azure OpenAI
export AZURE_OPENAI_ENDPOINT="https://your-endpoint.openai.azure.com"
export AZURE_OPENAI_API_KEY="your-api-key"
```

### Usage Examples

#### Basic Queries

```bash
# Show all running pods
kubectl ai "Show me all running pods"

# List pods in a namespace
kubectl ai "List all pods in the todo-app namespace"

# Get pod logs
kubectl ai "Show me logs for the backend pod in todo-app namespace"

# Describe a resource
kubectl ai "Describe the frontend deployment in todo-app"
```

#### Troubleshooting Queries

```bash
# Find failing pods
kubectl ai "Show me pods that are not running"

# Check pod status
kubectl ai "Why is the backend pod failing?"

# View recent events
kubectl ai "Show me recent events in todo-app namespace"

# Check resource usage
kubectl ai "What's using the most memory in todo-app namespace?"
```

#### Management Queries

```bash
# Scale deployments
kubectl ai "Scale the frontend deployment to 3 replicas in todo-app namespace"

# Update image
kubectl ai "Update the backend image to version 2.1.0 in todo-app namespace"

# Delete resources
kubectl ai "Delete all pods in todo-app namespace that are in Error state"

# Get service endpoints
kubectl ai "Show me all service endpoints in todo-app namespace"
```

#### Resource Analysis

```bash
# Resource usage
kubectl ai "What's the CPU and memory usage for all pods in todo-app?"

# Find large resources
kubectl ai "Show me the largest deployments by replica count"

# Check resource limits
kubectl ai "List all pods that have resource limits set"
```

### Best Practices

1. **Be Specific**: Include namespace names in queries
2. **Use Context**: Mention resource types (pods, deployments, services)
3. **Verify Commands**: Review generated commands before execution
4. **Test First**: Use `--dry-run` when possible
5. **Check Output**: Verify AI-generated commands match your intent

### Limitations

- Requires internet connection for AI API calls
- May generate incorrect commands for complex scenarios
- API costs apply (OpenAI, Anthropic, etc.)
- Not suitable for production automation without review

## kagent

kagent is an intelligent Kubernetes agent that provides troubleshooting recommendations and cluster insights.

### Installation

```bash
# Install via Homebrew (macOS)
brew install kagent

# Or download from releases
curl -LO https://github.com/kagent-io/kagent/releases/latest/download/kagent-linux-amd64
chmod +x kagent-linux-amd64
sudo mv kagent-linux-amd64 /usr/local/bin/kagent
```

### Configuration

```bash
# Set API key (if required)
export KAGENT_API_KEY="your-api-key"

# Configure cluster access
kagent config set cluster-name my-cluster
```

### Usage Examples

#### Troubleshooting

```bash
# Diagnose pod issues
kagent diagnose pod backend-xxx -n todo-app

# Analyze deployment problems
kagent analyze deployment frontend -n todo-app

# Check cluster health
kagent health-check
```

#### Recommendations

```bash
# Get optimization recommendations
kagent recommend optimize -n todo-app

# Security recommendations
kagent recommend security -n todo-app

# Resource optimization
kagent recommend resources -n todo-app
```

#### Monitoring

```bash
# Monitor pod status
kagent monitor pods -n todo-app

# Watch for issues
kagent watch -n todo-app

# Get cluster insights
kagent insights
```

### Integration with kubectl-ai

You can combine both tools:

```bash
# Use kubectl-ai to generate command, then kagent to analyze
kubectl ai "Show me failing pods" | kagent analyze
```

## Common Workflows

### Workflow 1: Diagnose Failing Pod

```bash
# Step 1: Find failing pods
kubectl ai "Show me pods in Error or CrashLoopBackOff state in todo-app"

# Step 2: Get detailed diagnosis
kagent diagnose pod <pod-name> -n todo-app

# Step 3: View logs
kubectl ai "Show me logs for <pod-name> in todo-app namespace"

# Step 4: Check events
kubectl ai "Show me recent events for <pod-name> in todo-app"
```

### Workflow 2: Scale Application

```bash
# Step 1: Check current state
kubectl ai "Show me current replica count for frontend deployment in todo-app"

# Step 2: Scale up
kubectl ai "Scale frontend deployment to 3 replicas in todo-app namespace"

# Step 3: Monitor rollout
kagent monitor deployment frontend -n todo-app
```

### Workflow 3: Update Application

```bash
# Step 1: Check current version
kubectl ai "What image is the backend deployment using in todo-app?"

# Step 2: Update image
kubectl ai "Update backend deployment image to version 2.1.0 in todo-app namespace"

# Step 3: Monitor update
kagent analyze deployment backend -n todo-app
```

## Troubleshooting AI Tools

### kubectl-ai Issues

**Problem**: Command not found
```bash
# Verify installation
kubectl krew list | grep ai

# Reinstall if needed
kubectl krew install ai
```

**Problem**: API key not working
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connection
curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Problem**: Incorrect commands generated
- Be more specific in queries
- Include namespace and resource type
- Review command before executing
- Use `--dry-run` flag when available

### kagent Issues

**Problem**: Cannot connect to cluster
```bash
# Verify kubectl access
kubectl cluster-info

# Check kagent configuration
kagent config show
```

**Problem**: No recommendations
- Ensure cluster has metrics-server enabled
- Check resource usage data is available
- Verify kagent has proper permissions

## Success Criteria Validation

### kubectl-ai 80% Success Rate

Test with 10 common queries and verify correct command generation:

1. "Show me all running pods" → `kubectl get pods --field-selector=status.phase=Running`
2. "List services in todo-app" → `kubectl get svc -n todo-app`
3. "Scale frontend to 3" → `kubectl scale deployment frontend --replicas=3 -n todo-app`
4. "Show backend logs" → `kubectl logs deployment/backend -n todo-app`
5. "Describe frontend pod" → `kubectl describe pod <name> -n todo-app`
6. "What's using memory?" → `kubectl top pods -n todo-app`
7. "Delete failed pods" → `kubectl delete pods --field-selector=status.phase=Failed -n todo-app`
8. "Update image to v2.0" → `kubectl set image deployment/backend backend=image:v2.0 -n todo-app`
9. "Show ingress" → `kubectl get ingress -n todo-app`
10. "Check pod events" → `kubectl get events -n todo-app`

### kagent 10-Second Response Time

Test troubleshooting scenarios:

1. Pod in CrashLoopBackOff → kagent should diagnose within 10 seconds
2. Service not accessible → kagent should identify issue quickly
3. Resource exhaustion → kagent should provide recommendations promptly

## Next Steps

1. Install kubectl-ai and kagent
2. Configure API keys
3. Test with sample queries
4. Integrate into daily workflow
5. Document team-specific queries and workflows

