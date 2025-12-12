# Quick Start Guide

**Feature**: 002-todo-web-app
**Date**: 2025-12-09
**Purpose**: Get the full-stack todo application running locally

## Prerequisites

Before starting, ensure you have the following installed:

- **Node.js**: v18.0.0 or higher (for frontend)
- **Python**: 3.13 or higher (for backend)
- **UV**: Python package manager ([install here](https://github.com/astral-sh/uv))
- **Git**: For version control
- **PostgreSQL Client** (optional): For database inspection

## Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Frontend      │  HTTP   │    Backend      │  SQL    │    Database     │
│   Next.js       │ ───────>│    FastAPI      │ ───────>│  Neon PostgreSQL│
│   :3000         │ <───────│    :8000        │ <───────│  (Cloud)        │
└─────────────────┘  JSON   └─────────────────┘         └─────────────────┘
```

## Step 1: Clone and Setup

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd todo

# Checkout the feature branch
git checkout 002-todo-web-app
```

## Step 2: Set Up Neon Database

1. **Create Neon Account**:
   - Go to [neon.tech](https://neon.tech)
   - Sign up for free account
   - Create a new project (name: "todo-app")

2. **Get Connection String**:
   - Copy the connection string from Neon dashboard
   - Format: `postgresql://username:password@host:port/database?sslmode=require`

3. **Keep Connection String Handy**:
   - You'll need this for the backend `.env` file

## Step 3: Set Up Backend (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with UV
uv venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Create .env file from example
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Backend .env Configuration**:

```bash
# Required: Your Neon PostgreSQL connection string
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require

# Required: Shared secret for JWT (must match frontend)
# Generate a secure random string (min 32 chars):
# python -c "import secrets; print(secrets.token_urlsafe(32))"
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars

# Optional: CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourapp.vercel.app
```

**Create Database Tables**:

```bash
# Run this Python command to create tables
python -c "from src.db import create_db_and_tables; create_db_and_tables()"
```

**Start Backend Server**:

```bash
# Start development server with auto-reload
uvicorn src.main:app --reload --port 8000
```

**Verify Backend**:
- Open [http://localhost:8000](http://localhost:8000) → Should see `{"message": "Todo API - Phase II"}`
- Open [http://localhost:8000/docs](http://localhost:8000/docs) → Should see Swagger UI with API endpoints
- Open [http://localhost:8000/health](http://localhost:8000/health) → Should see `{"status": "healthy"}`

## Step 4: Set Up Frontend (Next.js)

**Open a new terminal** (keep backend running):

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env.local file from example
cp .env.example .env.local

# Edit .env.local file
nano .env.local  # or use your preferred editor
```

**Frontend .env.local Configuration**:

```bash
# Required: Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Required: Shared secret for JWT (MUST match backend)
BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars

# Required: Frontend URL
BETTER_AUTH_URL=http://localhost:3000
```

**Important**: The `BETTER_AUTH_SECRET` **MUST be identical** in both frontend and backend `.env` files!

**Start Frontend Server**:

```bash
# Start development server
npm run dev
```

**Verify Frontend**:
- Open [http://localhost:3000](http://localhost:3000) → Should see homepage
- Should be able to navigate to signup and login pages

## Step 5: Test the Application

### Create an Account

1. Navigate to [http://localhost:3000/signup](http://localhost:3000/signup)
2. Fill in the form:
   - **Name**: Your name
   - **Email**: your@email.com
   - **Password**: At least 8 characters
3. Click "Sign Up"
4. You should be redirected to the dashboard

### Create a Task

1. On the dashboard, find the "Add Task" form
2. Enter a task title (e.g., "Buy groceries")
3. Optionally add a description
4. Click "Add Task"
5. Task should appear in the task list

### Mark Task Complete

1. Click the checkbox next to the task
2. Task should show strikethrough or completion styling
3. Refresh the page → Task should remain completed

### Edit a Task

1. Click the "Edit" button on a task
2. Modify the title or description
3. Save changes
4. Changes should persist

### Delete a Task

1. Click the "Delete" button on a task
2. Confirm deletion (if confirmation modal present)
3. Task should be removed from the list

### Test Multi-User Isolation

1. Log out of your account
2. Create a second account with different email
3. Create tasks under second account
4. Log back into first account
5. Verify you only see tasks from first account (not second account's tasks)

## Common Issues and Solutions

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
uv pip install -e .
```

---

**Issue**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution**:
- Verify DATABASE_URL in `backend/.env` is correct
- Check Neon database is running (visit Neon dashboard)
- Ensure connection string includes `?sslmode=require`

---

**Issue**: `JWT token verification fails`

**Solution**:
- Ensure `BETTER_AUTH_SECRET` is **identical** in `backend/.env` and `frontend/.env.local`
- Both secrets must be at least 32 characters
- Restart both frontend and backend servers after changing secrets

---

### Frontend Issues

**Issue**: `Module not found: Can't resolve 'better-auth'`

**Solution**:
```bash
# Install dependencies
npm install
```

---

**Issue**: `CORS Error: Access to fetch blocked`

**Solution**:
- Ensure backend `CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Restart backend server after changing `.env`

---

**Issue**: `API requests return 401 Unauthorized`

**Solution**:
- Clear browser cookies and localStorage
- Log out and log back in to get fresh JWT token
- Check browser console for error messages

---

## Development Workflow

### Making Changes

**Backend Changes**:
1. Edit files in `backend/src/`
2. Uvicorn will auto-reload on file changes
3. Refresh API docs at http://localhost:8000/docs

**Frontend Changes**:
1. Edit files in `frontend/app/` or `frontend/components/`
2. Next.js will hot-reload automatically
3. Changes appear immediately in browser

### Code Structure

**Backend**:
- `backend/src/main.py`: FastAPI app, CORS, routes
- `backend/src/models.py`: SQLModel database models
- `backend/src/db.py`: Database connection
- `backend/src/middleware/auth.py`: JWT verification
- `backend/src/routes/tasks.py`: Task CRUD endpoints

**Frontend**:
- `frontend/app/`: Next.js pages (login, signup, dashboard)
- `frontend/components/`: React components (TaskList, TaskItem, forms)
- `frontend/lib/api.ts`: API client with JWT handling
- `frontend/lib/auth.ts`: Better Auth configuration

### Environment Variables Reference

| Variable | Location | Purpose | Example |
|----------|----------|---------|---------|
| `DATABASE_URL` | `backend/.env` | Neon PostgreSQL connection | `postgresql://user:pass@host/db?sslmode=require` |
| `BETTER_AUTH_SECRET` | `backend/.env` AND `frontend/.env.local` | JWT secret (MUST match!) | `abc123...` (32+ chars) |
| `CORS_ORIGINS` | `backend/.env` | Allowed frontend origins | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | `frontend/.env.local` | Backend API URL | `http://localhost:8000` |
| `BETTER_AUTH_URL` | `frontend/.env.local` | Frontend URL | `http://localhost:3000` |

## API Testing with Swagger UI

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click "Authorize" button
3. Enter JWT token (get from browser localStorage or network tab after login)
   - Format: `Bearer <token>`
4. Try API endpoints interactively

## Database Inspection

**Using psql**:
```bash
# Connect to Neon database
psql <DATABASE_URL>

# List tables
\dt

# View tasks
SELECT * FROM tasks;

# View users
SELECT id, email, name FROM users;

# Exit
\q
```

**Using Neon Dashboard**:
1. Go to Neon dashboard
2. Click on your project
3. Navigate to "Tables" tab
4. View and query data directly

## Next Steps

Once you have the application running:

1. **Read the Specifications**:
   - `specs/002-todo-web-app/spec.md`: Feature requirements
   - `specs/002-todo-web-app/plan.md`: Implementation plan
   - `specs/002-todo-web-app/data-model.md`: Database schema

2. **Review the Code Guidelines**:
   - `backend/CLAUDE.md`: Backend development patterns
   - `frontend/CLAUDE.md`: Frontend development patterns
   - Root `CLAUDE.md`: Overall project guidelines

3. **Start Implementing**:
   - Run `/sp.tasks` to generate task list
   - Follow task-by-task implementation workflow
   - Create PHRs (Prompt History Records) for each session

4. **Test Thoroughly**:
   - Manual testing of all user stories
   - Test edge cases (validation, security, errors)
   - Use checklist in `specs/002-todo-web-app/checklists/requirements.md`

5. **Deploy**:
   - Frontend: `cd frontend && vercel deploy`
   - Backend: Deploy to Vercel Serverless, Railway, or Render
   - Database: Already on Neon (no deployment needed)

## Useful Commands

```bash
# Backend
cd backend
source .venv/bin/activate     # Activate venv
uvicorn src.main:app --reload # Run server
python -c "from src.db import create_db_and_tables; create_db_and_tables()" # Create tables
uv pip install <package>      # Install package

# Frontend
cd frontend
npm install                   # Install dependencies
npm run dev                   # Run dev server
npm run build                 # Build for production
npm run start                 # Run production build

# Git
git status                    # Check status
git add .                     # Stage changes
git commit -m "message"       # Commit changes
git push                      # Push to remote
```

## Support

If you encounter issues:
1. Check this quickstart guide
2. Review error messages carefully
3. Check `backend/README.md` and `frontend/README.md`
4. Verify environment variables are set correctly
5. Ensure both servers are running
6. Check browser console and terminal for errors

---

**Happy Coding!** 🚀
