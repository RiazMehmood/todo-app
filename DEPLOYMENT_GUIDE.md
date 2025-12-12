# Deployment Guide - Phase 2 Todo Application

**Status**: Ready for Deployment ✅
**Target**: Production deployment to Vercel (frontend) + Railway/Render (backend)

---

## Pre-Deployment Checklist

Before deploying, ensure:

- [x] All manual tests passed (see TESTING_GUIDE.md)
- [x] Backend runs locally without errors
- [x] Frontend runs locally without errors
- [x] Database migration applied (indexes created)
- [x] Environment variables configured for local development
- [ ] GitHub repository is up to date
- [ ] No sensitive data (secrets, API keys) committed to git

---

## Deployment Overview

We'll deploy in this order:
1. **Backend first** → Get production API URL
2. **Frontend second** → Configure with backend URL

**Recommended Platforms:**
- Backend: Railway.app (free tier, easy setup)
- Frontend: Vercel (free tier, automatic deployments)
- Database: Neon PostgreSQL (already set up)

---

## Part 1: Deploy Backend to Railway

### Step 1.1: Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub account
3. Verify email

### Step 1.2: Install Railway CLI (Optional)

```bash
npm install -g @railway/cli
railway login
```

Or use the web dashboard (easier for first deployment).

### Step 1.3: Create New Project

**Via Web Dashboard:**
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Select your `todo` repository
5. Choose "backend" as root directory

**Via CLI:**
```bash
cd backend
railway init
railway link
```

### Step 1.4: Configure Environment Variables

In Railway dashboard, go to Variables tab and add:

```bash
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
# ↑ Copy from your Neon dashboard

BETTER_AUTH_SECRET=your-secret-key-32-chars-minimum
# ↑ Generate new: python3 -c "import secrets; print(secrets.token_urlsafe(32))"

JWT_ALGORITHM=HS256

JWT_EXPIRATION_DAYS=7

CORS_ORIGINS=https://your-frontend-url.vercel.app
# ↑ We'll update this after deploying frontend
```

**Important Notes:**
- Use the **same** `BETTER_AUTH_SECRET` as local development (or generate a new one for production)
- We'll update `CORS_ORIGINS` after deploying the frontend
- Keep `DATABASE_URL` from Neon (production database)

### Step 1.5: Configure Build Settings

Railway should auto-detect Python. Verify:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

These are configured in `railway.json` and `Procfile`.

### Step 1.6: Deploy Backend

**Via Dashboard:**
- Click "Deploy" button
- Wait for build to complete (2-5 minutes)

**Via CLI:**
```bash
cd backend
railway up
```

### Step 1.7: Get Backend URL

After deployment completes:

**Via Dashboard:**
- Go to Settings → Domains
- Click "Generate Domain"
- Copy the URL: `https://your-backend.railway.app`

**Via CLI:**
```bash
railway domain
```

### Step 1.8: Verify Backend Deployment

Test the backend:

```bash
# Health check
curl https://your-backend.railway.app/health

# Expected response:
# {"status":"healthy","service":"todo-api","version":"2.0.0"}

# API documentation
open https://your-backend.railway.app/docs
```

**Checklist:**
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] API docs accessible at `/docs`
- [ ] No errors in Railway logs

---

## Part 2: Deploy Frontend to Vercel

### Step 2.1: Create Vercel Account

1. Go to https://vercel.com
2. Sign up with GitHub account
3. Import your `todo` repository

### Step 2.2: Configure Project Settings

When importing:

1. **Framework Preset**: Next.js (auto-detected)
2. **Root Directory**: `frontend`
3. **Build Command**: `npm run build` (default)
4. **Output Directory**: `.next` (default)
5. **Install Command**: `npm install` (default)

### Step 2.3: Configure Environment Variables

In Vercel dashboard, go to Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
# ↑ Use the Railway URL from Step 1.7

BETTER_AUTH_SECRET=same-secret-as-backend
# ↑ MUST match the backend BETTER_AUTH_SECRET

