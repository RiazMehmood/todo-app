---
id: 0002
title: Phase III Research AI Technologies
stage: research
date: 2025-12-16
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-ai-chatbot-integration
branch: 002-todo-web-app
user: riaz
command: research
labels: ["research", "ai", "openai", "mcp", "urdu", "privacy"]
links:
  spec: /home/riaz/Desktop/todo hackathon II/todo/specs/003-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /home/riaz/Desktop/todo hackathon II/todo/specs/003-ai-chatbot-integration/research.md
tests:
  - No tests run (research phase)
---

## Prompt

Research and create research.md for Phase III AI Chatbot Integration.

Research the following topics and create a comprehensive research.md file at `/home/riaz/Desktop/todo hackathon II/todo/specs/003-ai-chatbot-integration/research.md`:

1. **OpenAI ChatKit Integration**: Research how to integrate OpenAI ChatKit component into Next.js applications. Find documentation, best practices, and example implementations.

2. **Agents SDK Compatibility**: Research Python Agents SDK options compatible with FastAPI. Look for @anthropic/agents-sdk or similar Python agent frameworks.

3. **Model Context Protocol (MCP)**: Research MCP implementation for Python/FastAPI. Find libraries, protocols, and integration patterns.

4. **WebSocket vs SSE**: Research best approach for real-time chat in Next.js + FastAPI setup. Compare WebSocket vs Server-Sent Events.

5. **Urdu Language Support**: Research OpenAI's multilingual model support for Urdu language. Verify accuracy and best practices.

6. **Privacy Compliance**: Research best practices for opt-in AI features and GDPR/privacy compliance for AI-powered applications.

For each topic, provide:
- **Decision**: What was chosen
- **Rationale**: Why it was chosen
- **Alternatives Considered**: What else was evaluated
- **Implementation Notes**: Key technical details

Format the file as markdown with clear sections.

## Response snapshot

Created comprehensive research documentation at `/home/riaz/Desktop/todo hackathon II/todo/specs/003-ai-chatbot-integration/research.md` covering all six research topics.

### Key Findings:

**1. OpenAI ChatKit Integration**
- No official "ChatKit" exists - use OpenAI Chat Completions API with custom UI
- Use `openai` npm/Python packages with custom React components
- Leverage function calling for task CRUD operations
- Recommend GPT-4o for best multilingual support

**2. Agents SDK Compatibility**
- Two approaches: OpenAI Functions (recommended for MVP) or Anthropic Claude + MCP
- OpenAI Functions simpler, no additional framework needed
- Full MCP implementation optional for Phase IV enhancements
- TaskAgent class pattern for managing AI interactions

**3. Model Context Protocol (MCP)**
- Implement lightweight MCP-inspired pattern using OpenAI functions for MVP
- Full MCP server adds complexity not needed for basic CRUD
- Can migrate to full MCP later for advanced features
- Define tools, resources, and context similar to MCP concepts

**4. WebSocket vs SSE**
- **Decision**: Server-Sent Events (SSE) for real-time streaming
- SSE is unidirectional (perfect for AI responses), HTTP-based, simpler
- Works through all proxies/firewalls, auto-reconnect built-in
- WebSocket considered for future collaborative features

**5. Urdu Language Support**
- GPT-4o has native Urdu support, no translation API needed
- Automatic language detection from user input
- Provide bilingual examples in system prompt
- Use Noto Nastaliq Urdu font, handle RTL text direction
- 90%+ accuracy expected on common task phrases

**6. Privacy Compliance**
- **Decision**: Explicit opt-in flow with clear privacy notice
- GDPR/CCPA require transparency about third-party data processing
- Database schema for consent tracking (timestamp, version, audit trail)
- Users can disable AI and delete chat history anytime
- Default: AI features disabled until user consents

### Technology Decisions Summary:

| Component | Decision | Rationale |
|-----------|----------|-----------|
| Chat UI | Custom React components | No official ChatKit, custom gives control |
| AI Model | OpenAI GPT-4o | Best multilingual support (Urdu), function calling |
| Agent Framework | OpenAI Functions (MVP) | Simpler than full MCP, sufficient for CRUD |
| Real-time Streaming | Server-Sent Events (SSE) | Unidirectional, HTTP-based, simpler than WebSocket |
| Language Support | GPT-4o native Urdu | No translation API needed, auto-detection |
| Privacy | Explicit opt-in with notice | GDPR/CCPA compliance, builds trust |

### Implementation Priorities:

**Phase III MVP (P1)**:
1. OpenAI API integration with function calling
2. Custom chat UI components (React)
3. SSE streaming for real-time responses
4. Privacy opt-in flow and consent tracking
5. Basic task CRUD via natural language (English + Urdu)

**Phase III Enhancements (P2)**:
6. Query tasks via natural language
7. Update/delete tasks via chat
8. Chat history persistence and display
9. Improved error handling and fallbacks
10. Rate limiting and cost controls

### Open Questions for User:

1. OpenAI Budget: What is acceptable monthly spend on OpenAI API?
2. Privacy Review: Should legal counsel review privacy notice?
3. Language Priority: If Urdu accuracy is poor, launch English-only first?
4. Feature Scope: MVP include only creation (P1) or also querying (P2)?
5. Voice Input: Phase III or Phase IV priority?

## Outcome

- ✅ Impact: Comprehensive research document created covering all 6 topics with decisions, rationale, alternatives, and implementation details
- 🧪 Tests: No tests run (research phase)
- 📁 Files: Created research.md (1 file, ~550 lines)
- 🔁 Next prompts: Create data model for ChatMessage/AIConsent, define OpenAPI contracts for chat endpoints, implement OpenAI integration
- 🧠 Reflection: Research revealed no official "ChatKit" or universal "Agents SDK" - needed to clarify that we'll use OpenAI Chat Completions API with custom UI and function calling pattern. SSE is better choice than WebSocket for unidirectional AI streaming. Privacy compliance requires explicit opt-in flow with consent tracking.

## Evaluation notes (flywheel)

- Failure modes observed: WebSearch and WebFetch tools were unavailable, relied on internal knowledge of OpenAI, MCP, and privacy compliance standards (current as of January 2025)
- Graders run and results (PASS/FAIL): N/A (research phase, no automated grading)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify OpenAI API access and test GPT-4o Urdu support with sample task creation prompts before proceeding to implementation
