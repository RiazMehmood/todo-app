# Production Deployment Fix Guide

## Issue: CORS Error on Login

**Root Cause:** Frontend (Vercel) environment variables not configured for production backend (Railway)

## ✅ Railway Backend Configuration (Already Correct)

Your Railway backend at `https://todo-app-production-be56.up.railway.app/` is configured correctly:

- ✅ CORS headers are being sent properly
- ✅ Backend is healthy and accessible
- ✅ Database connection is working

**Verified Environment Variables in Railway:**
```bash
DATABASE_URL=<YOUR_NEON_DATABASE_URL_HERE>
BETTER_AUTH_SECRET=<YOUR_SECRET_KEY_HERE>
CORS_ORIGINS=https://todo-app-ashy-seven-25.vercel.app
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY_HERE>
AI_MODEL=gemini-2.5-flash-lite
CHAT_RATE_LIMIT_PER_USER=20
```

**✅ Confirmed:** CORS is allowing your Vercel frontend!

---

## ❌ Vercel Frontend Configuration (NEEDS UPDATE)

Your Vercel frontend at `https://todo-app-ashy-seven-25.vercel.app/` needs environment variable updates.

### Current Issue:
The frontend `.env.local` file has `NEXT_PUBLIC_API_URL=http://localhost:8000`, but this is only for local development. **Vercel production deployment needs different values.**

### Fix: Update Vercel Environment Variables

1. **Go to Vercel Dashboard:**
   - Navigate to: https://vercel.com/dashboard
   - Select your project: `todo-app-ashy-seven-25`
   - Go to: **Settings** → **Environment Variables**

2. **Add/Update These Variables:**

   | Variable Name | Value | Environment |
   |---------------|-------|-------------|
   | `NEXT_PUBLIC_API_URL` | `https://todo-app-production-be56.up.railway.app` | Production, Preview, Development |
   | `BETTER_AUTH_SECRET` | `<YOUR_SECRET_KEY_HERE>` | Production, Preview, Development |
   | `BETTER_AUTH_URL` | `https://todo-app-ashy-seven-25.vercel.app` | Production |
   | `NEXT_PUBLIC_AI_ENABLED` | `true` | Production, Preview, Development |

   **IMPORTANT:** Remove trailing slashes from URLs!
   - ✅ Correct: `https://todo-app-production-be56.up.railway.app`
   - ❌ Wrong: `https://todo-app-production-be56.up.railway.app/`

3. **Redeploy Frontend:**
   After updating environment variables, you MUST redeploy:

   **Option 1: Via Vercel Dashboard**
   - Go to **Deployments** tab
   - Click **...** (three dots) on latest deployment
   - Click **Redeploy**
   - Select **Use existing Build Cache: NO** (to force fresh build with new env vars)

   **Option 2: Via Git Push**
   ```bash
   # Make a small commit to trigger redeploy
   git commit --allow-empty -m "chore: trigger redeploy with updated env vars"
   git push origin 002-todo-web-app
   ```

---

## 🔧 Railway Backend - Additional Verification

While CORS is working, let's verify all required environment variables are set:

1. **Go to Railway Dashboard:**
   - Navigate to: https://railway.app/dashboard
   - Select your project
   - Go to: **Variables** tab

2. **Verify These Variables Exist:**

   ```bash
   # Database
   DATABASE_URL=<YOUR_NEON_DATABASE_URL_HERE>

   # Authentication
   BETTER_AUTH_SECRET=<YOUR_SECRET_KEY_HERE>
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_DAYS=7

   # CORS - MUST include Vercel frontend URL
   CORS_ORIGINS=https://todo-app-ashy-seven-25.vercel.app

   # AI Configuration (Phase III)
   GEMINI_API_KEY=<YOUR_GEMINI_API_KEY_HERE>
   AI_MODEL=gemini-2.5-flash-lite
   CHAT_RATE_LIMIT_PER_USER=20
   ```

   **NOTE:** If you need to support multiple frontend URLs (e.g., preview deployments), use comma-separated values:
   ```bash
   CORS_ORIGINS=https://todo-app-ashy-seven-25.vercel.app,https://todo-app-ashy-seven-25-preview.vercel.app
   ```

3. **If you updated any Railway variables, redeploy:**
   - Railway should auto-redeploy on variable changes
   - If not, click **Deploy** → **Redeploy**

---

## 🧪 Testing After Fix

Once you've updated Vercel environment variables and redeployed:

### 1. Test Backend Health
```bash
curl https://todo-app-production-be56.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "todo-api",
  "version": "3.0.0-dev",
  "phase": "III",
  "ai_enabled": true
}
```

### 2. Test CORS from Frontend
Open browser console on `https://todo-app-ashy-seven-25.vercel.app/login` and run:

```javascript
// This should NOT give CORS error anymore
fetch('https://todo-app-production-be56.up.railway.app/health')
  .then(r => r.json())
  .then(data => console.log('✅ Backend accessible:', data))
  .catch(err => console.error('❌ CORS error:', err));
```

