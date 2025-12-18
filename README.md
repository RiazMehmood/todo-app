# Todo Application

A full-stack todo application with multi-user support, built using Spec-Driven Development with Claude Code and Spec-Kit Plus.

## Production Deployment

### Live Application

**Frontend**: https://todo-app-ashy-seven-25.vercel.app/login
**Backend API**: https://todo-app-production-be56.up.railway.app/

**Deployment Status**: ✅ Production (Phase II Complete)

### Production Features

- User signup and authentication with JWT tokens
- Create, read, update, delete tasks
- Mark tasks complete/incomplete
- Multi-user data isolation
- Responsive design for mobile and desktop
- Secure CORS configuration
- PostgreSQL database with Neon

## Project Phases

### Phase I: Console Application (Completed)
- Python CLI todo app with in-memory storage
- CRUD operations for tasks
- Foundation for subsequent phases

### Phase II: Full-Stack Web Application (Completed, Deployed)
- Next.js 16+ frontend with TypeScript
- FastAPI backend with Python 3.13+
- Neon PostgreSQL database
- Better Auth authentication
- Deployed to Vercel (frontend) and Railway (backend)

### Phase III: AI Integration (Planned)
- OpenAI ChatKit integration
- Agents SDK implementation
- Model Context Protocol (MCP)

### Phase IV: Container Orchestration (Planned)
- Docker containerization
- Kubernetes deployment with Minikube
- Helm charts

### Phase V: Event-Driven Architecture (Planned)
- Apache Kafka integration
- Dapr runtime
- Cloud deployment (DOKS/GKE/AKS)

## Technology Stack

### Frontend
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Authentication**: JWT tokens
- **Package Manager**: UV
- **Deployment**: Railway.app

### Database
- **Database**: Neon Serverless PostgreSQL
- **Connection**: Pooled connections
- **Hosting**: Neon Cloud

## Local Development

### Prerequisites

- **Node.js**: 18+ (for frontend)
- **Python**: 3.13+ (for backend)
- **UV**: Python package manager
- **PostgreSQL**: Neon account (or local PostgreSQL)

### Backend Setup

```bash
cd backend
uv sync
cp .env.example .env
# Edit .env with your database credentials
uvicorn src.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API URL
npm run dev
```

Frontend runs at: http://localhost:3000

## Project Structure

```
todo/
├── frontend/              # Next.js application
│   ├── app/              # Next.js App Router
│   ├── components/       # React components
│   ├── lib/              # Utilities and API client
│   └── public/           # Static assets
├── backend/              # FastAPI application
│   ├── src/
│   │   ├── models.py    # SQLModel models
│   │   ├── routes/      # API endpoints
│   │   ├── middleware/  # Auth middleware
│   │   └── main.py      # FastAPI app
│   └── pyproject.toml   # UV dependencies
├── specs/                # Feature specifications
│   ├── 001-todo-console-app/  # Phase I specs
│   └── 002-todo-web-app/      # Phase II specs
├── .specify/             # SpecKit Plus templates
├── history/              # Prompt History Records
│   ├── prompts/         # PHRs by feature
│   └── adr/             # Architecture Decision Records
└── CLAUDE.md            # Development guidelines
```

## Features

### User Stories (All Completed)

1. **US1: User Account Creation** - Signup with email/password
2. **US2: User Login** - JWT authentication
3. **US3: Create New Task** - Add tasks with title and description
4. **US4: View Task List** - See all user's tasks
5. **US5: Mark Complete/Incomplete** - Toggle task status
6. **US6: Update Task Details** - Edit title and description
7. **US7: Delete Task** - Permanently remove tasks
8. **US8: User Logout** - Clear session and redirect

### API Endpoints

```
POST   /api/auth/signup          # Create new user account
POST   /api/auth/login           # Authenticate user
GET    /api/{user_id}/tasks      # List all tasks for user
POST   /api/{user_id}/tasks      # Create new task
GET    /api/{user_id}/tasks/{id} # Get single task
PUT    /api/{user_id}/tasks/{id} # Update task
DELETE /api/{user_id}/tasks/{id} # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete  # Toggle completion
```

## Documentation

### Specifications
- [Project Overview](specs/overview.md)
- [System Architecture](specs/architecture.md)
- [Phase II Specification](specs/002-todo-web-app/spec.md)
- [Implementation Plan](specs/002-todo-web-app/plan.md)
- [Implementation Tasks](specs/002-todo-web-app/tasks.md)
- [Deployment Guide](specs/002-todo-web-app/deployment.md)

### Guidelines
- [Root Guidelines](CLAUDE.md)
- [Frontend Guidelines](frontend/CLAUDE.md)
- [Backend Guidelines](backend/CLAUDE.md)
- [Project Constitution](.specify/memory/constitution.md)

## Deployment

### Railway Backend Deployment

```bash
# Configure Railway project
railway init
railway link

# Add environment variables
railway variables set DATABASE_URL="postgres://..."
railway variables set BETTER_AUTH_SECRET="your-secret"
railway variables set CORS_ORIGINS="https://*.vercel.app"

# Deploy
git push origin 002-todo-web-app
```

### Vercel Frontend Deployment

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Add environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://todo-app-production-be56.up.railway.app
BETTER_AUTH_SECRET=your-secret
BETTER_AUTH_URL=https://todo-app-ashy-seven-25.vercel.app
```

See [Deployment Guide](specs/002-todo-web-app/deployment.md) for detailed instructions.

## Testing

All 8 user stories have been tested in production:

- ✅ User signup flow
- ✅ User login flow
- ✅ Create task
- ✅ View task list
- ✅ Mark task complete/incomplete
- ✅ Update task details
- ✅ Delete task
- ✅ User logout
- ✅ Multi-user data isolation
- ✅ CORS configuration
- ✅ Mobile responsiveness

## Security

- JWT token-based authentication
- Password hashing with passlib (bcrypt)
- CORS configured for specific origins
- Environment variables for secrets
- User data isolation at database level
- Protected API routes with middleware

## Performance

- Neon Serverless PostgreSQL with auto-scaling
- Database connection pooling
- Optimized database indexes
- Next.js App Router for optimal performance
- Static asset optimization

## Monitoring

- Railway deployment logs: [Railway Dashboard](https://railway.app)
- Vercel build logs: [Vercel Dashboard](https://vercel.com)
- Automatic deployments from GitHub
- Health check endpoint: `/health`

## License

See LICENSE file for details.

## Contributing

This project follows Spec-Driven Development. See [CLAUDE.md](CLAUDE.md) for development guidelines and workflow.

## Support

For issues or questions:
1. Check [Deployment Guide](specs/002-todo-web-app/deployment.md)
2. Review [Troubleshooting Section](specs/002-todo-web-app/deployment.md#troubleshooting)
3. Check project history in `history/prompts/002-todo-web-app/`

---

**Built with**: Claude Code + Spec-Kit Plus + Spec-Driven Development
