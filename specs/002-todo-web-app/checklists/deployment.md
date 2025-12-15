# Deployment Checklist - Production Release

**Feature**: 002-todo-web-app
**Created**: 2025-12-15
**Status**: In Progress

## Pre-Deployment Checklist

### Code & Configuration
- [X] All Phase 1-11 tasks completed (T001-T131)
- [X] Frontend builds successfully without errors (`npm run build`)
- [X] Backend runs without errors locally (`uvicorn src.main:app`)
- [X] Database schema created in Neon PostgreSQL
- [X] Environment variable examples documented (.env.example files)
- [X] CORS configured for local development
- [X] JWT authentication working locally
- [X] All user stories (US1-US8) tested locally

### Repository Setup
- [X] Code pushed to GitHub repository
- [X] Branch `002-todo-web-app` exists
- [X] .gitignore excludes sensitive files (.env, __pycache__, node_modules, etc.)
- [X] Railway configuration exists (backend/railway.json)
- [X] Vercel configuration exists (frontend/vercel.json)
- [X] No secrets committed to repository

---

## Backend Deployment (Railway.app)

### Account & Project Setup
- [ ] Railway.app account created
- [ ] New Railway project created
- [ ] GitHub repository connected to Railway
- [ ] Deploy branch set to `002-todo-web-app`

### Configuration
- [ ] Root directory set to `backend`
- [ ] Builder set to Nixpacks (auto-detected)
- [ ] Start command verified: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- [ ] Restart policy configured (ON_FAILURE, max 10 retries)

### Environment Variables
- [ ] `DATABASE_URL` added (Neon PostgreSQL connection string)
- [ ] `BETTER_AUTH_SECRET` added (32+ character random string)
- [ ] `CORS_ORIGINS` added (initially: `http://localhost:3000`)
- [ ] All env vars verified (no typos, correct format)

### Deployment & Testing
- [ ] Initial deployment triggered
- [ ] Build logs reviewed (no errors)
- [ ] Deployment succeeded
- [ ] Railway URL copied and documented
- [ ] Health endpoint tested: `curl https://[railway-url]/health` → `{"status":"healthy"}`
- [ ] API docs accessible: `https://[railway-url]/docs`

### Post-Deployment Updates
- [ ] Vercel URL obtained (after frontend deployment)
- [ ] `CORS_ORIGINS` updated to include Vercel URL
- [ ] Railway auto-redeployment successful
- [ ] CORS verified (no browser console errors)

---

## Frontend Deployment (Vercel)

### Account & Project Setup
- [ ] Vercel account created
- [ ] New Vercel project created
- [ ] GitHub repository imported
- [ ] Deploy branch set to `002-todo-web-app`

### Configuration
- [ ] Framework preset: Next.js (auto-detected)
- [ ] Root directory set to `frontend`
- [ ] Build command: `npm run build`
- [ ] Output directory: `.next`
- [ ] Install command: `npm install`

### Environment Variables
- [ ] `NEXT_PUBLIC_API_URL` added (Railway backend URL)
- [ ] `BETTER_AUTH_SECRET` added (SAME as Railway backend)
- [ ] `BETTER_AUTH_URL` added (initially placeholder, updated after deployment)
- [ ] All env vars applied to: Production, Preview, Development
- [ ] Env var values verified (no typos, correct URLs)

### Deployment & Testing
- [ ] Initial deployment triggered
- [ ] Build logs reviewed (no TypeScript/module errors)
- [X] `frontend/tsconfig.json` has `"jsx": "preserve"` (fixed in commit 96293e5)
- [X] `frontend/vercel.json` has no invalid `env` config (fixed in commit ee00c9c)
- [ ] Build succeeded without errors
- [ ] Deployment succeeded
- [ ] Vercel URL copied and documented
- [ ] Login page loads: `https://[vercel-url]/login`
- [ ] Signup page loads: `https://[vercel-url]/signup`
- [ ] No console errors in browser DevTools

### Post-Deployment Updates
- [ ] `BETTER_AUTH_URL` updated with actual Vercel URL
- [ ] Vercel redeployment triggered
- [ ] Redeployment successful

---

## Integration Testing (Production)

### Authentication Flow
- [ ] **Signup**: Create account → JWT issued → Redirected to dashboard
- [ ] **Signup Error**: Existing email → "Email already registered" error
- [ ] **Signup Validation**: Password < 8 chars → Validation error
- [ ] **Login**: Correct credentials → JWT issued → Dashboard accessible
- [ ] **Login Error**: Invalid credentials → "Invalid credentials" error
- [ ] **Protected Route**: Access `/dashboard` without login → Redirected to `/login`

### Task Management Flow
- [ ] **Create Task**: Add task with title → Task created → Appears in list
- [ ] **Create Task**: Add task with description → Description saved
- [ ] **View Tasks**: Multiple tasks → All displayed, newest first
- [ ] **Empty State**: No tasks → "No tasks yet" message shown
- [ ] **Mark Complete**: Toggle checkbox → Task strikethrough → Status persists on refresh
- [ ] **Edit Task**: Update title/description → Changes saved → `updated_at` timestamp changed
- [ ] **Delete Task**: Confirm deletion → Task removed from database and UI
- [ ] **Delete Cancel**: Click "Cancel" → Task remains

