# Database Migration Agent

**Purpose**: Specialized agent for creating and managing database migrations

**Trigger**: Use when you need to:
- Create new database tables
- Add columns to existing tables
- Create indexes or constraints
- Write migration SQL scripts

## Agent Configuration

```yaml
name: database-migration-agent
description: Create and manage database migrations for PostgreSQL
capabilities:
  - Generate SQL migration scripts
  - Create SQLModel model definitions
  - Add indexes and constraints
  - Handle migration rollbacks
tools:
  - Read (for existing schema)
  - Write (for migration files)
  - Bash (for running migrations)
context_files:
  - backend/src/models.py
  - backend/migrations/*.sql
  - knowledge/patterns/database-pattern.md
```

## How to Use

### Creating a New Table

**Prompt**:
```
Create a database migration to add a new "notifications" table with columns:
- id (serial primary key)
- user_id (uuid, foreign key to users)
- message (text)
- read (boolean, default false)
- created_at (timestamp)

Also create the SQLModel model definition.
```

**Agent Will**:
1. Read existing models.py to understand patterns
2. Generate SQL migration file with CREATE TABLE
3. Add appropriate indexes (user_id, created_at)
4. Create SQLModel class definition
5. Add foreign key constraints
6. Provide rollback SQL

### Adding Columns to Existing Table

**Prompt**:
```
Add AI-related columns to the tasks table:
- created_via_ai (boolean, default false)
- ai_suggested_priority (integer, nullable, check 1-5)
- original_nl_input (text, nullable)
```

**Agent Will**:
1. Generate ALTER TABLE statements
2. Update SQLModel model definition
3. Add check constraints
4. Create index if beneficial
5. Provide rollback ALTER TABLE statements

## Example Output

```sql
-- Migration: 003_add_notifications_table.sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    read BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, read);
```

```python
# backend/src/models.py addition
class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    id: int = Field(primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    message: str
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Best Practices

1. **Naming**: Use sequential numbers (001_, 002_) for migration files
2. **Reversibility**: Always provide rollback SQL
3. **Indexes**: Add indexes for foreign keys and commonly queried fields
4. **Constraints**: Add check constraints for data validation
5. **Testing**: Test migration on local database before production

## Related Patterns

- [Database Pattern](../knowledge/patterns/database-pattern.md)
- [Backend Service Template](../templates/backend/service-template.py)
