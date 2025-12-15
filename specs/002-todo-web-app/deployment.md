# Deployment Guide - Full-Stack Todo Application

**Feature**: 002-todo-web-app
**Date**: 2025-12-15
**Target Platform**: Railway.app (Backend) + Vercel (Frontend)

## Overview

This guide walks through deploying the full-stack todo application to production:
- **Backend**: FastAPI deployed to Railway.app
- **Frontend**: Next.js deployed to Vercel
- **Database**: Neon Serverless PostgreSQL (already configured)

## Prerequisites

- [ ] GitHub repository with `002-todo-web-app` branch
- [ ] Neon PostgreSQL database created with connection string
- [ ] Railway.app account (free tier available)
- [ ] Vercel account (free tier available)
- [ ] Better Auth secret key (32+ characters)

---

## Part 1: Backend Deployment to Railway.app

### Step 1: Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Select the `002-todo-web-app` branch

### Step 2: Configure Railway Project

#### A. Set Root Directory

Railway needs to deploy from the `backend/` directory:

1. Go to **Project Settings**
2. Under **"Deploy"** tab, set:
   - **Root Directory**: `backend`
   - **Builder**: Nixpacks (auto-detected)

#### B. Configure Build Settings

Railway uses the `backend/railway.json` configuration:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

This is already configured in the repository.

### Step 3: Add Environment Variables

In Railway project settings, add these environment variables:

#### DATABASE_URL
```
postgresql://username:password@host:port/database?sslmode=require
```
- **Source**: Your Neon PostgreSQL connection string
- **How to get**: Neon Dashboard → Connection Details → Connection String

#### BETTER_AUTH_SECRET
```
your-secret-key-minimum-32-characters-long
```
- **Source**: Generate a secure random string (32+ chars)
- **Command**: `openssl rand -base64 32`
- **CRITICAL**: This MUST match the frontend secret

#### CORS_ORIGINS
```
http://localhost:3000,https://your-app.vercel.app
```
- **Local**: `http://localhost:3000` (for development)
- **Production**: Add your Vercel URL after Step 4

**Note**: You'll update this after getting your Vercel URL.

### Step 4: Deploy Backend

1. Click **"Deploy"** in Railway dashboard
2. Monitor build logs for errors
3. Wait for deployment to complete
4. Copy the **Railway deployment URL** (e.g., `https://todo-backend-production.up.railway.app`)

### Step 5: Test Backend Health Endpoint

Test that the backend is running:

```bash
curl https://your-railway-url.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

Also test the API docs:
```
https://your-railway-url.railway.app/docs
```

You should see the Swagger UI.

### Step 6: Update CORS_ORIGINS

After deploying the frontend to Vercel (Part 2), return here and update `CORS_ORIGINS`:

1. Go to Railway project settings
2. Edit `CORS_ORIGINS` variable
3. Add your Vercel URL:
   ```
   http://localhost:3000,https://your-app.vercel.app
   ```
4. Railway will automatically redeploy

---

## Part 2: Frontend Deployment to Vercel

### Step 1: Create Vercel Project

1. Go to [Vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click **"Add New Project"**
4. Import your GitHub repository
5. Select the `002-todo-web-app` branch

### Step 2: Configure Vercel Project Settings

#### Framework Preset
- **Framework**: Next.js (auto-detected)
- **Root Directory**: `frontend`

#### Build & Development Settings
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Install Command**: `npm install` (default)
- **Development Command**: `npm run dev` (default)

### Step 3: Add Environment Variables

In Vercel project settings → Environment Variables, add:

#### NEXT_PUBLIC_API_URL
```
https://your-railway-url.railway.app
```
- **Source**: Your Railway backend URL from Part 1, Step 4
- **Important**: This MUST be your Railway URL, not localhost
- **Environments**: Production, Preview, Development

#### BETTER_AUTH_SECRET
```
your-secret-key-minimum-32-characters-long
```
- **Source**: SAME value as Railway backend
- **CRITICAL**: Must match backend secret exactly
- **Environments**: Production, Preview, Development

#### BETTER_AUTH_URL
```
https://your-app.vercel.app
```
- **Source**: Your Vercel deployment URL (auto-assigned)
- **Important**: Update this after first deployment
- **Environments**: Production, Preview, Development

**Initial Deployment**: Use a placeholder (e.g., `https://localhost:3000`) for first deploy, then update after getting actual URL.

### Step 4: Deploy Frontend