### Security & Data Isolation
- [ ] **User Isolation**: User A creates tasks → User B cannot see them
- [ ] **Authorization**: User A tries to access User B's task (manipulate URL) → HTTP 403
- [ ] **Invalid Token**: Remove/modify JWT token → HTTP 401 Unauthorized
- [ ] **Expired Token**: Wait for token expiry → Redirected to login
- [ ] **CORS**: No CORS errors in browser console during API calls

### Performance
- [ ] Task list loads in < 1 second (for < 100 tasks)
- [ ] Task creation completes in < 3 seconds end-to-end
- [ ] Signup completes in < 10 seconds
- [ ] Optimistic UI updates provide immediate feedback

### Cross-Browser & Device Testing
- [ ] Chrome (desktop) - all features work
- [ ] Firefox (desktop) - all features work
- [ ] Safari (desktop/mobile) - all features work
- [ ] Edge (desktop) - all features work
- [ ] Mobile (iPhone/Android) - responsive design works
- [ ] Tablet - responsive design works
- [ ] Screen sizes: 320px to 2560px width - UI adapts correctly

---

## Monitoring & Maintenance

### Deployment Notifications
- [ ] Railway deployment notifications configured (email or Slack)
- [ ] Vercel deployment notifications configured
- [ ] Test notification by triggering deployment

### Automatic Deployments
- [ ] Push to `002-todo-web-app` branch → Railway auto-deploys backend
- [ ] Push to `002-todo-web-app` branch → Vercel auto-deploys frontend
- [ ] Verified auto-deployment works (make small change, push, verify deployment)

### Logging & Debugging
- [ ] Know how to access Railway logs (Project → Deployment → Logs)
- [ ] Know how to access Vercel build logs (Project → Deployments → Build Logs)
- [ ] Know how to access Vercel runtime logs (Project → Deployments → Runtime Logs)
- [ ] Test log viewing (trigger error, find in logs)

### Rollback Procedure
- [ ] Tested Railway rollback (Deployments → Previous deployment → Redeploy)
- [ ] Tested Vercel rollback (Deployments → Previous deployment → Promote to Production)
- [ ] Documented rollback steps in deployment guide

---

## Documentation

### Deployment Guide
- [X] Created `specs/002-todo-web-app/deployment.md`
- [ ] Railway deployment steps documented
- [ ] Vercel deployment steps documented
- [ ] Environment variable requirements documented
- [ ] Troubleshooting section complete
- [ ] Security checklist included

### README Updates
- [ ] Production URLs added to README.md
- [ ] Deployment status documented
- [ ] User instructions for accessing production app
- [ ] Environment setup instructions for contributors

### Environment Variable Documentation
- [X] `backend/.env.example` exists and is up-to-date
- [X] `frontend/.env.example` exists and is up-to-date
- [ ] Production env var values documented securely (not in repo)
- [ ] Team has access to production secrets (secure sharing method)

---

## Post-Deployment Tasks

### Task List Updates
- [ ] Mark deployment tasks (T132-T173) as completed in `specs/002-todo-web-app/tasks.md`
- [ ] Update task completion status with [X]
- [ ] Document actual Railway URL in tasks.md
- [ ] Document actual Vercel URL in tasks.md

### Requirements Checklist
- [ ] Update `specs/002-todo-web-app/checklists/requirements.md`
- [ ] Mark deployment-related requirements as complete:
  - [ ] SC-009: Frontend deploys to Vercel without build errors
  - [ ] SC-010: Backend connects to Neon PostgreSQL and performs CRUD operations
- [ ] Verify all functional requirements (FR-001 to FR-020) tested in production
- [ ] Verify all user stories (US-1 to US-8) work in production

### Demo & Presentation
- [ ] Record 90-second demo video showing:
  - Signup flow
  - Task creation
  - Task completion toggle
  - Task editing
  - Task deletion
  - Logout
- [ ] Prepare deployment architecture diagram
- [ ] Document tech stack used
- [ ] Prepare hackathon submission

---

## Production URLs

### Backend (Railway)
```
URL: [Your Railway URL here]
Health: [Your Railway URL]/health
API Docs: [Your Railway URL]/docs
```

### Frontend (Vercel)
```
URL: [Your Vercel URL here]
Login: [Your Vercel URL]/login
Dashboard: [Your Vercel URL]/dashboard
```

### Database (Neon)
```
Provider: Neon Serverless PostgreSQL
Region: [Your region]
Status: Active
```

---

## Definition of Done

### Backend Deployment
- [ ] Railway deployment successful
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible
- [ ] Environment variables configured
- [ ] CORS allows Vercel domain
- [ ] Database connection working

### Frontend Deployment
- [ ] Vercel build successful (no errors)
- [ ] Deployment successful
- [ ] Login/signup pages load
- [ ] Environment variables configured
- [ ] No console errors in browser
- [ ] API calls to Railway backend succeed

### Integration
- [ ] All 8 user stories work in production
- [ ] No CORS errors
- [ ] Multi-user data isolation verified
- [ ] Security requirements met
- [ ] Performance requirements met
- [ ] Responsive design works on all devices

### Documentation
- [ ] Deployment guide complete
- [ ] Troubleshooting guide complete
- [ ] README updated with production URLs
- [ ] Environment variables documented
- [ ] Rollback procedure documented

---

**Status**: Use this checklist to track deployment progress. Check off items as completed.

**Next Steps After Completion**:
1. Test all user flows in production
2. Record demo video
3. Submit hackathon entry
4. Plan Phase III enhancements
