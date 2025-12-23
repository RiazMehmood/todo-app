# Phase V: Advanced Cloud Deployment - Overview

## Purpose
Deploy a production-grade, cloud-native todo chatbot application with advanced features, event-driven architecture using Kafka, and Dapr for distributed application runtime on Kubernetes.

## Phase Information
- **Phase**: V - Advanced Cloud Deployment
- **Due Date**: January 18, 2026
- **Points**: 300
- **Status**: 🚧 In Progress

## Objectives

### Part A: Advanced Features
Implement comprehensive task management capabilities:
- **Advanced Level**: Recurring Tasks, Due Dates & Time Reminders
- **Intermediate Level**: Priorities, Tags/Categories, Search, Filter, Sort

### Part B: Event-Driven Architecture
- Kafka integration via Redpanda Cloud
- Event-driven communication between services
- Async processing for reminders and notifications

### Part C: Dapr Integration
Implement all Dapr building blocks:
- **Pub/Sub**: Kafka abstraction for event streaming
- **State Management**: Conversation and task state storage
- **Bindings**: Cron triggers for scheduled reminders
- **Secrets Management**: Secure API keys and credentials
- **Service Invocation**: Inter-service communication

### Part D: Deployment
1. **Local (Minikube)**:
   - Deploy with Helm charts
   - Configure Dapr components
   - Test locally before cloud deployment

2. **Cloud (DOKS/GKE/AKS)**:
   - Production Kubernetes deployment
   - Redpanda Cloud for Kafka
   - CI/CD with GitHub Actions
   - Monitoring and logging

## Technology Stack

### Core Application
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **AI**: OpenAI Agents SDK, MCP Server

### Cloud-Native Stack
- **Message Broker**: Kafka (Redpanda Cloud)
- **Runtime**: Dapr (Distributed Application Runtime)
- **Orchestration**: Kubernetes (Minikube local, DOKS/GKE/AKS cloud)
- **Package Manager**: Helm Charts
- **CI/CD**: GitHub Actions
- **Containerization**: Docker

### AIOps Tools
- **Docker AI**: Gordon (Docker AI Agent)
- **Kubernetes AI**: kubectl-ai, kagent

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (DOKS/GKE/AKS)            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Frontend Pod │  │ Backend Pod  │  │ Notif Pod    │         │
│  │              │  │              │  │              │         │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │         │
│  │ │Next.js   │ │  │ │FastAPI   │ │  │ │Notif     │ │         │
│  │ │+ Dapr    │◄┼──┼►│+ MCP     │ │  │ │Service   │ │         │
│  │ │Sidecar   │ │  │ │+ Dapr    │ │  │ │+ Dapr    │ │         │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                   │                  │                │
│         └───────────────────┼──────────────────┘                │
│                             │                                   │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │              Dapr Components                             │  │
│  │  ┌──────────────────┐  ┌─────────────────┐              │  │
│  │  │ pubsub.kafka     │──┼──► Redpanda     │              │  │
│  │  ├──────────────────┤  │    Cloud        │              │  │
│  │  │ state.postgresql │──┼──► Neon DB      │              │  │
│  │  ├──────────────────┤  │                 │              │  │
│  │  │ bindings.cron    │  │                 │              │  │
│  │  ├──────────────────┤  │                 │              │  │
│  │  │ secretstores.k8s │  │                 │              │  │
│  │  └──────────────────┘  └─────────────────┘              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features to Implement

### 1. Advanced Features
- **Recurring Tasks**: Daily, weekly, monthly patterns
- **Due Dates**: DateTime with timezone support
- **Reminders**: Email/push notifications before due date
- **Priorities**: High, Medium, Low with visual indicators
- **Tags/Categories**: Multi-tag support (work, personal, urgent)
- **Search**: Full-text search across title and description
- **Filter**: By status, priority, tags, due date
- **Sort**: By due date, priority, created date, title

### 2. Event-Driven Architecture
- **Kafka Topics**:
  - `task-events`: Task CRUD operations
  - `reminders`: Scheduled reminder triggers
  - `task-updates`: Real-time client sync
  - `recurring-tasks`: Recurring task processing

### 3. Microservices
- **Chat API Service**: Main API with MCP tools
- **Notification Service**: Consumes reminder events
- **Recurring Task Service**: Processes recurring task creation
- **Audit Service**: Logs all task operations

### 4. Dapr Building Blocks
- **Pub/Sub**: Kafka integration without direct kafka-python dependency
- **State**: Conversation history and task cache
- **Bindings**: Cron triggers for reminder checks
- **Secrets**: OpenAI API keys, database credentials
- **Service Invocation**: Frontend ↔ Backend communication

## Success Criteria

### Part A: Advanced Features
- ✅ Users can create recurring tasks
- ✅ Users can set due dates with time
- ✅ Users receive reminders before due date
- ✅ Users can assign priorities and tags
- ✅ Users can search, filter, and sort tasks

### Part B: Local Deployment
- ✅ Application runs on Minikube
- ✅ Dapr components configured and working
- ✅ All services communicate via Dapr
- ✅ Events flow through local Kafka

### Part C: Cloud Deployment
- ✅ Application deployed on DOKS/GKE/AKS
- ✅ Connected to Redpanda Cloud
- ✅ CI/CD pipeline deploys on push
- ✅ Monitoring and logging configured
- ✅ Application accessible via public URL

## Development Workflow

1. **Specify**: Create detailed specifications for each feature
2. **Implement Advanced Features**: Add to existing backend/frontend
3. **Set up Kafka**: Create Redpanda Cloud account and topics
4. **Integrate Dapr**: Add Dapr components and update code
5. **Local Deploy**: Test on Minikube
6. **Cloud Deploy**: Deploy to DOKS/GKE/AKS
7. **CI/CD**: Set up GitHub Actions
8. **Document**: Create PHR for Phase V

## Timeline Estimate

- **Advanced Features**: 3-5 days
- **Kafka Integration**: 2-3 days
- **Dapr Integration**: 2-3 days
- **Local Deployment**: 1-2 days
- **Cloud Deployment**: 2-3 days
- **CI/CD Setup**: 1-2 days
- **Testing & Documentation**: 1-2 days

**Total**: ~14-20 days (Complete by Jan 18, 2026)

## References

- [Hackathon II Documentation](../../Hackathon II - Todo Spec-Driven Development.pdf)
- [Phase IV Kubernetes Deployment](../004-kubernetes-deployment/)
- [Redpanda Cloud](https://redpanda.com/cloud)
- [Dapr Documentation](https://docs.dapr.io)
- [kubectl-ai](https://github.com/sozercan/kubectl-ai)
- [kagent](https://github.com/ktruckload/kagent)
