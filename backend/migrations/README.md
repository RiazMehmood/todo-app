# Database Migrations

This directory contains SQL migration scripts for the Todo application database.

## Available Migrations

### 001_add_task_indexes.sql
Adds performance indexes to the tasks table:
- `idx_tasks_user_id` - Index on user_id column
- `idx_tasks_completed` - Index on completed column

## Running Migrations

### Option 1: Using psql (PostgreSQL CLI)

```bash
# Connect to your Neon database
psql "postgresql://user:password@host/dbname?sslmode=require"

# Run the migration
\i backend/migrations/001_add_task_indexes.sql

# Verify indexes were created
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'tasks';
```

### Option 2: Using Python Script

```bash
cd backend
python -c "
from src.db import engine
with engine.connect() as conn:
    with open('migrations/001_add_task_indexes.sql', 'r') as f:
        sql = f.read()
    conn.execute(sql)
    conn.commit()
print('✓ Indexes created successfully')
"
```

### Option 3: Automatic on Startup (New Databases)

For new database setups, the indexes will be created automatically when running:

```python
from src.db import create_db_and_tables
create_db_and_tables()  # Called on app startup
```

This is because the SQLModel Task model now has `index=True` on both `user_id` and `completed` fields.

## Verifying Indexes

To check if indexes exist:

```sql
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'tasks'
ORDER BY indexname;
```

Expected output:
```
       indexname        |                           indexdef
-----------------------+--------------------------------------------------------------
 idx_tasks_completed   | CREATE INDEX idx_tasks_completed ON tasks USING btree (completed)
 idx_tasks_user_id     | CREATE INDEX idx_tasks_user_id ON tasks USING btree (user_id)
 tasks_pkey            | CREATE UNIQUE INDEX tasks_pkey ON tasks USING btree (id)
```

## Future Migrations

For production applications, consider using a migration tool like:
- **Alembic** (recommended for SQLModel/SQLAlchemy)
- **Flyway**
- **Liquibase**

See `@.claude/skills/db-migrate.md` for Alembic setup instructions.

## Migration Best Practices

1. **Never modify existing migration files** - Create new ones instead
2. **Test migrations on a copy** of production data first
3. **Use CREATE INDEX IF NOT EXISTS** to make migrations idempotent
4. **Add rollback scripts** for reversible migrations
5. **Document why** each migration is needed (reference task/issue numbers)

## Rollback (if needed)

To remove the indexes created by 001_add_task_indexes.sql:

```sql
DROP INDEX IF EXISTS idx_tasks_user_id;
DROP INDEX IF EXISTS idx_tasks_completed;
```

**Note**: Only drop indexes if you have a specific reason. These indexes improve query performance.
