"""
Database initialization script for Railway deployment.

Run this once to create all required tables in the Neon PostgreSQL database.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🗄️  Database Initialization Script")
print("=" * 70)
print()

# Check required environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("   Please set DATABASE_URL in your .env file or Railway environment variables.")
    exit(1)

print(f"📍 Database URL: {DATABASE_URL[:50]}...")
print()

# Import database and models
try:
    from src.db import engine, create_db_and_tables
    from src.models import User, Task, UserPreferences, Conversation, Message
except ImportError as e:
    print(f"❌ ERROR: Failed to import modules: {e}")
    print("   Make sure you're running this from the backend/ directory.")
    print("   Install dependencies: uv pip install -r requirements.txt")
    exit(1)

print("✅ Successfully imported database and models")
print()

# List all models that will be created
models = [User, Task, UserPreferences, Conversation, Message]
print("📋 Tables to create:")
for model in models:
    print(f"   - {model.__tablename__}")
print()

# Create tables
print("🔨 Creating tables...")
try:
    create_db_and_tables()
    print("✅ All tables created successfully!")
    print()
except Exception as e:
    print(f"❌ ERROR: Failed to create tables: {e}")
    print()
    print("💡 Troubleshooting:")
    print("   1. Check that DATABASE_URL is correct")
    print("   2. Verify Neon database is accessible")
    print("   3. Check if tables already exist")
    print()
    exit(1)

# Verify tables were created
print("🔍 Verifying tables...")
try:
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print(f"✅ Found {len(tables)} tables in database:")
    for table in sorted(tables):
        print(f"   - {table}")
    print()

    # Check if all required tables exist
    required_tables = {"users", "tasks", "user_preferences", "conversations", "messages"}
    existing_tables = set(tables)
    missing_tables = required_tables - existing_tables

    if missing_tables:
        print(f"⚠️  WARNING: Missing tables: {missing_tables}")
    else:
        print("✅ All required tables exist!")

    print()
except Exception as e:
    print(f"⚠️  WARNING: Could not verify tables: {e}")
    print()

print("=" * 70)
print("✨ Database initialization complete!")
print("=" * 70)
print()
print("🎯 Next steps:")
print("   1. Test the API: curl https://your-railway-url.up.railway.app/health")
print("   2. Try creating a user via signup endpoint")
print("   3. Check Railway logs if you encounter errors")
print()
