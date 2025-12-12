# Todo App Backend

Phase II: Full-Stack Web Application - Backend API

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.13+
- **ORM**: SQLModel
- **Database**: Neon Serverless PostgreSQL
- **Server**: Uvicorn

## Setup

1. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
uv pip install -e .
```

4. Create `.env` from `.env.example`:
```bash
cp .env.example .env
```

5. Update environment variables in `.env`

6. Create database tables (first time only):
```python
python -c "from src.db import create_db_and_tables; create_db_and_tables()"
```

7. Run development server:
```bash
uvicorn src.main:app --reload --port 8000
```

8. Open API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

See `CLAUDE.md` for detailed structure and guidelines.

## Specifications

- See `../specs/api/rest-endpoints.md` for API endpoints
- See `../specs/database/schema.md` for database schema
- See `../specs/features/task-crud.md` for feature requirements

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Migrations (Optional)

Using Alembic:
```bash
alembic init migrations
alembic revision --autogenerate -m "Create tables"
alembic upgrade head
```

## Phase II Features

- RESTful API endpoints
- JWT authentication
- User-scoped data isolation
- PostgreSQL persistence

## Future Phases

- Phase III: MCP server for AI chatbot
- Phase IV: Containerization
- Phase V: Event-driven architecture with Kafka
