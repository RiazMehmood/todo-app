# Deployment URLs - Todo App

**Date**: 2025-12-25
**Phase**: V - Cloud-Native Deployment
**Status**: Backend Live, Frontend Deploying

---

## 🌐 Application URLs

### Backend API (Live ✅)
- **Production URL**: http://104.248.108.206
- **Health Check**: http://104.248.108.206/health
- **API Documentation**: http://104.248.108.206/docs
- **Platform**: DigitalOcean Kubernetes (DOKS)
- **Service**: LoadBalancer
- **Status**: ✅ Operational

**Test Commands:**
```bash
# Health check
curl http://104.248.108.206/health

# API info
curl http://104.248.108.206/

# Swagger UI (browser)
open http://104.248.108.206/docs
```

### Frontend (Deploying 🔄)
- **Production URL**: `<YOUR_VERCEL_URL_HERE>`
- **Expected Format**: `https://todo-frontend-<hash>.vercel.app`
- **Platform**: Vercel
- **Framework**: Next.js 16
- **Status**: ⏳ Pending Deployment

**After Deployment, Update:**
1. Copy your Vercel URL from deployment output
2. Paste it here: `____________________________________`
3. Update `BETTER_AUTH_URL` in Vercel environment variables
4. Redeploy frontend

---

## 🚀 How to Deploy Frontend

### Method 1: Vercel CLI (Terminal)

```bash
# 1. Login to Vercel (opens browser)
vercel login

# 2. Deploy frontend
cd /home/riaz/Desktop/todo\ hackathon\ II/todo/frontend
vercel --prod

# 3. Follow prompts and copy the deployment URL
```

### Method 2: Vercel Web Dashboard (Recommended)

**Step 1: Import GitHub Repository**
1. Go to: https://vercel.com/new
2. Click "Import Git Repository"
3. Connect GitHub account if needed
4. Select: `RiazMehmood/todo-app`
5. Branch: `005-cloud-native-deployment`

**Step 2: Configure Project**
- Framework Preset: **Next.js**
- Root Directory: **`frontend/`** ⚠️ (Important!)
- Build Command: `npm run build`
- Output Directory: `.next`

**Step 3: Set Environment Variables**
Add these in Vercel dashboard:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `http://104.248.108.206` |
| `BETTER_AUTH_SECRET` | `Pph1JttVAbghDQY0481WP-IcNdokMj0RDpF6l6MroEg` |
| `BETTER_AUTH_URL` | (Leave blank initially) |

**Step 4: Deploy**
- Click "Deploy"
- Wait ~3-5 minutes for build
- Copy deployment URL (e.g., `https://todo-frontend-xyz.vercel.app`)

**Step 5: Update BETTER_AUTH_URL**
- Go to: Project Settings → Environment Variables
- Edit `BETTER_AUTH_URL`
- Set to your Vercel URL (from Step 4)
- Click "Save"
- Go to Deployments → Click "Redeploy"

---

## 📝 Deployment Checklist

### Backend ✅
- [x] Deployed to Kubernetes
- [x] LoadBalancer configured
- [x] External IP assigned
- [x] Health check passing
- [x] API docs available
- [x] Database migrations applied

### Frontend 🔄
- [ ] Deployed to Vercel
- [ ] Frontend URL obtained
- [ ] `BETTER_AUTH_URL` updated
- [ ] Frontend redeployed
- [ ] Can access via browser
- [ ] Authentication working
- [ ] Can create/view tasks

---

## 🧪 Testing After Deployment

### 1. Test Backend API
```bash
# Should return: {"status": "healthy", ...}
curl http://104.248.108.206/health
```

### 2. Test Frontend
```bash
# Open frontend in browser
open <YOUR_VERCEL_URL>

# Should see:
# - Login/Signup page
# - After login: Dashboard with tasks
```

### 3. Test Full Flow
1. **Open Frontend**: Navigate to your Vercel URL
2. **Sign Up**: Create a new account
3. **Login**: Login with credentials
4. **Create Task**: Add a new task
5. **View Tasks**: See tasks in dashboard
6. **Toggle Task**: Mark task as complete
7. **Check Backend**: Verify data in backend
   ```bash
   # Get tasks for user (requires JWT token)
   curl -H "Authorization: Bearer <token>" \
     http://104.248.108.206/api/<user_id>/tasks
   ```

---

## 🔐 Environment Variables

### Backend (Kubernetes Secrets)
```yaml
db-secrets:
  connection-string: <Neon PostgreSQL URL>

api-secrets:
  better-auth-secret: Pph1JttVAbghDQY0481WP-IcNdokMj0RDpF6l6MroEg
  openai-api-key: <OpenAI API Key>
```

### Frontend (Vercel Environment)
```
NEXT_PUBLIC_API_URL=http://104.248.108.206
BETTER_AUTH_SECRET=Pph1JttVAbghDQY0481WP-IcNdokMj0RDpF6l6MroEg
BETTER_AUTH_URL=<Your Vercel URL>
```

⚠️ **Important**: `BETTER_AUTH_SECRET` must match between frontend and backend!

---

## 🎯 Final URLs (Fill After Deployment)

Once frontend is deployed, fill this in:

```
Frontend URL: _______________________________________________
Backend URL:  http://104.248.108.206
GitHub Repo:  https://github.com/RiazMehmood/todo-app
Branch:       005-cloud-native-deployment
```

---

## 📞 Share These URLs

**For Hackathon Submission:**
- **Frontend**: `<YOUR_VERCEL_URL>`
- **Backend API**: http://104.248.108.206
- **API Docs**: http://104.248.108.206/docs
- **GitHub**: https://github.com/RiazMehmood/todo-app/tree/005-cloud-native-deployment

**Demo Credentials** (create after deployment):
- Email: `demo@example.com`
- Password: `Demo123!`

---

## 🚨 Troubleshooting

### Frontend Build Fails
- **Check**: Root directory is set to `frontend/` in Vercel
- **Verify**: All environment variables are set
- **Logs**: Check build logs in Vercel dashboard

### CORS Errors
- **Backend**: Check CORS configuration in `backend/src/main.py`
- **Add Frontend URL** to allowed origins:
  ```python
  allow_origins=["http://104.248.108.206", "<YOUR_VERCEL_URL>"]
  ```

### Authentication Not Working
- **Verify**: `BETTER_AUTH_SECRET` matches in both frontend and backend
- **Check**: `BETTER_AUTH_URL` is set to your Vercel URL
- **Redeploy**: Frontend after updating environment variables

---

**Created**: 2025-12-25 22:50 UTC
**Last Updated**: Pending frontend deployment
**Next Step**: Deploy frontend to Vercel and update URLs above
