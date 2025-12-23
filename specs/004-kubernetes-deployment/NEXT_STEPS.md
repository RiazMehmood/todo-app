# Next Steps - Kubernetes Deployment

**Last Updated**: After completing Docker installation and Minikube startup

## ✅ Completed

- [X] T006: Minikube installed (v1.37.0)
- [X] Docker installed and running
- [X] Minikube cluster started with recommended settings (2 CPUs, 4GB RAM, 20GB disk)
- [X] T007: Ingress addon enabled
- [X] T010: Docker environment configured for Minikube
- [X] T011: Frontend Docker image built successfully
- [X] T012: Backend Docker image built successfully
- [X] T029: /etc/hosts configured for todo.local
- [X] T030: All Kubernetes manifests deployed
- [X] T031: Pods deployed and running (both frontend and backend are Ready)
- [X] Secrets updated with real database URL, OpenAI API key, and Gemini API key
- [X] T032: Application tested - Login working successfully at http://todo.local
- [X] Frontend API URL configuration fixed for Kubernetes deployment
- [X] Ingress routing configured correctly

## 🔄 Ready to Continue

When you're ready to proceed, run these commands in order:

### Step 6: Enable Ingress Addon (T007)

```bash
export PATH="$HOME/.local/bin:$PATH"
minikube addons enable ingress
```

Verify it's enabled:
```bash
minikube addons list | grep ingress
```

### Step 7: Configure Docker Environment (T010)

Point Docker to Minikube's Docker daemon:
```bash
eval $(minikube docker-env)
docker ps  # Should show Minikube containers
```

### Step 8: Build Docker Images (T011, T012)

```bash
# Make sure you're in the project root
cd /home/riaz/Desktop/todo\ hackathon\ II/todo

# Build images (will use Minikube's Docker)
./scripts/build-images.sh
```

Or manually:
```bash
eval $(minikube docker-env)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# Verify images
docker images | grep todo
```

### Step 9: Deploy Application

After images are built, you can deploy using either:

**Option A: Using Helm (Recommended)**
```bash
# Create secrets first (replace with actual values)
kubectl create secret generic backend-secrets \
  --from-literal=database_url="postgresql://user:pass@host:5432/dbname" \
  --from-literal=better_auth_secret="your-jwt-secret" \
  --namespace=todo-app

# Deploy with Helm
./scripts/deploy-minikube.sh
```

**Option B: Using Raw Kubernetes Manifests**
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=database_url="postgresql://..." \
  --from-literal=better_auth_secret="..." \
  --namespace=todo-app

# Deploy manifests
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/ingress.yaml
```

### Step 10: Configure Local Access

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"

# Add to /etc/hosts
echo "$MINIKUBE_IP todo.local" | sudo tee -a /etc/hosts
```

### Step 11: Verify Deployment

```bash
# Check pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check ingress
kubectl get ingress -n todo-app

# Access application
# Open http://todo.local in browser
```

## 📋 Quick Reference

**Current State:**
- ✅ Minikube: Running
- ✅ Docker: Running
- ⏳ Ingress: Not enabled yet
- ⏳ Images: Not built yet
- ⏳ Deployment: Not deployed yet

**Next Command to Run:**
```bash
export PATH="$HOME/.local/bin:$PATH"
minikube addons enable ingress
```

## 📝 Notes

- Make sure Docker is accessible (you may need to run `newgrp docker` if you just added yourself to docker group)
- All images must be built using Minikube's Docker daemon (`eval $(minikube docker-env)`)
- Secrets need actual values (not placeholders) before deployment
- Database should point to your Neon PostgreSQL connection string

## 🆘 If You Need Help

- Check `docs/kubernetes/deployment-guide.md` for detailed instructions
- Check `docs/kubernetes/troubleshooting.md` for common issues
- Run `minikube status` to verify cluster health
- Run `kubectl get nodes` to verify cluster connectivity

