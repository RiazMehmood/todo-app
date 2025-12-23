# Todo App - Hackathon II Overview

## Purpose
A todo application that evolves from a simple console app to a fully-featured, cloud-native AI chatbot deployed on Kubernetes. This project demonstrates the **Evolution of Todo** - mastering Spec-Driven Development and Cloud-Native AI technologies.

## Current Phase
**Phase V: Advanced Cloud Deployment**

Implement advanced features, event-driven architecture with Kafka, Dapr integration, and deploy to Kubernetes (local and cloud) with full CI/CD pipeline.

## Tech Stack Evolution

### Phase I (Completed)
- Python 3.13+ with UV package manager
- In-memory storage (Python list/dict)
- CLI interface with table display
- Full CRUD operations

### Phase II (Completed, Deployed)
- **Frontend**: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT
- **Deployment**: Vercel (frontend), Railway (backend)
- **Status**: ✅ Production Live

### Phase III (Current)
- **AI Framework**: OpenAI ChatKit
- **Agent Runtime**: Agents SDK
- **Protocol**: Model Context Protocol (MCP)
- **Integration**: Natural language task management
- **Spec-Driven**: Claude Code + Spec-Kit Plus

### Future Phases
- **Phase VI**: Additional enhancements and optimizations

## Core Features

### Basic Level (All Phases)
- [x] **Add Task** - Create new todo items
- [x] **View Task List** - Display all tasks
- [x] **Update Task** - Modify existing task details
- [x] **Delete Task** - Remove tasks from list
- [x] **Mark as Complete** - Toggle task completion status

### Phase II Additions (Completed)
- [x] **User Authentication** - Signup/Signin with Better Auth
- [x] **Multi-user Support** - Each user has their own tasks
- [x] **Persistent Storage** - Tasks saved to Neon PostgreSQL
- [x] **RESTful API** - Backend API with JWT security
- [x] **Responsive Web UI** - Modern Next.js interface

### Phase III Additions
- [ ] **AI Chat Interface** - Conversational UI for task management
- [ ] **Natural Language Processing** - Understand user intent
- [ ] **Agent Integration** - Agents SDK for autonomous task handling
- [ ] **MCP Protocol** - Model Context Protocol for AI communication
- [ ] **Voice Commands** - Optional voice input for tasks

### Future Enhancements
- **Intermediate**: Priorities, tags, search, filter, sort
- **Advanced**: Recurring tasks, due dates, reminders, AI chatbot

## Architecture Principles

1. **Spec-Driven Development**: All features start with specifications
2. **AI-Native**: Using Claude Code to generate implementations from specs
3. **Cloud-Native**: Designed for scalability and distributed deployment
4. **Event-Driven**: (Phase V) Using Kafka for async communication
5. **Stateless Services**: Enable horizontal scaling

## Success Criteria

### Phase II Deliverables
1. GitHub repository with monorepo structure
2. Working web application (frontend + backend)
3. User authentication and authorization
4. All basic CRUD operations via REST API
5. Deployed on Vercel (frontend) and accessible backend
6. Complete specifications in `/specs` folder
7. PHR records documenting the development process

## Project Status

- **Phase I**: ✅ Completed (Dec 7, 2025)
- **Phase II**: ✅ Completed & Deployed (Dec 16, 2025)
  - Frontend: https://todo-app-ashy-seven-25.vercel.app/login
  - Backend: https://todo-app-production-be56.up.railway.app/
- **Phase III**: ✅ Completed (Dec 21, 2025)
- **Phase IV**: ✅ Completed (Jan 4, 2026)
- **Phase V**: 🚧 In Progress (Due: Jan 18, 2026)

## Development Workflow

1. **Specify**: Write/update specifications in `/specs`
2. **Plan**: Create implementation plan (optional for complex features)
3. **Implement**: Use Claude Code to generate code from specs
4. **Test**: Verify functionality manually and with tests
5. **Document**: Create PHR records for learning and traceability
6. **Deploy**: Push to staging/production environments

## Key Constraints

- **Spec-First**: Cannot write code manually; must refine specs until Claude Code generates correct output
- **Multi-user**: All features must support multiple users with data isolation
- **Security**: JWT authentication required for all API endpoints
- **Stateless Backend**: No in-memory state; all data persisted to database

## References

- [Hackathon II Documentation](../Hackathon II - Todo Spec-Driven Development.pdf)
- [Phase I Specification](001-todo-console-app/spec.md)
- [Project Constitution](../.specify/memory/constitution.md)
