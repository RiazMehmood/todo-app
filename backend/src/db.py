"""
Database connection and session management for the Todo application.

This module handles:
- Database engine creation with connection pooling
- Session management for database operations
- Table creation (for development)
"""

from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to log SQL queries (useful for debugging)
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10,  # Max connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use (handles stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def create_db_and_tables():
    """
    Create all database tables defined in SQLModel models.

    This function should be called on application startup during development.
    For production, use Alembic migrations instead.
    """
    SQLModel.metadata.create_all(engine)
    print("✓ Database tables created successfully")


def get_session():
    """
    Dependency function for FastAPI route injection.

    Usage in routes:
        @app.get("/api/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            # Use session here
            pass

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session