1. Click **"Deploy"**
2. Monitor build logs
3. Wait for deployment to complete (2-3 minutes)
4. Copy the **Vercel deployment URL** (e.g., `https://todo-app-xyz.vercel.app`)

### Step 5: Update Environment Variables with Actual URL

After deployment completes:

1. Go to Vercel project settings → Environment Variables
2. Update `BETTER_AUTH_URL` with your actual Vercel URL
3. Trigger redeploy:
   - Settings → Deployments → Latest Deployment → **"Redeploy"**

### Step 6: Update Railway CORS_ORIGINS

Return to Railway and update `CORS_ORIGINS` to include your Vercel URL (see Part 1, Step 6).

---

## Part 3: Integration Testing

### Test 1: Health Check

```bash
# Backend health
curl https://your-railway-url.railway.app/health

# Frontend (open in browser)
https://your-vercel-url.vercel.app
```

### Test 2: Signup Flow

1. Open frontend URL in browser
2. Navigate to signup page
3. Create account with:
   - Name: Test User
   - Email: test@example.com
   - Password: password123
4. **Expected**: Account created → JWT issued → Redirected to dashboard

### Test 3: Create Task

1. Login to account
2. Create new task:
   - Title: "Test deployment"
   - Description: "Verify production works"
3. **Expected**: Task appears in list

### Test 4: CORS Verification

1. Open browser DevTools (F12) → Console
2. Perform any action (create task, toggle complete, etc.)
3. **Expected**: No CORS errors in console
4. **If CORS errors**: Check Railway `CORS_ORIGINS` includes Vercel URL

### Test 5: Multi-User Isolation

1. Create second account (different email)
2. Create tasks in second account
3. Switch back to first account
4. **Expected**: Cannot see second user's tasks

### Test 6: Mobile Responsiveness

1. Open frontend on mobile device or DevTools → Device Mode
2. Test all user flows
3. **Expected**: UI is responsive and usable

---

## Part 4: Troubleshooting

### Issue: Build Fails on Vercel

**Symptom**: `Module not found` errors or TypeScript errors

**Solution**:
1. Check `frontend/tsconfig.json` has `"jsx": "preserve"`
2. Verify `frontend/vercel.json` doesn't have invalid `env` config
3. Run `npm install` locally to verify dependencies
4. Check build logs for specific error

**Fixed in**: Commit `96293e5` and `ee00c9c`

### Issue: Backend Returns 401 for All Requests

**Symptom**: All API calls return `{"detail": "Invalid token"}`

**Cause**: `BETTER_AUTH_SECRET` mismatch between frontend and backend

**Solution**:
1. Verify Railway `BETTER_AUTH_SECRET` value
2. Verify Vercel `BETTER_AUTH_SECRET` value
3. Ensure they are IDENTICAL (case-sensitive)
4. Redeploy both if changed

### Issue: CORS Errors in Browser Console

**Symptom**: `Access-Control-Allow-Origin` error

**Cause**: Railway `CORS_ORIGINS` doesn't include Vercel URL

**Solution**:
1. Go to Railway project settings
2. Update `CORS_ORIGINS` to include:
   ```
   http://localhost:3000,https://your-app.vercel.app
   ```
3. Railway auto-redeploys
4. Hard refresh browser (Ctrl+Shift+R)

### Issue: Database Connection Fails

**Symptom**: `500 Internal Server Error` on all API calls

**Cause**: Invalid `DATABASE_URL` or database not accessible

**Solution**:
1. Verify Neon database is running
2. Check Railway `DATABASE_URL` format:
   ```
   postgresql://user:pass@host:port/db?sslmode=require
   ```
3. Test connection from Railway logs
4. Ensure Neon allows connections from Railway IP

### Issue: Frontend Shows "Network Error"

**Symptom**: API calls fail with network error

**Cause**: Incorrect `NEXT_PUBLIC_API_URL`

**Solution**:
1. Verify Vercel `NEXT_PUBLIC_API_URL` is Railway URL
2. Ensure Railway backend is running (check health endpoint)
3. Check Railway URL is HTTPS (not HTTP)
4. Redeploy Vercel after changing env var

### Issue: JWT Token Expired Mid-Session

**Symptom**: User gets logged out unexpectedly

**Cause**: Token expiration (default 7 days)

**Solution**:
1. This is expected behavior for security
2. User should login again
3. To extend: Modify JWT expiry in Better Auth config
4. Consider implementing refresh tokens in Phase III

---

## Part 5: Monitoring & Maintenance

### Railway Logs

View backend logs:
1. Go to Railway project dashboard
2. Click on deployment
3. View **"Logs"** tab
4. Filter by errors: Search for `ERROR` or `500`

