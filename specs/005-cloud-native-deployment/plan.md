# Implementation Plan: Complete Redpanda Cloud Integration

**Branch**: `005-cloud-native-deployment` | **Date**: 2025-12-22 | **Spec**: [overview.md](./overview.md)
**Input**: Complete Redpanda Cloud integration - enable Kafka in backend, configure microservices, test event flow, and setup monitoring

## Summary

This plan completes the Redpanda Cloud integration for Phase V by:
1. Enabling Kafka event publishing in the backend deployment
2. Deploying microservices (notification-service, audit-service) to Kubernetes
3. Testing end-to-end event flow from API → Kafka → Consumers
4. Setting up monitoring in Redpanda Cloud console

**Current Status**: Redpanda cluster is configured, Dapr components deployed, Kubernetes running. Backend code has Kafka publishing (currently disabled via `KAFKA_ENABLED=false`).

**Technical Approach**: Enable the existing Kafka event publishing code by setting environment variables, deploy microservices with Dapr sidecars, and validate event flow through Redpanda Cloud console.

## Technical Context

**Language/Version**: Python 3.13+ (backend/services), Node.js 18+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Dapr SDK
- Services: Dapr gRPC, CloudEvents SDK
- Infrastructure: Kubernetes (Minikube), Dapr, Helm

**Storage**:
- Primary: Neon Serverless PostgreSQL (connection string in `.env`)
- Audit: PostgreSQL (AuditLog table in same database)
- Events: Redpanda Cloud Kafka (serverless, free tier)

**Testing**: Manual end-to-end testing (create task → verify events in Redpanda console → verify consumer logs)

**Target Platform**: Kubernetes (Minikube for local, cloud-ready for DOKS/GKE/AKS)

**Project Type**: Web application (Next.js frontend + FastAPI backend + Python microservices)

**Performance Goals**:
- Event publishing: <50ms overhead per API call
- Event consumption: <1s latency from publish to consumer processing
- No message loss or duplication

**Constraints**:
- Free tier limits: 10 GB/month storage, 10 MB/s throughput
- Minikube resource limits: 4GB RAM allocated
- All services must work with Kafka disabled (degraded mode)

**Scale/Scope**:
- 4 Kafka topics (task-events, task-updates, reminders, recurring-tasks)
- 3 services (backend, notification, audit)
- ~10-100 events/minute expected during testing

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Specification-First Development
**Status**: PASS
**Evidence**: Working from existing specs in `specs/005-cloud-native-deployment/` and PHASE_V_PROGRESS.md. This plan documents the completion approach.

### ✅ Principle II: Clean Architecture
**Status**: PASS
**Evidence**:
- Backend maintains separation: Models → Services → API routes
- Event publishing is isolated in `backend/src/events.py`
- Microservices are independent with clear responsibilities
- No circular dependencies

### ✅ Principle III: Code Quality Standards
**Status**: PASS
**Evidence**: Existing code follows PEP 8, uses descriptive names, feature flags for configuration.

### ✅ Principle IV: User-Friendly Error Handling
**Status**: PASS
**Evidence**:
- Kafka publishing wrapped in try/except with graceful degradation
- Services log errors without crashing
- User-facing errors don't expose Kafka internals

### ⚠️ Principle V: Test-Driven Development (TDD)
**Status**: ACCEPTABLE (tests optional per constitution)
**Evidence**: Manual testing via Redpanda Cloud console and service logs. Automated tests deferred to future work.

### ✅ Principle VI: Simplicity and YAGNI
**Status**: PASS
**Evidence**:
- Using existing Kafka publishing code (already written)
- Using existing Dapr components (already deployed)
- No new abstractions needed
- Feature flag allows disabling without code changes

**GATE RESULT**: ✅ PASS - All mandatory principles satisfied. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/004-kubernetes-deployment/
├── spec.md              # Feature specification (Kubernetes deployment)
├── plan.md              # This file (completion plan for Redpanda integration)
├── research.md          # Phase 0 output (environment variables, testing approach)
├── data-model.md        # Phase 1 output (event schemas, Kafka topics)
├── quickstart.md        # Phase 1 output (deployment steps, testing guide)
└── contracts/           # Phase 1 output (event message formats)
```

### Source Code (repository root)

```text
# Backend (existing - needs configuration update)
backend/
├── src/
│   ├── events.py        # ✅ Kafka publishing (complete, disabled)
│   ├── routes/tasks.py  # ✅ Integrated event calls (complete)
│   ├── models.py        # ✅ Task model with Phase V fields
│   └── main.py          # ✅ FastAPI app
└── Dockerfile           # ✅ Container image (complete)

