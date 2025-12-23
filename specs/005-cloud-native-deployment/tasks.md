---
description: "Actionable tasks for completing Redpanda Cloud integration"
---

# Tasks: Complete Redpanda Cloud Integration

**Input**: Design documents from `/specs/004-kubernetes-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Manual end-to-end testing (automated tests optional per constitution)

**Organization**: Tasks organized to complete Redpanda Cloud event-driven architecture integration

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Services**: `services/notification-service/`, `services/audit-service/`
- **Kubernetes**: `k8s/`
- **Documentation**: `docs/`, `specs/004-kubernetes-deployment/`

---

## Phase 1: Setup & Verification

**Purpose**: Verify prerequisites and environment readiness

- [X] T001 Verify Minikube is running and accessible (check `minikube status`)
- [X] T002 Verify Dapr installed in cluster (check `kubectl get pods -n dapr-system`)
- [X] T003 Verify Dapr components deployed (check kafka-pubsub, statestore, reminder-cron exist)
- [X] T004 Verify Redpanda Cloud cluster accessible (check Redpanda Cloud console shows 4 topics)
- [X] T005 Verify kafka-secrets exists in Kubernetes (check `kubectl get secret kafka-secrets`)

**Checkpoint**: Prerequisites verified - ready to create additional secrets and build images

---

## Phase 2: Foundational (Secrets & Images)

**Purpose**: Create Kubernetes secrets and build Docker images for all services

**⚠️ CRITICAL**: These must be complete before deployment can begin

### Secrets Creation

- [X] T006 Create db-secrets in Kubernetes with DATABASE_URL from .env file
- [X] T007 Create api-secrets in Kubernetes with BETTER_AUTH_SECRET from .env file
- [X] T008 Create email-secrets in Kubernetes with placeholder sendgridApiKey (optional)
- [X] T009 Verify all secrets created (db-secrets, api-secrets, email-secrets, kafka-secrets)

### Docker Image Builds

**Note**: Run `eval $(minikube docker-env)` before building to use Minikube's Docker daemon

- [X] T010 [P] Build backend Docker image: `docker build -t todo-backend:latest ./backend`
- [X] T011 [P] Build notification-service Docker image: `docker build -t todo-notification:latest ./services/notification-service`
- [X] T012 [P] Build audit-service Docker image: `docker build -t todo-audit:latest ./services/audit-service`
- [X] T013 Verify all images built successfully (check `docker images | grep todo`)

**Checkpoint**: Foundation ready - all secrets and images available for deployment

---

## Phase 3: User Story 1 - Complete Redpanda Integration (Priority: P1) 🎯 MVP

**Goal**: Deploy all services to Kubernetes with Kafka event publishing enabled, verify end-to-end event flow from API → Redpanda → Consumer services

**Independent Test**: Create a task via API, verify event appears in Redpanda Cloud console task-events topic, verify audit-service logs show event consumed, verify audit database record created

### Service Deployments

- [ ] T014 Deploy backend-service to Kubernetes: `kubectl apply -f k8s/backend/deployment.yaml`
- [ ] T015 Wait for backend-service rollout to complete: `kubectl rollout status deployment/backend-service`
- [ ] T016 Verify backend-service pods running (2/2 containers: app + Dapr sidecar)
- [ ] T017 [P] Deploy notification-service to Kubernetes: `kubectl apply -f k8s/notification-service/deployment.yaml`
- [ ] T018 [P] Deploy audit-service to Kubernetes: `kubectl apply -f k8s/audit-service/deployment.yaml`
- [ ] T019 Verify all service pods running with status 2/2 (app + Dapr sidecar each)
- [ ] T020 Check for any pod errors or CrashLoopBackOff (troubleshoot if needed per quickstart.md)

### End-to-End Testing: Task Creation Event Flow

- [ ] T021 Port-forward backend-service for local access: `kubectl port-forward service/backend-service 8000:8000`
- [ ] T022 Create test task via API with priority, tags, due date, and reminder settings
- [ ] T023 Verify backend logs show "Published event to task-events: created" message
- [ ] T024 Verify Redpanda Cloud console shows new message in task-events topic with correct event structure
- [ ] T025 Verify audit-service logs show "Received event: created for task_id=X" message
- [ ] T026 Port-forward audit-service API: `kubectl port-forward service/audit-service 8001:8001`
- [ ] T027 Query audit trail via API and verify audit log entry exists for created task

### End-to-End Testing: Task Update Event Flow

- [ ] T028 Update test task via API (change title and priority)
- [ ] T029 Verify backend logs show "Published event to task-events: updated" message
- [ ] T030 Verify backend logs show "Published event to task-updates: task_updated" message
- [ ] T031 Verify Redpanda Cloud console shows 2 new messages (task-events + task-updates topics)
- [ ] T032 Verify audit-service logs show "Received event: updated for task_id=X" message
- [ ] T033 Query audit trail and verify update audit log entry with changes metadata

### End-to-End Testing: Task Completion Event Flow

- [ ] T034 Complete test task via API: `PATCH /api/{user_id}/tasks/{task_id}/complete`
- [ ] T035 Verify backend logs show "Published event to task-events: completed" message
- [ ] T036 Verify Redpanda Cloud console shows new "completed" event in task-events topic
- [ ] T037 Verify audit-service logs show completion event received
- [ ] T038 Query audit trail and verify completion audit log entry exists

### End-to-End Testing: Task Deletion Event Flow

- [ ] T039 Delete test task via API: `DELETE /api/{user_id}/tasks/{task_id}`
- [ ] T040 Verify backend logs show "Published event to task-events: deleted" message
- [ ] T041 Verify Redpanda Cloud console shows "deleted" event with full task snapshot
- [ ] T042 Verify audit-service logs show deletion event received
- [ ] T043 Query audit trail and verify deletion audit log entry exists

**Checkpoint**: At this point, complete event flow from API → Kafka → Consumer services is verified and working

---

## Phase 4: Polish & Monitoring

**Purpose**: Set up monitoring, verify system health, and validate documentation

### Redpanda Cloud Console Monitoring

- [ ] T044 Navigate to Redpanda Cloud console Overview and verify throughput metrics show activity
- [ ] T045 Check Consumer Groups → todo-service-group and verify consumer lag is <10 messages
- [ ] T046 Check Storage usage is within limits (<1GB used during testing)
- [ ] T047 Review task-events topic metrics (message count, throughput)
- [ ] T048 Review task-updates topic metrics (should show updates when tasks modified)

### Kubernetes Service Health Checks

- [ ] T049 Verify all pods show 2/2 Running status: `kubectl get pods`
- [ ] T050 Verify all service endpoints have IPs: `kubectl get endpoints`
- [ ] T051 Check pod resource usage: `kubectl top pods` (verify within limits)
- [ ] T052 Review backend-service logs for any errors: `kubectl logs deployment/backend-service -c backend --tail=100`
- [ ] T053 Review audit-service logs for any errors: `kubectl logs deployment/audit-service -c audit --tail=100`
- [ ] T054 Review notification-service logs: `kubectl logs deployment/notification-service -c notification --tail=100`

### Real-Time Log Monitoring Setup

- [ ] T055 Open terminal 1 for backend logs: `kubectl logs -f deployment/backend-service -c backend | grep -E "Published|ERROR"`
- [ ] T056 Open terminal 2 for audit-service logs: `kubectl logs -f deployment/audit-service -c audit | grep -E "Received|ERROR"`
- [ ] T057 Perform create/update/delete operations and verify logs appear in real-time

### Documentation Validation

- [ ] T058 [P] Verify quickstart.md instructions match actual deployment steps performed
- [ ] T059 [P] Update PHASE_V_PROGRESS.md to mark Redpanda integration as complete
- [ ] T060 [P] Document any issues encountered and their solutions in quickstart.md troubleshooting section

### System Health Validation

- [ ] T061 Verify all success criteria from plan.md are met:
  - All pods show 2/2 Running status ✓
  - Backend publishes events successfully ✓
  - Redpanda Cloud console shows messages in all topics ✓
  - Audit service consumes events and writes to database ✓
  - Audit API returns records for test tasks ✓
  - Consumer lag remains <10 messages ✓

**Checkpoint**: Redpanda Cloud integration complete and healthy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS deployment
- **User Story 1 (Phase 3)**: Depends on Foundational completion (secrets + images must exist)
- **Polish (Phase 4)**: Depends on User Story 1 completion (services must be deployed and working)

### Within Phase 2 (Foundational)

- Secrets (T006-T009): Sequential, must complete before deployment
- Docker Images (T010-T012): Can run in parallel [P] - different images, no dependencies

### Within Phase 3 (User Story 1)

- **Deployment (T014-T020)**:
  - Backend must deploy first (T014-T016)
  - Notification and Audit can deploy in parallel (T017-T018) after backend
- **Testing (T021-T043)**: Sequential by event type (create → update → complete → delete)
  - Each test group verifies one event flow end-to-end
  - Must complete previous test before next to avoid confusion

### Within Phase 4 (Polish)

- Monitoring tasks (T044-T057): Sequential for understanding metrics
- Documentation tasks (T058-T060): Can run in parallel [P] - different files

### Parallel Opportunities

**Phase 2 - Image Builds**:
```bash
# Launch all image builds together:
Task T010: "Build backend Docker image"
Task T011: "Build notification-service Docker image"
Task T012: "Build audit-service Docker image"
```

**Phase 3 - Service Deployments (after backend)**:
```bash
# Launch microservice deployments together:
Task T017: "Deploy notification-service"
Task T018: "Deploy audit-service"
```

**Phase 4 - Documentation**:
```bash
# Update documentation in parallel:
Task T058: "Verify quickstart.md"
Task T059: "Update PHASE_V_PROGRESS.md"
Task T060: "Document issues and solutions"
```

---

## Implementation Strategy

### MVP First (Phase 3 Only)

1. Complete Phase 1: Setup & Verification (verify prerequisites)
2. Complete Phase 2: Foundational (create secrets, build images)
3. Complete Phase 3: Deploy and test event flow
4. **STOP and VALIDATE**: Verify all event flows work independently
5. System is fully functional - Redpanda integration complete!

### Full Completion

1. Complete Setup (Phase 1) → Prerequisites verified
2. Complete Foundational (Phase 2) → Secrets and images ready
3. Complete User Story 1 (Phase 3) → Services deployed and tested
4. Complete Polish (Phase 4) → Monitoring set up and documented
5. Celebrate! Event-driven architecture is live 🎉

---

## Task Summary

**Total Tasks**: 61
**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 8 tasks (3 parallel image builds)
- Phase 3 (User Story 1): 30 tasks (core deployment and testing)
- Phase 4 (Polish): 18 tasks (3 parallel documentation tasks)

**Parallel Tasks**: 6 tasks marked [P]
- 3 Docker image builds (Phase 2)
- 3 Documentation tasks (Phase 4)

**Critical Path**: Phase 1 → Phase 2 → Phase 3 (backend deployment) → Phase 3 (microservice deployments) → Phase 3 (testing) → Phase 4

**Estimated Time**:
- Setup: 10 minutes
- Foundational: 15 minutes (image builds)
- Deployment & Testing: 45-60 minutes (includes verification)
- Monitoring: 15 minutes
- **Total: ~90 minutes** (following quickstart.md)

**MVP Scope**: Phases 1-3 (deploy and verify event flow) = Core functionality
**Full Scope**: All phases (includes monitoring and documentation)

---

## Notes

- [P] tasks = different files/images, no dependencies
- All secrets must exist before deployment (Phase 2 required)
- Backend must deploy before microservices (Dapr component dependency)
- Each test scenario verifies complete event flow (publish → Kafka → consume → database)
- Use quickstart.md as reference for detailed commands and troubleshooting
- Real-time log monitoring (T055-T057) is optional but helpful for debugging
- Verify tests at each checkpoint before proceeding
- Consumer lag should remain near 0 during testing (low volume)
- If any deployment fails, check quickstart.md troubleshooting section

**Success Criteria**: When T043 completes, the Redpanda Cloud integration is fully functional with all event types verified end-to-end.

---

## Quick Reference Commands

```bash
# Prerequisites check
minikube status
kubectl get pods -n dapr-system
kubectl get components
kubectl get secrets

# Image builds (run after: eval $(minikube docker-env))
docker build -t todo-backend:latest ./backend
docker build -t todo-notification:latest ./services/notification-service
docker build -t todo-audit:latest ./services/audit-service

# Deployments
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/notification-service/deployment.yaml
kubectl apply -f k8s/audit-service/deployment.yaml

# Status checks
kubectl get pods
kubectl rollout status deployment/backend-service
kubectl logs deployment/backend-service -c backend --tail=20

# Port forwarding
kubectl port-forward service/backend-service 8000:8000
kubectl port-forward service/audit-service 8001:8001

# Testing
curl -X POST http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Kafka", "priority": "high"}'
```

See quickstart.md for complete command reference and troubleshooting guide.
