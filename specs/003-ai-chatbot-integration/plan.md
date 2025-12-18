# Implementation Plan: AI Chatbot Integration for Task Management

**Branch**: `003-ai-chatbot-integration` | **Date**: 2025-12-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add AI-powered natural language interface to the todo application using OpenAI ChatKit for the UI, Agents SDK for AI runtime management, and Model Context Protocol (MCP) for communication. Users can manage tasks through conversational commands in English and Urdu with explicit opt-in for privacy compliance.

**Technical Approach**:
- Frontend: Integrate OpenAI ChatKit (`@openai/chatkit-react`) component into existing Next.js application
- Backend: Add MCP server layer between FastAPI and OpenAI using OpenAI Agents SDK (`openai-agents`)
- MCP: Official MCP Python SDK (`mcp[cli]`) for Model Context Protocol implementation
- Database: Extend PostgreSQL schema to store conversations, messages, and user AI preferences
- Authentication: Reuse existing JWT system with added AI opt-in flag
- Languages: Support English and Urdu through OpenAI GPT-4o multilingual model

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5.x with Next.js 16+
- Backend: Python 3.13+ with FastAPI

**Primary Dependencies**:
- `@openai/chatkit-react` (npm) - Official OpenAI chat UI component
- `openai-agents` (Python) - OpenAI Agents SDK for AI agent runtime management
- `openai` (Python) - OpenAI API client
- `mcp[cli]` (Python) - Official Model Context Protocol Python SDK
- Existing: FastAPI, SQLModel, Neon PostgreSQL, Better Auth

**Storage**:
- PostgreSQL (Neon) - extended with Conversation, Message, and UserPreferences tables
- Chat history persisted with same multi-user isolation as tasks

**Testing**:
- Manual testing for MVP (per constitution)
- Optional: Playwright for E2E chat flows
- Backend: pytest for API endpoints

**Target Platform**:
- Web (browsers with WebSocket/SSE support for real-time chat)
- Mobile responsive (existing responsive design extends to chat)

**Project Type**: Web (monorepo: frontend/ + backend/)

**Performance Goals**:
- Chat response time: <2 seconds (95th percentile)
- Support 100 concurrent chat users
- OpenAI API calls rate-limited to prevent abuse
- WebSocket/SSE connection handling for real-time updates

**Constraints**:
- OpenAI API rate limits and costs
- Must maintain existing multi-user data isolation
- Opt-in privacy model (no AI processing without explicit consent)
- English and Urdu language support
- Graceful degradation when OpenAI API unavailable

**Scale/Scope**:
- 5 user stories (US0-US4: Opt-in, Create, Query, Update/Delete, Voice)
- 23 functional requirements
- 3 new database tables (Conversation, Message, UserPreferences) + enhanced Task table
- ~7-10 new API endpoints for chat operations (simplified for Basic Level)
- 1 new major UI component (ChatKit chat interface)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Specification-First Development ✅ PASS
- Specification created and validated: `specs/003-ai-chatbot-integration/spec.md`
- All user stories prioritized with acceptance criteria
- Implementation plan follows specification
- No code written before spec approval

### II. Clean Architecture ✅ PASS (with notes)
- Frontend: Chat component separated from existing task UI
- Backend: MCP layer sits between API routes and OpenAI client
- Models: ChatMessage, UserPreferences as new entities
- Services: ChatService handles NLP and task operations
- Dependency flow: UI → API → MCP Server → Agents SDK → OpenAI
- **Note**: MCP adds middleware layer - justified for AI abstraction and protocol standardization

### III. Code Quality Standards ✅ PASS
- TypeScript for frontend (existing standard)
- Python PEP 8 for backend (existing standard)
- Descriptive naming: ChatService, MessageProcessor, AIAgentManager
- Single responsibility maintained per module

### IV. User-Friendly Error Handling ✅ PASS
- Graceful fallback when OpenAI unavailable
- Clear error messages for AI misinterpretation
- Privacy notice during opt-in
- Confirmation dialogs for destructive operations
- Ambiguity handled with clarifying questions from AI

### V. Test-Driven Development (TDD) ⚠️ OPTIONAL
- Testing optional per constitution
- Manual testing plan included in spec
- Optional automated tests for critical chat flows

### VI. Simplicity and YAGNI ✅ PASS
- Only implementing features from specification
- No premature optimization
- Phase III scope clearly bounded (no advanced AI features)
- Voice input (US5) marked as P3 - can be deferred

**Constitution Compliance**: ✅ ALL GATES PASSED

**Justifications**: MCP middleware layer adds architectural complexity but is justified for:
1. Protocol standardization between AI and application
2. Abstraction of OpenAI-specific implementation
3. Future AI provider flexibility

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-integration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technical decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── chat-api.yaml   # OpenAPI spec for chat endpoints
│   └── mcp-protocol.md # MCP message formats
├── checklists/
│   └── requirements.md  # Spec validation (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```text
# Option 2: Web application (monorepo with frontend + backend)

