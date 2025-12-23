# Todo App Helm Chart

This Helm chart deploys the Todo Application (Next.js frontend + FastAPI backend) to Kubernetes.

## Prerequisites

- Kubernetes 1.28+
- Helm 3.x
- Minikube (for local development)
- NGINX Ingress Controller (enabled in Minikube)

## Installation

### Basic Installation

```bash
# Install with default values
helm install todo-app ./helm-chart

# Install with custom namespace
helm install todo-app ./helm-chart --namespace todo-app --create-namespace

# Install with development values
helm install todo-app ./helm-chart -f values.dev.yaml
```

### Custom Configuration

```bash
# Override specific values
helm install todo-app ./helm-chart \
  --set backend.secrets.database_url="postgresql://..." \
  --set backend.secrets.better_auth_secret="your-secret"
```

## Configuration

### Required Values

- `backend.secrets.database_url`: PostgreSQL connection string
- `backend.secrets.better_auth_secret`: JWT secret key

### Optional Values

See `values.yaml` for all configurable options including:
- Resource requests/limits
- Replica counts
- Image tags
- Ingress hostname
- PostgreSQL configuration (if using in-cluster database)

## Upgrading

```bash
# Upgrade with new values
helm upgrade todo-app ./helm-chart -f values.dev.yaml

# Upgrade with specific overrides
helm upgrade todo-app ./helm-chart \
  --set frontend.image.tag=v2.1.0
```

## Rollback

```bash
# List releases
helm list

# Rollback to previous version
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 2
```

## Uninstallation

```bash
helm uninstall todo-app
```

## Local Development with Minikube

1. Start Minikube:
   ```bash
   minikube start --cpus=2 --memory=4096
   ```

2. Enable Ingress:
   ```bash
   minikube addons enable ingress
   ```

3. Build Docker images:
   ```bash
   eval $(minikube docker-env)
   docker build -t todo-frontend:latest ./frontend
   docker build -t todo-backend:latest ./backend
   ```

4. Install Helm chart:
   ```bash
   helm install todo-app ./helm-chart \
     --set backend.secrets.database_url="your-neon-db-url" \
     --set backend.secrets.better_auth_secret="your-secret"
   ```

5. Configure /etc/hosts:
   ```bash
   echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts
   ```

6. Access application:
   Open http://todo.local in your browser

## Troubleshooting

- Check pod status: `kubectl get pods -n todo-app`
- View logs: `kubectl logs -n todo-app <pod-name>`
- Describe pod: `kubectl describe pod -n todo-app <pod-name>`
- Check services: `kubectl get svc -n todo-app`
- Check ingress: `kubectl get ingress -n todo-app`

