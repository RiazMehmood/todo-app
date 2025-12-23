# Docker Build Guide

Guide for building Docker images for the Todo application.

## Prerequisites

- Docker Desktop 4.53+ or Docker Engine
- Node.js 18+ (for frontend builds)
- Python 3.12+ (for backend builds)

## Frontend Build

### Multi-Stage Build

The frontend Dockerfile uses a multi-stage build:

1. **deps stage**: Installs npm dependencies
2. **builder stage**: Builds Next.js application
3. **runner stage**: Production runtime with minimal image

### Build Command

```bash
cd frontend

# Basic build
docker build -t todo-frontend:latest .

# Build with specific tag
docker build -t todo-frontend:v2.0.2 .

# Build with build arguments (if needed)
docker build --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 -t todo-frontend:latest .
```

### Build for Minikube

```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build image (will be available to Minikube)
docker build -t todo-frontend:latest ./frontend

# Verify image
docker images | grep todo-frontend
```

## Backend Build

### Multi-Stage Build

The backend Dockerfile uses a multi-stage build:

1. **deps stage**: Installs Python dependencies using UV
2. **builder stage**: Copies application code
3. **runner stage**: Production runtime with minimal dependencies

### Build Command

```bash
cd backend

# Basic build
docker build -t todo-backend:latest .

# Build with specific tag
docker build -t todo-backend:v2.0.0 .

# Build with cache (faster rebuilds)
docker build --cache-from todo-backend:latest -t todo-backend:latest .
```

### Build for Minikube

```bash
# Point Docker to Minikube
eval $(minikube docker-env)

# Build image
docker build -t todo-backend:latest ./backend

# Verify image
docker images | grep todo-backend
```

## Build Optimization

### Layer Caching

Dockerfiles are optimized for layer caching:
- Dependencies installed before code copy
- Code changes don't invalidate dependency cache

### Image Size Optimization

- Multi-stage builds reduce final image size
- Alpine base images for minimal footprint
- Only production dependencies in final stage

### Build Time Optimization

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t todo-frontend:latest ./frontend

# Parallel builds
docker build -t todo-frontend:latest ./frontend &
docker build -t todo-backend:latest ./backend &
wait
```

## Testing Images Locally

### Run Frontend

```bash
# Run with environment variable
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:latest

# Access at http://localhost:3000
```

### Run Backend

```bash
# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e BETTER_AUTH_SECRET="secret" \
  -e CORS_ORIGINS="http://localhost:3000" \
  todo-backend:latest

# Access at http://localhost:8000
# Health check at http://localhost:8000/health
```

## Troubleshooting

### Build Fails: Dependencies

```bash
# Clear build cache
docker builder prune

# Rebuild without cache
docker build --no-cache -t todo-frontend:latest ./frontend
```

### Build Fails: Out of Memory

```bash
# Increase Docker memory limit (Docker Desktop settings)
# Or use build with less parallelism
docker build --progress=plain -t todo-frontend:latest ./frontend
```

### Image Too Large

```bash
# Check image size
docker images | grep todo

# Analyze image layers
docker history todo-frontend:latest

# Use .dockerignore to exclude unnecessary files
```

## Best Practices

1. **Use .dockerignore**: Exclude node_modules, .git, etc.
2. **Multi-stage builds**: Separate build and runtime
3. **Layer ordering**: Install dependencies before copying code
4. **Tag images**: Use version tags, not just `latest`
5. **Scan images**: Use `docker scan` to check for vulnerabilities

## Next Steps

After building images:
1. Test images locally
2. Build for Minikube (if using Minikube)
3. Deploy to Kubernetes (see deployment guide)

