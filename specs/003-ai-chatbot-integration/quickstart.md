# Quick Start Guide: AI Chatbot Integration

**Feature**: 003-ai-chatbot-integration
**Last Updated**: 2025-12-16 (Updated for Strict Hackathon Compliance)

## Overview

This guide helps developers set up and develop the AI Chatbot Integration feature for the Todo application using the **required hackathon technology stack**: OpenAI ChatKit, OpenAI Agents SDK, and Official MCP Python SDK.

**Hackathon II Phase III Requirements:**
- ✅ OpenAI ChatKit (`@openai/chatkit-react`) - Official chat UI component
- ✅ OpenAI Agents SDK (`openai-agents`) - AI agent runtime management
- ✅ Official MCP Python SDK (`mcp[cli]`) - Model Context Protocol server
- ✅ Neon PostgreSQL with Conversation and Message tables (Page 18)
- ✅ FastAPI backend + Next.js frontend + Better Auth

## Prerequisites

### System Requirements
- Node.js 18+ and npm
- Python 3.13+
- UV package manager
- PostgreSQL (Neon account) or local PostgreSQL
- OpenAI API account and API key
- Git

### Existing Setup
This assumes you have completed Phase II and have:
- ✅ Working Next.js frontend (http://localhost:3000)
- ✅ Working FastAPI backend (http://localhost:8000)
- ✅ Neon PostgreSQL database connected
- ✅ Authentication with JWT working

---

## 1. Environment Setup

### Backend Environment Variables

Add to `backend/.env`:

```bash
# Existing variables (keep these)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=your-secret-here
CORS_ORIGINS=http://localhost:3000

# NEW: AI Chat Variables
OPENAI_API_KEY=sk-...your-key-here
OPENAI_MODEL=gpt-4o
OPENAI_AGENT_ID=your-agent-id  # From OpenAI Agent Builder
MCP_SERVER_PORT=8001  # Optional: if running MCP on separate port
CHAT_RATE_LIMIT_PER_USER=20  # messages per minute
```

**How to get API keys**:
- OpenAI API Key: https://platform.openai.com/api-keys
- Create new secret key, copy immediately (shown once)

### Frontend Environment Variables

Add to `frontend/.env.local`:

```bash
# Existing variables (keep these)
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-here
BETTER_AUTH_URL=http://localhost:3000

# NEW: AI Chat Variables
NEXT_PUBLIC_CHATKIT_API_KEY=optional-if-needed
NEXT_PUBLIC_AI_ENABLED=true
```

---

## 2. Database Migration

### Run Migration Scripts

```bash
# Navigate to backend
cd backend

# Create migration file (if using Alembic)
uv run alembic revision --autogenerate -m "add_chat_tables"

# Or run SQL directly
uv run python -c "
from src.db import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text(open('migrations/003_add_chat_tables.sql').read()))
    conn.commit()
"
```

### Migration SQL

Create `backend/migrations/003_add_chat_tables.sql`:

```sql
-- User Preferences Table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ai_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    ai_opt_in_date TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'en' NOT NULL,
    privacy_consent_version VARCHAR(10),
    auto_detect_language BOOLEAN DEFAULT TRUE NOT NULL,
    voice_input_enabled BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT check_ai_consent CHECK (
        (ai_enabled = FALSE) OR
        (ai_enabled = TRUE AND privacy_consent_version IS NOT NULL)
    ),
    CONSTRAINT check_language CHECK (preferred_language IN ('en', 'ur'))
);

-- Chat Messages Table
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    sender VARCHAR(10) NOT NULL CHECK (sender IN ('user', 'ai')),
    language VARCHAR(10) CHECK (language IN ('en', 'ur')),
    related_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    intent_detected VARCHAR(50),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB
);

-- Add AI columns to tasks
ALTER TABLE tasks
    ADD COLUMN created_via_ai BOOLEAN DEFAULT FALSE NOT NULL,
    ADD COLUMN ai_suggested_priority INTEGER CHECK (ai_suggested_priority >= 1 AND ai_suggested_priority <= 5),
    ADD COLUMN original_nl_input TEXT;

-- Create indexes
CREATE INDEX idx_user_prefs_user_id ON user_preferences(user_id);
CREATE INDEX idx_chat_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_timestamp ON chat_messages(timestamp DESC);
CREATE INDEX idx_chat_user_timestamp ON chat_messages(user_id, timestamp DESC);
CREATE INDEX idx_tasks_created_via_ai ON tasks(created_via_ai);
```

---

## 3. Install Dependencies

### Backend Dependencies

```bash
cd backend

# Add new dependencies to pyproject.toml (CORRECT PACKAGES)
uv add openai  # OpenAI Python client
uv add openai-agents  # OpenAI Agents SDK (official)
uv add "mcp[cli]"  # Official MCP Python SDK
uv add websockets  # For SSE streaming (optional)

# Install all dependencies
uv sync
```

### Frontend Dependencies

```bash
cd frontend

# Add new dependencies (CORRECT PACKAGES)
npm install @openai/chatkit-react  # Official OpenAI ChatKit for React
npm install react-markdown  # For rendering AI responses
npm install @heroicons/react  # For chat UI icons

# Install all dependencies
npm install
```

---

## 4. Local Development

### Start Backend

```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**Verify**:
- Backend running: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Start Frontend

```bash
cd frontend
npm run dev
```

**Verify**:
- Frontend running: http://localhost:3000
- Login page loads
- Can create tasks (Phase II functionality works)

### Test AI Integration

1. **Opt-in to AI**:
   - Navigate to http://localhost:3000/settings
   - Find "Enable AI Chat Assistant" toggle
   - Click to enable, accept privacy notice
   - Verify AI chat interface appears on dashboard

2. **Send Test Message**:
   - Type: "Add task to buy milk"
   - Verify AI response confirms task creation
   - Check database: task should exist with `created_via_ai=TRUE`

3. **Test Urdu**:
   - Type: "مجھے دودھ خریدنا یاد دلائیں"
   - Verify AI understands and responds in Urdu
   - Task should be created

---

## 5. Development Workflow

### Backend Development

**File Structure**:
```bash
backend/src/
├── models.py           # Add ChatMessage, UserPreferences models
├── routes/
│   ├── auth.py        # Add AI opt-in endpoints
│   ├── tasks.py       # Existing task CRUD
│   └── chat.py        # NEW: Chat endpoints
├── services/
│   ├── chat_service.py      # NEW: Chat logic
│   ├── task_service.py      # NEW: Task operations for AI
│   └── ai_agent_manager.py  # NEW: Agents SDK integration
├── mcp/
│   ├── server.py      # NEW: MCP server
│   ├── handlers.py    # NEW: Message handlers
│   └── protocol.py    # NEW: Protocol definitions
└── main.py            # Register new routes
```

**Key Files to Create**:
1. `src/models.py`: Add new models
2. `src/routes/chat.py`: Chat API endpoints
3. `src/services/chat_service.py`: Business logic
4. `src/mcp/server.py`: MCP implementation

### Frontend Development

**File Structure**:
```bash
frontend/
├── app/
│   ├── dashboard/page.tsx    # Add chat interface
│   └── settings/page.tsx     # Add AI settings
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx  # NEW: Main chat UI
│   │   ├── ChatMessage.tsx    # NEW: Message component
│   │   └── ChatInput.tsx      # NEW: Input component
│   └── settings/
│       └── AISettingsPanel.tsx  # NEW: Settings UI
└── lib/
    ├── api.ts        # Add chat API functions
    ├── chat.ts       # NEW: Chat utilities
    └── types.ts      # Add chat types
```

**Key Files to Create**:
1. `components/chat/ChatInterface.tsx`: Main UI
2. `lib/api.ts`: Add `sendChatMessage()`, `getChatHistory()`
3. `lib/types.ts`: Add TypeScript interfaces

---

## 6. Testing

### Manual Testing Checklist

**Phase 0: Setup**
- [ ] Database migration successful
- [ ] All dependencies installed
- [ ] Environment variables set
- [ ] Both servers start without errors

**Phase 1: Opt-In Flow (US0)**
- [ ] Settings page shows AI toggle
- [ ] Privacy notice displays on enable
- [ ] Opt-in creates UserPreferences record
- [ ] Chat interface appears after opt-in
- [ ] Opt-out hides chat interface

**Phase 2: Basic Chat (US1)**
- [ ] Can send message to AI
- [ ] AI responds within 2 seconds
- [ ] Task created from "Add task..." message
- [ ] Task appears in task list
- [ ] Database shows created_via_ai=TRUE

**Phase 3: Task Queries (US2)**
- [ ] "Show my tasks" lists tasks
- [ ] "What's pending?" shows incomplete tasks
- [ ] Empty list handled gracefully

**Phase 4: Task Updates (US3)**
- [ ] "Mark X as done" updates task
- [ ] "Delete X" shows confirmation
- [ ] Ambiguous references prompt clarification

**Phase 5: Urdu Support**
- [ ] Urdu input recognized
- [ ] AI responds in Urdu
- [ ] Tasks created with Urdu titles
- [ ] Mixed language conversations work

### API Testing with curl

```bash
# Opt-in to AI
curl -X POST http://localhost:8000/api/users/{user_id}/ai/opt-in \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"privacy_consent_version": "1.0.0"}'

# Send chat message
curl -X POST http://localhost:8000/api/users/{user_id}/chat/messages \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message_text": "Add task to buy milk"}'

# Get chat history
curl http://localhost:8000/api/users/{user_id}/chat/messages?limit=10 \
  -H "Authorization: Bearer {jwt_token}"
```

---

## 7. Troubleshooting

### Common Issues

**Issue**: "OpenAI API error: Invalid API key"
- **Fix**: Check `OPENAI_API_KEY` in backend/.env
- **Verify**: Visit https://platform.openai.com/api-keys

**Issue**: "AI features not enabled"
- **Fix**: User must opt-in first via settings
- **Check**: `SELECT * FROM user_preferences WHERE user_id='...'`

**Issue**: "Database migration failed"
- **Fix**: Check PostgreSQL connection
- **Rollback**: Run rollback SQL if needed

**Issue**: "Chat interface not showing"
- **Check**: User has ai_enabled=TRUE in preferences
- **Check**: Frontend console for errors
- **Verify**: ChatInterface component imported correctly

**Issue**: "Urdu text not displaying"
- **Fix**: Ensure UTF-8 encoding in database
- **Fix**: Check font supports Urdu characters
- **Database**: `ALTER DATABASE your_db SET client_encoding TO 'UTF8';`

---

## 8. Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Backend: `--reload` flag for uvicorn
- Frontend: Next.js dev server auto-reloads

### Debugging

**Backend**:
```python
# Add logging
import logging
logging.basicConfig(level=logging.DEBUG)

# In chat_service.py
logger.info(f"Processing message: {message_text}")
logger.debug(f"Intent detected: {intent}, confidence: {confidence}")
```

**Frontend**:
```typescript
// In ChatInterface.tsx
console.log('Sending message:', messageText);
console.log('AI response:', response);
```

### Database Inspection

```bash
# Connect to local database
psql -d your_database

# Check chat messages
SELECT * FROM chat_messages ORDER BY timestamp DESC LIMIT 10;

# Check AI opt-in status
SELECT user_id, ai_enabled, preferred_language
FROM user_preferences
WHERE ai_enabled = TRUE;

# Check AI-created tasks
SELECT id, title, created_via_ai, original_nl_input
FROM tasks
WHERE created_via_ai = TRUE;
```

---

## 9. Deployment

### Prerequisites for Deployment

- Vercel account (for frontend)
- Backend hosting service (Railway, Render, or similar)
- Neon PostgreSQL database (production instance)
- OpenAI API key with sufficient quota
- Google Gemini API key (if using Gemini instead of OpenAI)

### Backend Deployment

#### Option 1: Railway Deployment

1. **Create Railway Project**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login to Railway
   railway login

   # Initialize project
   railway init
   ```

2. **Configure Environment Variables**:
   In Railway dashboard, add:
   ```bash
   DATABASE_URL=postgresql://...  # Your Neon PostgreSQL URL
   BETTER_AUTH_SECRET=<production-secret>
   CORS_ORIGINS=https://your-app.vercel.app
   GEMINI_API_KEY=<your-gemini-key>
   AI_MODEL=gemini-2.0-flash-exp
   CHAT_RATE_LIMIT_PER_USER=20
   ```

3. **Deploy**:
   ```bash
   # Deploy backend
   railway up

   # Get deployment URL
   railway domain
   ```

4. **Run Migrations**:
   ```bash
   # Connect to Railway shell
   railway run python run_migration.py
   ```

#### Option 2: Render Deployment

1. **Create Web Service** in Render dashboard

2. **Build Command**:
   ```bash
   pip install uv && uv sync
   ```

3. **Start Command**:
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Environment Variables**: Same as Railway above

### Frontend Deployment (Vercel)

1. **Connect Repository**:
   - Go to https://vercel.com
   - Click "New Project"
   - Import your Git repository
   - Select `frontend` as root directory

2. **Configure Build Settings**:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

3. **Environment Variables**:
   ```bash
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   BETTER_AUTH_SECRET=<same-as-backend>
   BETTER_AUTH_URL=https://your-app.vercel.app
   NEXT_PUBLIC_AI_ENABLED=true
   ```

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Get deployment URL: `https://your-app.vercel.app`

### Post-Deployment Steps

1. **Update CORS Origins**:
   ```bash
   # In backend environment variables
   CORS_ORIGINS=https://your-app.vercel.app,https://your-app-staging.vercel.app
   ```

2. **Run Database Migrations**:
   ```bash
   # Connect to production database
   psql "postgresql://..."

   # Run migration
   \i backend/migrations/003_add_chat_tables.sql
   ```

3. **Verify Deployment**:
   - Visit frontend URL
   - Test authentication
   - Enable AI in settings
   - Send test chat message
   - Check database for records

### Deployment Checklist

**Pre-Deployment**:
- [ ] All tests pass locally
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] CORS origins configured
- [ ] API keys secured (not in code)

**Backend Deployment**:
- [ ] Backend deployed successfully
- [ ] Health endpoint responds: `GET /health`
- [ ] Database connected (check logs)
- [ ] Migrations applied
- [ ] HTTPS enabled

**Frontend Deployment**:
- [ ] Frontend deployed successfully
- [ ] Environment variables set
- [ ] Backend API reachable
- [ ] Authentication works
- [ ] Chat interface loads

**Post-Deployment**:
- [ ] Create test user account
- [ ] Enable AI features
- [ ] Test task creation via chat
- [ ] Test Urdu language support
- [ ] Verify multi-user isolation
- [ ] Check logs for errors
- [ ] Monitor API usage/costs

### Monitoring & Maintenance

**Backend Monitoring**:
```python
# Add to main.py for health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",  # Test DB connection
        "ai_service": "available",  # Test AI API
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Frontend Monitoring**:
- Use Vercel Analytics for performance
- Monitor error logs in Vercel dashboard
- Set up alerts for 500 errors

**Database Monitoring**:
- Use Neon dashboard for metrics
- Monitor connection pool usage
- Set up alerts for high query times
- Regular backups (Neon handles this)

**AI API Monitoring**:
- Track OpenAI/Gemini API usage
- Monitor rate limits
- Set up billing alerts
- Log AI operation errors

### Scaling Considerations

**Backend**:
- Start with 1-2 instances
- Add more instances as user base grows
- Use connection pooling for database
- Consider caching for frequent queries

**Frontend**:
- Vercel handles scaling automatically
- Enable edge caching for static assets
- Use ISR for dynamic routes if needed

**Database**:
- Neon auto-scales compute and storage
- Monitor active connections
- Add read replicas if needed
- Optimize slow queries

### Rollback Procedure

If deployment fails:

1. **Revert Backend**:
   ```bash
   # Railway
   railway rollback

   # Render
   # Use dashboard to rollback to previous deployment
   ```

2. **Revert Frontend**:
   - Go to Vercel dashboard
   - Select previous deployment
   - Click "Promote to Production"

3. **Rollback Database**:
   ```sql
   -- Revert migration (if needed)
   -- Create rollback script beforehand
   DROP TABLE IF EXISTS chat_messages;
   DROP TABLE IF EXISTS user_preferences;
   ALTER TABLE tasks DROP COLUMN created_via_ai;
   ALTER TABLE tasks DROP COLUMN ai_suggested_priority;
   ALTER TABLE tasks DROP COLUMN original_nl_input;
   ```

---

## 10. Next Steps

After local development is working:

1. **Run `/sp.tasks`** to generate implementation tasks
2. **Follow tasks.md** for structured implementation
3. **Test each user story** independently
4. **Deploy to staging** (Railway + Vercel)
5. **Production deployment** after testing

---

## 10. Resources

### Documentation
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Agents SDK Guide](https://github.com/anthropics/agents-sdk) (TBD)

### Specifications
- [spec.md](./spec.md) - Feature specification
- [plan.md](./plan.md) - Implementation plan
- [data-model.md](./data-model.md) - Database schema
- [contracts/chat-api.yaml](./contracts/chat-api.yaml) - API contract
- [contracts/mcp-protocol.md](./contracts/mcp-protocol.md) - MCP spec

### Support
- GitHub Issues: [project-repo]/issues
- Team Chat: [team-slack/discord]
- Documentation: specs/003-ai-chatbot-integration/

---

**Ready to start? Run `/sp.tasks` to generate implementation tasks!**
