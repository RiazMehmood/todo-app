# Deploy Backend Skill

**Description:** Deploy FastAPI backend to Railway/Render/Fly.io

## Prerequisites
- Account on hosting platform (Railway/Render/Fly.io)
- Backend working locally
- Database connection string (Neon PostgreSQL)

## Deployment Steps (Railway)

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

### 2. Initialize Project
```bash
cd backend
railway init
```

### 3. Add Environment Variables
```bash
railway variables set DATABASE_URL="postgresql://..."
railway variables set BETTER_AUTH_SECRET="your-secret"
railway variables set JWT_ALGORITHM="HS256"
railway variables set JWT_EXPIRATION_DAYS="7"
railway variables set CORS_ORIGINS="https://your-frontend.vercel.app"
```

### 4. Deploy
```bash
railway up
```

### 5. Get Deployment URL
```bash
railway domain
```

## Alternative: Render.com

### 1. Create Web Service
- Connect GitHub repo
- Select `backend` directory
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### 2. Add Environment Variables
Add in Render dashboard

### 3. Deploy
Auto-deploys on git push

## Success Criteria
✅ Backend accessible at deployment URL
✅ /health endpoint returns healthy
✅ /docs shows API documentation
✅ Frontend can connect and authenticate
