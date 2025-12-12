# Setup Environment Skill

**Description:** Set up environment variables for development and production

## Development Environment

### Backend (.env)
```bash
cd backend
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/dbname?sslmode=require

# Authentication Secret (MUST match frontend)
BETTER_AUTH_SECRET=generate-with-python-secrets-token-urlsafe-32

# JWT Configuration
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
EOF
```

### Frontend (.env.local)
```bash
cd frontend
cat > .env.local << 'EOF'
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Authentication Secret (MUST match backend)
BETTER_AUTH_SECRET=same-as-backend-secret

# Frontend URL
BETTER_AUTH_URL=http://localhost:3000
EOF
```

## Production Environment

### Backend (on hosting platform)
```bash
DATABASE_URL=postgresql://...neon-production-url...
BETTER_AUTH_SECRET=production-secret-32-chars-min
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
CORS_ORIGINS=https://your-app.vercel.app
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
BETTER_AUTH_SECRET=same-production-secret
BETTER_AUTH_URL=https://your-app.vercel.app
```

## Generate Secrets

### Python (recommended)
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### OpenSSL
```bash
openssl rand -base64 32
```

### Node.js
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

## Validation Checklist

### Backend .env
- [ ] DATABASE_URL is valid PostgreSQL connection string
- [ ] BETTER_AUTH_SECRET is at least 32 characters
- [ ] CORS_ORIGINS includes frontend URL
- [ ] All required variables present

### Frontend .env.local
- [ ] NEXT_PUBLIC_API_URL points to backend
- [ ] BETTER_AUTH_SECRET matches backend
- [ ] BETTER_AUTH_URL is correct frontend URL
- [ ] All required variables present

## Troubleshooting

### Auth Issues
- Verify BETTER_AUTH_SECRET matches exactly in both files
- Check for trailing spaces or quotes
- Ensure minimum 32 character length

### CORS Errors
- Verify frontend URL in backend CORS_ORIGINS
- Include protocol (http:// or https://)
- No trailing slash

### Database Connection
- Test connection string with psql
- Check SSL mode requirement
- Verify credentials and permissions

## Success Criteria
✅ Backend starts without errors
✅ Frontend compiles without errors
✅ Can connect to database
✅ Authentication works
✅ No CORS errors