### Vercel Build Logs

View frontend build logs:
1. Go to Vercel project dashboard
2. Click on **"Deployments"**
3. Click on specific deployment
4. View **"Build Logs"** and **"Runtime Logs"**

### Deployment Notifications

#### Railway Notifications
1. Project Settings → Notifications
2. Add email or Slack webhook
3. Get notified on deployment failures

#### Vercel Notifications
1. Project Settings → Notifications
2. Enable deployment notifications
3. Configure for production deployments only

### Automatic Deployments

Both Railway and Vercel auto-deploy on git push:

1. Push to `002-todo-web-app` branch
2. Railway auto-deploys backend
3. Vercel auto-deploys frontend
4. Monitor both dashboards for success

### Rollback Procedure

#### Railway Rollback
1. Go to Deployments tab
2. Find previous successful deployment
3. Click **"Redeploy"**

#### Vercel Rollback
1. Go to Deployments tab
2. Find previous working deployment
3. Click **"⋯"** → **"Promote to Production"**

---

## Part 6: Security Checklist

- [ ] **HTTPS Only**: Both Railway and Vercel use HTTPS by default
- [ ] **Environment Variables**: All secrets stored in platform dashboards (not in code)
- [ ] **CORS**: Railway only allows requests from Vercel URL
- [ ] **JWT Verification**: Backend verifies all tokens
- [ ] **Data Isolation**: Users can only access their own tasks
- [ ] **SQL Injection**: SQLModel uses parameterized queries
- [ ] **No Secrets in Git**: `.env` files are `.gitignore`d

---

## Part 7: Production URLs

After deployment, document your URLs:

### Backend (Railway)
```
Production URL: https://todo-backend-production.up.railway.app
Health Endpoint: https://todo-backend-production.up.railway.app/health
API Docs: https://todo-backend-production.up.railway.app/docs
```

### Frontend (Vercel)
```
Production URL: https://todo-app-xyz.vercel.app
Login Page: https://todo-app-xyz.vercel.app/login
Dashboard: https://todo-app-xyz.vercel.app/dashboard
```

### Database (Neon)
```
Provider: Neon Serverless PostgreSQL
Region: [Your region]
Connection: Via Railway env var (not exposed publicly)
```

---

## Part 8: Cost Estimate

### Free Tier Limits

**Railway.app (Free Tier)**
- $5 credit per month
- ~500 hours execution time
- 512MB RAM, 1 vCPU
- Auto-sleeps after 30min inactivity

**Vercel (Hobby Tier)**
- Free for personal projects
- 100GB bandwidth per month
- Unlimited deployments
- Serverless function execution

**Neon PostgreSQL (Free Tier)**
- 3GB storage
- 1 project
- Auto-suspend after 5min inactivity
- Unlimited compute hours

**Total Cost**: $0/month for hackathon demo and low-traffic usage

---

## Part 9: Next Steps

### After Deployment
1. ✅ Test all 8 user stories in production
2. ✅ Record demo video showing app functionality
3. ✅ Update README.md with production URLs
4. ✅ Share production URL with hackathon organizers

### Phase III Enhancements
- Add OpenAI ChatKit integration
- Implement Claude Agents SDK
- Add Model Context Protocol (MCP)
- See `specs/overview.md` for Phase III details

---

## Summary Checklist

### Backend (Railway)
- [ ] Railway project created
- [ ] Connected to GitHub repo
- [ ] Root directory set to `backend`
- [ ] Environment variables configured (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS)
- [ ] Deployment successful
- [ ] Health endpoint returns 200 OK
- [ ] API docs accessible

### Frontend (Vercel)
- [ ] Vercel project created
- [ ] Framework set to Next.js
- [ ] Root directory set to `frontend`
- [ ] Environment variables configured (NEXT_PUBLIC_API_URL, BETTER_AUTH_SECRET, BETTER_AUTH_URL)
- [ ] Build successful (no errors)
- [ ] Deployment successful
- [ ] Login/signup pages load correctly

### Integration
- [ ] CORS configured correctly (no browser errors)
- [ ] Signup flow works end-to-end
- [ ] Task CRUD operations work in production
- [ ] Multi-user isolation verified
- [ ] Mobile responsiveness tested

### Documentation
- [ ] Production URLs documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide complete
- [ ] README.md updated

---

**Deployment Complete!** Your full-stack todo application is now live in production.

**Questions?** Check troubleshooting section or view deployment logs in Railway/Vercel dashboards.
