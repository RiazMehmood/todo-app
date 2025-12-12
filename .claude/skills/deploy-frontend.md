# Deploy Frontend Skill

**Description:** Deploy Next.js frontend to Vercel

## Prerequisites
- Vercel account created
- Vercel CLI installed: `npm install -g vercel`
- Frontend working locally

## Deployment Steps

### 1. First-Time Setup
```bash
cd frontend
vercel login
```

### 2. Deploy to Production
```bash
cd frontend
vercel --prod
```

### 3. Environment Variables
Set in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` - Production backend URL
- `BETTER_AUTH_SECRET` - Same secret as backend
- `BETTER_AUTH_URL` - Production frontend URL

### 4. Verify Deployment
- Check deployment URL
- Test signup/login
- Test task operations
- Verify API connection

## Troubleshooting
- Build errors: Check `npm run build` locally first
- API connection: Verify CORS on backend includes frontend URL
- Auth issues: Verify BETTER_AUTH_SECRET matches backend

## Success Criteria
✅ Frontend accessible at Vercel URL
✅ Can signup and login
✅ Can perform all task operations
✅ No console errors
