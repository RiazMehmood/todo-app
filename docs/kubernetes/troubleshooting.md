# Kubernetes Deployment Troubleshooting

Common issues and solutions for Todo app Kubernetes deployment.

## Pod Issues

### Pod in Pending State

**Symptoms**: Pod stays in `Pending` state

**Causes**:
- Insufficient resources
- Node not available
- PersistentVolumeClaim not bound

**Solutions**:
```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Check node resources
kubectl top nodes

# Check PVC status
kubectl get pvc -n todo-app
```

### Pod in CrashLoopBackOff

**Symptoms**: Pod restarts repeatedly

**Causes**:
- Application error
- Configuration issue
- Missing environment variables

**Solutions**:
```bash
# View pod logs
kubectl logs <pod-name> -n todo-app

# View previous container logs
kubectl logs <pod-name> -n todo-app --previous

# Check environment variables
kubectl exec <pod-name> -n todo-app -- env

# Describe pod for events
kubectl describe pod <pod-name> -n todo-app
```

### Pod Not Ready

**Symptoms**: Pod is `Running` but not `Ready`

**Causes**:
- Readiness probe failing
- Application not responding on probe path

**Solutions**:
```bash
# Check readiness probe configuration
kubectl describe pod <pod-name> -n todo-app | grep -A 5 Readiness

# Test probe endpoint manually
kubectl exec <pod-name> -n todo-app -- curl http://localhost:8000/health

# Temporarily disable probe for debugging (edit deployment)
kubectl edit deployment <deployment-name> -n todo-app
```

## Service Issues

### Service Not Accessible

**Symptoms**: Cannot connect to service from other pods

**Causes**:
- Service selector doesn't match pod labels
- Service port mismatch
- Network policy blocking traffic

**Solutions**:
```bash
# Verify service endpoints
kubectl get endpoints <service-name> -n todo-app

# Check service selector
kubectl get svc <service-name> -n todo-app -o yaml | grep selector

# Check pod labels match selector
kubectl get pods -n todo-app --show-labels
```

### Service Type Issues

**Symptoms**: Cannot access service from outside cluster

**Causes**:
- Using ClusterIP instead of NodePort/LoadBalancer
- Ingress not configured correctly

**Solutions**:
```bash
# Check service type
kubectl get svc -n todo-app

# Use port-forward for testing
kubectl port-forward svc/frontend-service 3000:80 -n todo-app

# Verify ingress configuration
kubectl get ingress -n todo-app
```

## Ingress Issues

### Ingress Not Routing

**Symptoms**: Cannot access app via http://todo.local

**Causes**:
- Ingress controller not running
- /etc/hosts not configured
- Ingress rules incorrect

**Solutions**:
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Verify ingress status
kubectl describe ingress -n todo-app

# Check /etc/hosts
cat /etc/hosts | grep todo.local

# Test ingress directly
curl -H "Host: todo.local" http://$(minikube ip)
```

## Configuration Issues

### ConfigMap/Secret Not Found

**Symptoms**: Pod fails with "configmap not found" error

**Causes**:
- ConfigMap/Secret not created
- Wrong namespace
- Wrong name reference

**Solutions**:
```bash
# List ConfigMaps
kubectl get configmap -n todo-app

# List Secrets
kubectl get secret -n todo-app

# Verify references in deployment
kubectl get deployment <name> -n todo-app -o yaml | grep -A 3 configMapKeyRef
```

### Environment Variables Not Set

**Symptoms**: Application uses wrong values

**Causes**:
- ConfigMap/Secret values incorrect
- Environment variable name mismatch

**Solutions**:
```bash
# Check environment variables in pod
kubectl exec <pod-name> -n todo-app -- env | grep -i database

# Verify ConfigMap values
kubectl get configmap <name> -n todo-app -o yaml

# Update ConfigMap
kubectl edit configmap <name> -n todo-app
# Restart pods to pick up changes
kubectl rollout restart deployment/<name> -n todo-app
```

## Image Issues

### ImagePullBackOff

**Symptoms**: Pod cannot pull Docker image

**Causes**:
- Image not found
- Wrong image name/tag
- Image not available to Minikube

**Solutions**:
```bash
# Verify image exists in Minikube
eval $(minikube docker-env)
docker images | grep todo

# Rebuild and tag images
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Set imagePullPolicy to IfNotPresent in deployment
kubectl edit deployment <name> -n todo-app
```

## Resource Issues

### Out of Memory

**Symptoms**: Pods killed, OOMKilled status

**Causes**:
- Resource limits too low
- Memory leak in application
- Too many pods for available resources

**Solutions**:
```bash
# Check resource usage
kubectl top pods -n todo-app

# Increase resource limits
kubectl edit deployment <name> -n todo-app
# Update resources.requests and resources.limits

# Check node resources
kubectl top nodes
```

### CPU Throttling

**Symptoms**: Slow application performance

**Causes**:
- CPU limits too low
- High CPU usage

**Solutions**:
```bash
# Check CPU usage
kubectl top pods -n todo-app

# Increase CPU limits
kubectl edit deployment <name> -n todo-app
```

## Database Connection Issues

### Cannot Connect to Database

**Symptoms**: Backend logs show database connection errors

**Causes**:
- Wrong DATABASE_URL
- Database not accessible from cluster
- Network policy blocking

**Solutions**:
```bash
# Verify DATABASE_URL in secret
kubectl get secret backend-secrets -n todo-app -o jsonpath='{.data.database_url}' | base64 -d

# Test connection from pod
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -- psql $DATABASE_URL

# Check backend logs
kubectl logs deployment/backend -n todo-app | grep -i database
```

## Helm Issues

### Helm Install Fails

**Symptoms**: `helm install` command fails

**Causes**:
- Invalid values.yaml
- Missing required values
- Chart syntax error

**Solutions**:
```bash
# Validate chart
helm lint ./helm-chart

# Dry-run to see what would be created
helm install todo-app ./helm-chart --dry-run --debug

# Check template rendering
helm template ./helm-chart
```

### Helm Upgrade Fails

**Symptoms**: `helm upgrade` doesn't apply changes

**Causes**:
- Values not updated
- Chart version not changed

**Solutions**:
```bash
# Check current values
helm get values todo-app -n todo-app

# Upgrade with new values
helm upgrade todo-app ./helm-chart --set <key>=<value>

# Force upgrade
helm upgrade todo-app ./helm-chart --force
```

## Getting Help

### Useful Commands

```bash
# Get all resources in namespace
kubectl get all -n todo-app

# Describe any resource
kubectl describe <resource-type> <name> -n todo-app

# View events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Check Minikube status
minikube status
minikube logs
```

### Debug Pod

```bash
# Create debug pod
kubectl run -it --rm debug --image=busybox --restart=Never -n todo-app -- sh

# From debug pod, test connectivity
wget -O- http://backend-service:8000/health
nslookup backend-service
```