# Microservices (existing - need deployment)
services/
├── notification-service/
│   ├── main.py          # ✅ Dapr consumer for reminders topic
│   ├── requirements.txt # ✅ Dependencies
│   └── Dockerfile       # ✅ Container image
└── audit-service/
    ├── main.py          # ✅ Dapr consumer for task-events + HTTP API
    ├── requirements.txt # ✅ Dependencies
    └── Dockerfile       # ✅ Container image

# Kubernetes (existing - need updates)
k8s/
├── dapr-components/     # ✅ Deployed (kafka-pubsub, statestore, reminder-cron)
├── backend/             # Needs: Update deployment.yaml with KAFKA_ENABLED=true
├── notification/        # Needs: Create deployment manifests
├── audit/               # Needs: Create deployment manifests
└── configmaps/          # Needs: Create with Kafka configuration

# Documentation (existing)
docs/
└── REDPANDA_SETUP.md    # ✅ Steps 1-8 complete, Steps 9-10 pending
```

**Structure Decision**: Web application (frontend + backend + microservices). All services are containerized and deployed to Kubernetes with Dapr sidecars for pub/sub communication.

## Complexity Tracking

> **No violations - this section left empty per template instructions**

---

## Phase 0: Outline & Research

### Unknowns from Technical Context

1. **Backend deployment configuration**: What environment variables are needed to enable Kafka? Where are they set in the existing deployment?
2. **Microservice deployment patterns**: What Kubernetes manifests are needed for Dapr-enabled services?
3. **Testing approach**: How to verify events are flowing end-to-end without automated tests?
4. **Monitoring setup**: What metrics and logs should we monitor in Redpanda Cloud console?

### Research Tasks

1. **Research: Backend Kafka enable configuration**
   - **Question**: How to enable Kafka in the backend deployment?
   - **Investigation**: Check `backend/src/events.py` for environment variables, check existing K8s manifests

2. **Research: Dapr sidecar annotations**
   - **Question**: What Kubernetes annotations are required for Dapr sidecars?
   - **Investigation**: Review Dapr documentation and existing patterns

3. **Research: Event flow testing best practices**
   - **Question**: How to test Kafka event flow without automated tests?
   - **Investigation**: Redpanda console features, kubectl logs patterns, manual test scenarios

4. **Research: Monitoring and observability**
   - **Question**: What should we monitor to ensure the system is healthy?
   - **Investigation**: Redpanda Cloud console features, Dapr logging, service health checks

### Research Output

✅ **Complete** - See `research.md` for detailed findings.

---

## Phase 1: Design & Contracts

### 1.1 Data Model

✅ **Complete** - See `data-model.md`
- Defined 4 Kafka topics with retention policies
- Defined 4 event schemas (task-events, reminders, task-updates, recurring-tasks)
- Defined 2 database entities (Task, AuditLog) with validation rules
- Documented event flows and state transitions

### 1.2 API Contracts

✅ **Complete** - See `contracts/` directory
- `task-event.schema.json` - JSON Schema for task CRUD events
- `reminder-event.schema.json` - JSON Schema for reminder events
- `recurring-task-event.schema.json` - JSON Schema for recurring task events
- `task-update-event.schema.json` - JSON Schema for real-time sync events

All schemas follow JSON Schema Draft 07 specification for validation.

### 1.3 Quickstart Guide

✅ **Complete** - See `quickstart.md`
- Step-by-step deployment instructions
- End-to-end testing procedures
- Troubleshooting guide with common issues
- Monitoring and observability checklist
- Reference commands for kubectl, Dapr, Docker

### 1.4 Agent Context Update

✅ **Complete**
- Updated `CLAUDE.md` with Python 3.13+ and Node.js 18+ technologies
- Added 004-kubernetes-deployment to active technologies

---

## Planning Complete

**Status**: ✅ All planning phases complete

**Artifacts Generated**:
1. ✅ `plan.md` - This implementation plan
2. ✅ `research.md` - Research findings and decisions
3. ✅ `data-model.md` - Event schemas and data entities
4. ✅ `contracts/` - JSON Schema files (4 schemas)
5. ✅ `quickstart.md` - Deployment and testing guide

**Next Steps**:
1. Run `/sp.tasks` to generate actionable tasks from this plan
2. Run `/sp.implement` to execute tasks
3. Follow quickstart.md for deployment

**Branch**: `005-cloud-native-deployment`
**Plan File**: `/home/riaz/Desktop/todo hackathon II/todo/specs/005-cloud-native-deployment/plan.md`

---

## Summary

This implementation plan completes the Redpanda Cloud integration by:
- ✅ Documenting existing configuration (Kafka already enabled)
- ✅ Defining event schemas and data models
- ✅ Creating JSON Schema contracts for validation
- ✅ Providing comprehensive deployment guide
- ✅ Identifying all remaining work (secrets, image builds, deployment, testing)

**Key Finding**: Most code is already complete. Remaining work is primarily operational (DevOps tasks like building images, creating secrets, deploying to Kubernetes, and testing).
