# Railway Database Initialization

## Problem

Your backend is returning **500 Internal Server Error** when trying to signup. This is likely because the database tables don't exist on Railway yet.

## Solution

You need to run the database initialization script on Railway to create all required tables.

## Method 1: Using Railway CLI (Recommended)

### Step 1: Install Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Or on Mac with Homebrew
brew install railway
```

### Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate.

### Step 3: Link to Your Project

```bash
cd /home/riaz/Desktop/todo\ hackathon\ II/todo/backend
railway link
```

Select your project from the list.

### Step 4: Run Database Initialization

```bash
railway run python init_db.py
```

This will:
- Connect to your Neon database
- Create all required tables (users, tasks, user_preferences, conversations, messages)
- Verify tables were created successfully

### Step 5: Verify

```bash
# Check Railway logs
railway logs

# Or test the API
curl -X POST https://todo-app-production-be56.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
```

Should return a success response with JWT token instead of 500 error.

---

## Method 2: Using Neon SQL Editor (Alternative)

If Railway CLI doesn't work, you can create tables directly in Neon:

### Step 1: Go to Neon Console

1. Visit: https://console.neon.tech/
2. Select your project
3. Click **SQL Editor**

### Step 2: Run SQL Script

Copy and paste this SQL:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_via_ai BOOLEAN DEFAULT FALSE,
    ai_suggested_priority INTEGER CHECK (ai_suggested_priority >= 1 AND ai_suggested_priority <= 5),
    original_nl_input TEXT
);

CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS ix_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS ix_tasks_created_via_ai ON tasks(created_via_ai);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ai_enabled BOOLEAN DEFAULT FALSE,
    ai_opt_in_date TIMESTAMP,
    preferred_language VARCHAR(10) DEFAULT 'en',
    privacy_consent_version VARCHAR(10),
    auto_detect_language BOOLEAN DEFAULT TRUE,
    voice_input_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL,
    content VARCHAR(2000) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    language VARCHAR(10),
    related_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    intent_detected VARCHAR(50),
    confidence_score FLOAT CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata VARCHAR
);

CREATE INDEX IF NOT EXISTS ix_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages(conversation_id);
```

### Step 3: Execute

Click **Run** button in SQL Editor.

### Step 4: Verify

Check if tables were created:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see: conversations, messages, tasks, user_preferences, users

---

## Method 3: Update Railway Startup Command

You can also make Railway run the initialization on every deployment:

### Step 1: Create Startup Script

Create `backend/start.sh`:

```bash
#!/bin/bash

echo "Initializing database..."
python init_db.py

echo "Starting application..."
uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

Make it executable:
```bash
chmod +x backend/start.sh
```

### Step 2: Update Railway Start Command

In Railway dashboard:
1. Go to your backend service
2. Click **Settings**
3. Find **Start Command**
4. Change to: `bash start.sh`
5. Click **Save**

### Step 3: Redeploy

Railway will auto-redeploy and run init_db.py before starting the server.

---

## Verification

After running any method above, test that it worked:

### 1. Test Health Endpoint

```bash
curl https://todo-app-production-be56.up.railway.app/health
```

Should return: `{"status":"healthy", ...}`

### 2. Test Signup

```bash
curl -X POST https://todo-app-production-be56.up.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -H "Origin: https://todo-app-ashy-seven-25.vercel.app" \
  -d '{"email":"test@example.com","password":"testpass123","name":"Test User"}'
```

**Before fix:** `Internal Server Error`
**After fix:** `{"user": {...}, "token": "eyJ..."}`

### 3. Test from Frontend

1. Visit: https://todo-app-ashy-seven-25.vercel.app/signup
2. Create account
3. Should successfully signup and redirect to dashboard

---

## Troubleshooting

### Error: "relation 'users' does not exist"

**Solution:** Tables weren't created. Run Method 1 or Method 2 again.

### Error: "permission denied for schema public"

**Solution:** Your Neon database user doesn't have CREATE permissions.
- Go to Neon dashboard
- Check database user permissions
- Make sure you're using the owner role

### Error: "could not connect to server"

**Solution:** DATABASE_URL is incorrect.
- Verify DATABASE_URL in Railway environment variables
- Copy it exactly from Neon dashboard
- Should include `?sslmode=require`

---

## Quick Fix Command

If you have Railway CLI installed:

```bash
cd /home/riaz/Desktop/todo\ hackathon\ II/todo/backend
railway link
railway run python init_db.py
```

That's it! Your database will be initialized and signup will work.
