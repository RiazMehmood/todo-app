# Minikube Setup Guide

This guide walks you through setting up Minikube for local Kubernetes development.

## Prerequisites

- Docker Desktop 4.53+ (or Docker Engine)
- 4GB+ RAM available for Minikube
- 2+ CPU cores
- 20GB+ free disk space

## Installation

### Linux

```bash
# Download and install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Verify installation
minikube version
```

### macOS

```bash
# Using Homebrew
brew install minikube

# Or download directly
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
```

### Windows

```powershell
# Using Chocolatey
choco install minikube

# Or download from: https://minikube.sigs.k8s.io/docs/start/
```

## Starting Minikube

### Basic Start

```bash
# Start with default settings (2 CPUs, 2GB RAM)
minikube start
```

### Recommended Configuration

```bash
# Start with recommended resources for Todo app
minikube start \
  --cpus=2 \
  --memory=4096 \
  --disk-size=20g \
  --driver=docker
```

### Driver Options

- **Docker** (recommended): `--driver=docker` - Uses Docker Desktop
- **VirtualBox**: `--driver=virtualbox` - Requires VirtualBox installation
- **Hyper-V** (Windows): `--driver=hyperv` - Windows native virtualization

## Enable Required Addons

```bash
# Enable NGINX Ingress Controller (required for external access)
minikube addons enable ingress

# Enable metrics-server (optional, for resource monitoring)
minikube addons enable metrics-server

# List enabled addons
minikube addons list
```

## Verify Installation

```bash
# Check cluster status
minikube status

# Verify kubectl is configured
kubectl get nodes

# Check cluster info
kubectl cluster-info
```

## Configure Docker Environment

To build Docker images that Minikube can access:

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker ps

# Build images (they'll be available to Minikube)
docker build -t todo-frontend:latest ./frontend
docker build -t todo-backend:latest ./backend

# To switch back to your local Docker
eval $(minikube docker-env -u)
```

## Accessing Minikube

### Get Minikube IP

```bash
minikube ip
```

### Access Services

```bash
# Open Minikube dashboard
minikube dashboard

# Get service URL
minikube service <service-name> -n <namespace>

# Tunnel for LoadBalancer services
minikube tunnel
```

## Stopping and Deleting

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster
minikube delete

# Delete all Minikube clusters
minikube delete --all
```

## Troubleshooting

### Issue: Minikube won't start

```bash
# Check logs
minikube logs

# Reset Minikube
minikube delete
minikube start --cpus=2 --memory=4096
```

### Issue: Out of memory

```bash
# Reduce memory allocation
minikube stop
minikube start --memory=2048
```

### Issue: Ingress not working

```bash
# Verify ingress addon is enabled
minikube addons list | grep ingress

# Re-enable if needed
minikube addons disable ingress
minikube addons enable ingress
```

## Next Steps

After Minikube is running:

1. Build Docker images (see Docker build guide)
2. Deploy using Helm chart (see deployment guide)
3. Configure /etc/hosts for todo.local access

