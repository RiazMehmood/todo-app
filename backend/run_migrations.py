#!/usr/bin/env python3
"""
Migration runner script - applies SQL migrations to Neon PostgreSQL database
"""
import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

# Migration files in order
MIGRATIONS = [
    "006_add_search_vector.sql",
    "007_add_saved_searches.sql",
    "008_add_task_templates.sql",
    "009_add_time_entries.sql",
    "010_add_analytics_indexes.sql",
]

def run_migration(conn, migration_file: Path):
    """Run a single migration file"""
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_file.name}")
    print(f"{'='*60}")

    try:
        with open(migration_file, 'r') as f:
            sql = f.read()

        with conn.cursor() as cur:
            # Execute migration
            cur.execute(sql)
            conn.commit()
            print(f"✅ SUCCESS: {migration_file.name} applied")

    except Exception as e:
        conn.rollback()
        print(f"❌ ERROR in {migration_file.name}: {e}")
        raise

def main():
    """Run all pending migrations"""
    migrations_dir = Path(__file__).parent / "migrations"

    if not migrations_dir.exists():
        print(f"ERROR: Migrations directory not found at {migrations_dir}")
        sys.exit(1)

    print("\n" + "="*60)
    print("DATABASE MIGRATION RUNNER")
    print("="*60)
    print(f"Database: {DATABASE_URL.split('@')[1].split('/')[0] if '@' in DATABASE_URL else 'unknown'}")
    print(f"Migrations to run: {len(MIGRATIONS)}")
    print("="*60)

    # Connect to database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Run migrations
    try:
        for migration_name in MIGRATIONS:
            migration_file = migrations_dir / migration_name

            if not migration_file.exists():
                print(f"⚠️  WARNING: Migration file not found: {migration_name}")
                continue

            run_migration(conn, migration_file)

        print("\n" + "="*60)
        print("✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()
        print("Database connection closed")

if __name__ == "__main__":
    main()
