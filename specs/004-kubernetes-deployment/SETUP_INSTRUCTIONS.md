# Minikube Setup Instructions

## Step 1: Install Docker

Choose one of these methods:

### Option A: Install via Snap (Recommended)
```bash
sudo snap install docker
```

### Option B: Install via apt
```bash
sudo apt update
sudo apt install docker.io
```

### Option C: Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop/

## Step 2: Start Docker Service

```bash
# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to run without sudo)
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker

# Verify Docker is running
docker ps
```

## Step 3: Start Minikube

```bash
# Make sure Minikube is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Start Minikube with recommended settings
minikube start --cpus=2 --memory=4096 --disk-size=20g --driver=docker
```

This will take 2-5 minutes on first start as it downloads the Kubernetes images.

## Step 4: Enable Ingress Addon

```bash
minikube addons enable ingress
```

## Step 5: Verify Installation

```bash
# Check Minikube status
minikube status

# Check Kubernetes cluster
kubectl get nodes

# Check Ingress addon
minikube addons list | grep ingress

# Get Minikube IP
minikube ip
```

## Expected Output

After successful setup, you should see:

```bash
$ minikube status
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured

$ kubectl get nodes
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.3
```

## Troubleshooting

### Issue: Docker permission denied
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: Minikube start fails
```bash
# Check Docker is running
docker ps

# Try with verbose output
minikube start --cpus=2 --memory=4096 --disk-size=20g --driver=docker -v=7
```

### Issue: Out of memory
```bash
# Reduce memory allocation
minikube start --cpus=2 --memory=2048 --disk-size=20g --driver=docker
```

## Next Steps

After Minikube is running:

1. Build Docker images: `./scripts/build-images.sh`
2. Create secrets: See deployment guide
3. Deploy application: `./scripts/deploy-minikube.sh`