BETTER_AUTH_URL=https://your-app.vercel.app
# ↑ Will be provided after first deployment, update later
```

**Important:**
- `BETTER_AUTH_SECRET` must **exactly match** the backend secret
- Use the Railway backend URL (no trailing slash)

### Step 2.4: Deploy Frontend

Click **"Deploy"** button.

Vercel will:
1. Clone your repo
2. Install dependencies (`npm install`)
3. Build Next.js app (`npm run build`)
4. Deploy to production

This takes 2-5 minutes.

### Step 2.5: Get Frontend URL

After deployment:
- Vercel provides: `https://your-app.vercel.app`
- Or custom domain: `https://yourdomain.com`

### Step 2.6: Update Backend CORS

Now that you have the frontend URL, update the backend:

**In Railway dashboard:**
1. Go to Variables
2. Update `CORS_ORIGINS` to: `https://your-app.vercel.app`
3. Redeploy backend (click "Redeploy")

**Or via CLI:**
```bash
railway variables set CORS_ORIGINS="https://your-app.vercel.app"
railway up
```

### Step 2.7: Update Frontend BETTER_AUTH_URL

**In Vercel dashboard:**
1. Go to Settings → Environment Variables
2. Update `BETTER_AUTH_URL` to: `https://your-app.vercel.app`
3. Redeploy frontend (Deployments → Three dots → Redeploy)

---

## Part 3: Post-Deployment Verification

### Step 3.1: Test Complete User Flow

Open your deployed frontend: `https://your-app.vercel.app`

**Test Checklist:**

1. **Signup**
   - [ ] Navigate to signup page
   - [ ] Create account with email/password
   - [ ] Redirected to dashboard
   - [ ] JWT token stored

2. **Login**
   - [ ] Logout
   - [ ] Login with same credentials
   - [ ] Successfully authenticated

3. **Create Task**
   - [ ] Add new task with title and description
   - [ ] Task appears in list

4. **View Tasks**
   - [ ] All tasks visible
   - [ ] Correct order (newest first)

5. **Update Task**
   - [ ] Edit task title/description
   - [ ] Changes saved

6. **Toggle Complete**
   - [ ] Mark task complete (checkbox)
   - [ ] Strikethrough appears
   - [ ] Uncheck to mark incomplete

7. **Delete Task**
   - [ ] Delete task
   - [ ] Removed from list

8. **Logout**
   - [ ] Click logout
   - [ ] Redirected to login page
   - [ ] Cannot access dashboard without login

9. **Multi-User Isolation**
   - [ ] Create second user account
   - [ ] Verify each user sees only their tasks

### Step 3.2: Check Browser Console

Open DevTools (F12) and check:
- [ ] No console errors
- [ ] No failed network requests
- [ ] JWT token in localStorage/cookies

### Step 3.3: Monitor Backend Logs

**Railway Dashboard:**
- Go to "Observability" tab
- Check logs for errors
- Verify API requests are successful

**Look for:**
- No 500 Internal Server Errors
- Successful database connections
- JWT authentication working

### Step 3.4: Database Verification

Connect to your Neon database:

```bash
psql "postgresql://user:password@host/dbname?sslmode=require"
```

Verify data:
```sql
-- Check users
SELECT id, email, name, created_at FROM users;

-- Check tasks
SELECT id, user_id, title, completed, created_at FROM tasks;

-- Verify indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'tasks';
```

Expected indexes:
- `idx_tasks_user_id`
- `idx_tasks_completed`
- `tasks_pkey`

---

## Part 4: Custom Domain (Optional)

### For Frontend (Vercel)

1. Go to Vercel dashboard → Settings → Domains
2. Add custom domain: `yourdomain.com`
3. Configure DNS with your registrar:
   - Type: `A` or `CNAME`
   - Value: Provided by Vercel
4. Wait for DNS propagation (5-30 minutes)
5. Update `BETTER_AUTH_URL` to custom domain

### For Backend (Railway)

1. Go to Railway dashboard → Settings → Domains
2. Add custom domain: `api.yourdomain.com`
3. Configure DNS:
   - Type: `CNAME`
   - Value: Provided by Railway
4. Update frontend `NEXT_PUBLIC_API_URL` to custom domain

---

