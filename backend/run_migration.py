#!/usr/bin/env python3
"""
Standalone migration script to run 003_add_chat_tables.sql
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("✗ DATABASE_URL environment variable is not set")
    sys.exit(1)

try:
    # Read the migration file
    migration_file = "migrations/003_add_chat_tables.sql"
    with open(migration_file, 'r') as f:
        sql = f.read()

    # Connect to database using psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Execute the migration
    cursor.execute(sql)
    conn.commit()

    print(f'✓ Migration {migration_file} executed successfully')
    print('✓ Created: user_preferences, conversations, messages tables')
    print('✓ Enhanced tasks table with AI metadata columns')
    print('✓ Created all performance indexes')

    cursor.close()
    conn.close()

except FileNotFoundError:
    print(f"✗ Migration file not found: {migration_file}")
    sys.exit(1)
except psycopg2.Error as e:
    print(f'✗ Database error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'✗ Migration failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
