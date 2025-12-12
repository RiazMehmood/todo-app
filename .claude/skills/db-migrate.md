# Database Migration Skill

**Description:** Run database migrations with Alembic

## Setup Alembic (First Time)

### 1. Install Alembic
```bash
cd backend
source .venv/bin/activate
pip install alembic
```

### 2. Initialize Alembic
```bash
alembic init migrations
```

### 3. Configure Alembic
Edit `migrations/env.py`:

```python
from src.models import SQLModel
from src.db import DATABASE_URL

config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = SQLModel.metadata
```

## Create Migration

### Auto-generate from models
```bash
alembic revision --autogenerate -m "Add new column to tasks"
```

### Manual migration
```bash
alembic revision -m "Add indexes"
```

Edit generated file in `migrations/versions/`

## Run Migrations

### Upgrade to latest
```bash
alembic upgrade head
```

### Upgrade by 1 version
```bash
alembic upgrade +1
```

### Downgrade by 1 version
```bash
alembic downgrade -1
```

### Show current version
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

## Common Migrations

### Add Index
```python
def upgrade():
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_completed', 'tasks', ['completed'])

def downgrade():
    op.drop_index('idx_tasks_user_id', 'tasks')
    op.drop_index('idx_tasks_completed', 'tasks')
```

### Add Column
```python
def upgrade():
    op.add_column('tasks', sa.Column('priority', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('tasks', 'priority')
```

## Success Criteria
✅ Migration runs without errors
✅ Database schema updated correctly
✅ Can rollback if needed
✅ Application works with new schema