backend/
├── src/
│   ├── models.py                    # Enhanced: Add Conversation, Message, UserPreferences models
│   ├── routes/
│   │   ├── auth.py                  # Enhanced: Add AI opt-in endpoints
│   │   ├── tasks.py                 # Existing task CRUD
│   │   ├── chat.py                  # NEW: Chat endpoints (send message, get history)
│   │   └── chatkit.py               # NEW: ChatKit session endpoint
│   ├── services/
│   │   ├── chat_service.py          # NEW: Chat logic and conversation management
│   │   ├── task_service.py          # NEW: Task operations for AI agent
│   │   └── ai_agent_manager.py      # NEW: Agents SDK integration
│   ├── agents/
│   │   └── task_agent.py            # NEW: Task agent with function tools
│   ├── mcp_server/
│   │   └── task_tools.py            # NEW: MCP server with 5 required tools
│   ├── middleware/
│   │   └── auth.py                  # Existing JWT auth
│   └── main.py                      # Enhanced: Register chat routes, mount MCP
├── tests/                           # Optional
│   ├── test_chat_service.py
│   ├── test_mcp_server.py
│   └── test_ai_integration.py
└── pyproject.toml                   # Enhanced: Add openai-agents, mcp[cli], openai deps

frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx                 # Enhanced: Add chat interface component
│   └── settings/
│       └── page.tsx                 # Enhanced: Add AI opt-in toggle
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx        # NEW: Main chat UI (uses ChatKit)
│   │   ├── ChatMessage.tsx          # NEW: Message display
│   │   ├── ChatInput.tsx            # NEW: Message input with voice
│   │   └── ChatHistory.tsx          # NEW: Message history
│   ├── settings/
│   │   └── AISettingsPanel.tsx      # NEW: Opt-in and privacy controls
│   └── ui/
│       └── PrivacyNotice.tsx        # NEW: Privacy consent modal
├── lib/
│   ├── api.ts                       # Enhanced: Add chat API calls
│   ├── chat.ts                      # NEW: Chat client logic
│   └── types.ts                     # Enhanced: Add chat types
└── package.json                     # Enhanced: Add @openai/chatkit dep
```

**Structure Decision**: Extends existing monorepo web application structure. Backend adds MCP layer as new module. Frontend adds chat components as new feature module alongside existing task UI. Maintains clean separation and follows existing architectural patterns.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Official MCP Python SDK | **Hackathon requirement** - Protocol standardization for AI-app communication | Direct OpenAI integration would not meet hackathon spec (Page 17); required to use Official MCP SDK |
| OpenAI Agents SDK | **Hackathon requirement** - Runtime management for AI agent lifecycle, context, state | Hackathon explicitly requires Agents SDK (Page 17); manual agent state management not compliant |
| OpenAI ChatKit component | **Hackathon requirement** - Pre-built chat UI with streaming, tool visualization | Custom chat UI would not meet hackathon spec; ChatKit required (Page 17) |
| Three new database tables | **Hackathon requirement** - Conversation, Message, UserPreferences tables required by spec (Page 18) | Hackathon explicitly defines required schema; must implement Conversation and Message tables |

**Justification Summary**: Added complexity is minimal and directly serves specification requirements. All additions follow clean architecture principles and maintain separation of concerns.

## Implementation Strategy

### Phase 0: Research & Technical Decisions
See [research.md](./research.md) for detailed findings on:
- **OpenAI ChatKit** (`@openai/chatkit-react`) - Official pre-built chat UI component
- **OpenAI Agents SDK** (`openai-agents`) - Production-ready agent runtime management
- **Official MCP Python SDK** (`mcp[cli]`) - Model Context Protocol implementation
- Hybrid Architecture: ChatKit + Agents SDK + MCP integration patterns
- Server-Sent Events (SSE) for real-time streaming
- Urdu language support in OpenAI GPT-4o models
- Privacy compliance best practices (opt-in flow)

### Phase 1: Design & Contracts
See artifacts:
- [data-model.md](./data-model.md) - Database schema for Conversation, Message, UserPreferences tables
- [contracts/chat-api.yaml](./contracts/chat-api.yaml) - OpenAPI spec for chat endpoints
- [contracts/mcp-protocol.md](./contracts/mcp-protocol.md) - MCP tool definitions (add_task, list_tasks, etc.)
- [quickstart.md](./quickstart.md) - Setup and development guide with correct dependencies

### Phase 2: Task Generation
Run `/sp.tasks` after Phase 1 artifacts complete to generate dependency-ordered implementation tasks.

### Phase 3: Implementation
Run `/sp.implement` to execute tasks from tasks.md.

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI API rate limits | Medium | High | Implement aggressive caching, rate limiting per user, fallback to manual UI |
| Urdu language accuracy | Medium | Medium | Test thoroughly, provide feedback mechanism, allow manual correction |
| WebSocket scaling | Low | Medium | Use managed service (Railway/Vercel supports WS), implement connection pooling |
| User adoption of AI features | Medium | Low | Make opt-in clear, provide value immediately (US1 P1), keep manual UI available |
| Privacy compliance issues | Low | High | Legal review of privacy notice, clear opt-in flow, data deletion capability |

## Success Metrics

Aligned with spec success criteria (SC-001 to SC-010):
- Task creation via chat: <30 seconds
- AI accuracy: >90%
- Response time: <2 seconds
- Concurrent users: 100+
- Uptime: 95%+
- Feature retention: 80% after 1 week
- Time reduction: 40% for chat vs manual

## Next Steps

1. ✅ Complete Phase 0 research (research.md)
2. ✅ Complete Phase 1 design (data-model.md, contracts/, quickstart.md)
3. ⏭️ Run `/sp.tasks` to generate implementation tasks
4. ⏭️ Run `/sp.implement` to execute tasks
5. ⏭️ Manual testing against acceptance criteria
6. ⏭️ Deploy to staging → production
7. ⏭️ Create PHR and ADR if architectural decisions identified
