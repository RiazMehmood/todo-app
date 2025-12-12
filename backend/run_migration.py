#!/usr/bin/env python3
"""
Database migration runner for Todo application.

Usage:
    python run_migration.py 001_add_task_indexes.sql
    python run_migration.py all  # Run all migrations
"""

import sys
import os
from pathlib import Path
from sqlalchemy import text

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.db import engine


def run_migration(migration_file: str):
    """Run a single migration file."""
    migration_path = Path(__file__).parent / "migrations" / migration_file

    if not migration_path.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False

    print(f"Running migration: {migration_file}")

    try:
        with open(migration_path, 'r') as f:
            sql = f.read()

        with engine.connect() as conn:
            # Execute the SQL migration
            conn.execute(text(sql))
            conn.commit()

        print(f"✓ Migration completed: {migration_file}")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {migration_file}")
        print(f"Error: {e}")
        return False


def run_all_migrations():
    """Run all migration files in order."""
    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted([
        f.name for f in migrations_dir.glob("*.sql")
    ])

    if not migration_files:
        print("No migration files found in migrations/")
        return

    print(f"Found {len(migration_files)} migration(s)")
    print("-" * 50)

    success_count = 0
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
        print("-" * 50)

    print(f"\n✓ Completed {success_count}/{len(migration_files)} migrations")


def verify_indexes():
    """Verify that the indexes were created."""
    print("\nVerifying indexes on tasks table...")

    query = text("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'tasks'
        ORDER BY indexname;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        indexes = result.fetchall()

    if indexes:
        print("\nIndexes found:")
        for idx in indexes:
            print(f"  - {idx[0]}")
        print()
    else:
        print("  No indexes found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_migration.py <migration_file.sql>")
        print("  python run_migration.py all")
        print("\nExample:")
        print("  python run_migration.py 001_add_task_indexes.sql")
        sys.exit(1)

    migration_arg = sys.argv[1]

    if migration_arg == "all":
        run_all_migrations()
    else:
        run_migration(migration_arg)

    # Verify indexes after migration
    verify_indexes()