### 3. Test Signup Flow
1. Go to: https://todo-app-ashy-seven-25.vercel.app/signup
2. Create a new account:
   - Name: Test User
   - Email: test@example.com
   - Password: testpass123
3. Verify you're redirected to dashboard
4. Check browser console for any CORS errors

### 4. Test Login Flow
1. Go to: https://todo-app-ashy-seven-25.vercel.app/login
2. Login with created account
3. Verify successful login and redirect

### 5. Test Task Creation
1. On dashboard, add a task: "Test task from production"
2. Verify it appears in the list
3. Check database to confirm:
   ```bash
   # Connect to Neon database (use your connection string)
   psql "postgresql://neondb_owner:<YOUR_DB_PASSWORD>@ep-frosty-dawn-ado879ad-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

   # Query tasks
   SELECT id, title, user_id, created_via_ai FROM tasks ORDER BY created_at DESC LIMIT 5;
   ```

### 6. Test AI Chat (Phase III)
1. Go to Settings
2. Enable AI Chat Assistant
3. Accept privacy notice
4. Go to Dashboard
5. Type in chat: "Add task to buy milk"
6. Verify task is created

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error After Redeployment
**Symptom:** Still getting CORS error after updating Vercel env vars

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+F5)
3. Verify Vercel deployment used new env vars:
   - Go to Vercel Dashboard → Deployments
   - Click on latest deployment
   - Scroll down to **Environment Variables**
   - Verify `NEXT_PUBLIC_API_URL` shows Railway URL

### Issue 2: "Cannot connect to backend"
**Symptom:** Frontend shows "Network error" or "Failed to fetch"

**Solution:**
1. Verify Railway backend is running:
   ```bash
   curl https://todo-app-production-be56.up.railway.app/health
   ```
2. Check Railway logs for errors:
   - Go to Railway Dashboard → Deployments → View Logs
3. Restart Railway deployment if needed

### Issue 3: "Invalid token" or "Unauthorized"
**Symptom:** Login seems to work but then shows 401 error

**Solution:**
1. Verify `BETTER_AUTH_SECRET` matches on both Railway and Vercel
2. Clear browser localStorage:
   ```javascript
   // In browser console
   localStorage.clear();
   location.reload();
   ```
3. Try creating a new account instead of using old one

### Issue 4: Database Connection Error
**Symptom:** "Database connection failed" in Railway logs

**Solution:**
1. Verify DATABASE_URL is correct in Railway
2. Check Neon database is active:
   - Go to: https://console.neon.tech/
   - Verify project is running
3. Test connection from Railway:
   ```bash
   # In Railway shell
   railway run python -c "from src.db import engine; engine.connect()"
   ```

### Issue 5: AI Chat Not Working
**Symptom:** Chat interface shows "AI disabled" or doesn't appear

**Solution:**
1. Verify `GEMINI_API_KEY` is set in Railway
2. Check Railway logs for AI errors
3. Verify user has opted in to AI features in settings
4. Test Gemini API key:
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key=<YOUR_GEMINI_API_KEY_HERE>" \
     -H 'Content-Type: application/json' \
     -d '{"contents":[{"parts":[{"text":"Hello"}]}]}'
   ```

---

## 📋 Quick Checklist

Before declaring "FIXED":

- [ ] Vercel environment variables updated with Railway backend URL
- [ ] Vercel redeployed (not just saved env vars)
- [ ] Railway environment variables include Vercel frontend URL in CORS_ORIGINS
- [ ] Backend health check returns 200 OK
- [ ] Can access https://todo-app-ashy-seven-25.vercel.app/login without CORS error
- [ ] Can create new account via signup
- [ ] Can login with created account
- [ ] Can create tasks from dashboard
- [ ] Can enable AI chat in settings
- [ ] Can create tasks via AI chat
- [ ] Browser console shows no CORS errors

---

## 🎯 Next Steps After Fix

Once everything is working:

1. **Document Production URLs:**
   - Update README.md with production URLs
   - Add to project documentation

2. **Monitor Logs:**
   - Railway: Check for any errors
   - Vercel: Check for failed requests
   - Neon: Monitor database connections

3. **Test Phase III Features:**
   - AI chat task creation (English)
   - AI chat task queries
   - AI chat task updates/deletes
   - Urdu language support (if implemented)

4. **Optional: Voice Input (Bonus Feature):**
   - Continue with T063-T070 if you want +200 hackathon points

---

## 🆘 Still Not Working?

If you've followed all steps and still have issues:

1. **Check browser console** for exact error message
2. **Check Railway logs** for backend errors
3. **Check Vercel deployment logs** for build errors
4. **Verify all URLs** have no typos or trailing slashes
5. **Test with a different browser** (to rule out cache issues)

Share the exact error message and I can help debug further!