## Troubleshooting

### Issue: Frontend shows "Network Error"

**Cause:** Backend CORS not configured correctly

**Solution:**
1. Check `CORS_ORIGINS` in Railway includes frontend URL
2. No trailing slash in URLs
3. Use HTTPS (not HTTP) for production

---

### Issue: Login returns "Invalid token"

**Cause:** `BETTER_AUTH_SECRET` mismatch between frontend and backend

**Solution:**
1. Verify both use **exact same secret**
2. Check for extra spaces or quotes
3. Regenerate secret if needed (update both)

---

### Issue: Backend shows "Database connection failed"

**Cause:** Invalid `DATABASE_URL`

**Solution:**
1. Copy fresh connection string from Neon dashboard
2. Ensure `?sslmode=require` is included
3. Check Neon database is active (not paused)

---

### Issue: Build fails on Railway/Vercel

**Cause:** Missing dependencies or build errors

**Solution:**
1. Test build locally: `npm run build` (frontend) or `pip install -r requirements.txt` (backend)
2. Check build logs in dashboard
3. Ensure `requirements.txt` is up to date (backend)
4. Ensure `package.json` dependencies are correct (frontend)

---

### Issue: "Cannot access other user's tasks" error

**Cause:** This is expected! Multi-user isolation is working correctly.

**Solution:** No action needed. This prevents users from seeing each other's data.

---

## Environment Variables Reference

### Backend (Railway)

| Variable              | Example Value                                      | Required |
|-----------------------|---------------------------------------------------|----------|
| DATABASE_URL          | postgresql://user:pass@host/db?sslmode=require   | ✅       |
| BETTER_AUTH_SECRET    | a1b2c3d4...32-chars-minimum                      | ✅       |
| JWT_ALGORITHM         | HS256                                            | ✅       |
| JWT_EXPIRATION_DAYS   | 7                                                | ✅       |
| CORS_ORIGINS          | https://your-app.vercel.app                      | ✅       |

### Frontend (Vercel)

| Variable              | Example Value                      | Required |
|-----------------------|------------------------------------|----------|
| NEXT_PUBLIC_API_URL   | https://your-backend.railway.app  | ✅       |
| BETTER_AUTH_SECRET    | same-as-backend-secret            | ✅       |
| BETTER_AUTH_URL       | https://your-app.vercel.app       | ✅       |

---

## Deployment Checklist Summary

### Backend Deployment
- [ ] Railway account created
- [ ] Backend project created
- [ ] Environment variables configured
- [ ] Backend deployed successfully
- [ ] Health endpoint returns `{"status":"healthy"}`
- [ ] API docs accessible

### Frontend Deployment
- [ ] Vercel account created
- [ ] Frontend project imported
- [ ] Environment variables configured
- [ ] Frontend deployed successfully
- [ ] Can access signup/login pages
- [ ] CORS configured correctly

### Post-Deployment
- [ ] Complete user flow tested
- [ ] Multi-user isolation verified
- [ ] No console errors
- [ ] Backend logs show no errors
- [ ] Database contains test data
- [ ] All environment variables correct

### Documentation
- [ ] Update README with deployment URLs
- [ ] Document any deployment issues
- [ ] Create demo video (90 seconds)
- [ ] Submit hackathon deliverables

---

## Next Steps

After successful deployment:

1. **Update README.md**
   ```markdown
   ## Live Demo
   - Frontend: https://your-app.vercel.app
   - Backend API: https://your-backend.railway.app
   - API Docs: https://your-backend.railway.app/docs
   ```

2. **Create Demo Video** (90 seconds for hackathon)
   - Show signup/login
   - Create, edit, complete, delete tasks
   - Show multi-user isolation
   - Highlight key features

3. **Monitor Performance**
   - Check Railway/Vercel analytics
   - Monitor error rates
   - Set up alerts (optional)

4. **Prepare for Phase 3**
   - AI Chatbot with OpenAI ChatKit
   - Agents SDK integration
   - MCP tools

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Next.js Deployment**: https://nextjs.org/docs/deployment

---

**Deployment complete!** 🚀 Your todo app is now live in production!
