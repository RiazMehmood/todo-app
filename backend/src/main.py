"""
Main FastAPI application entry point for the Todo API.

This module configures:
- FastAPI app with metadata
- CORS middleware for frontend access
- Database initialization on startup
- API route registration
- Health check endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .db import create_db_and_tables
from .routes import auth, tasks, chat

# Import Phase III models for database registration
from .models import (
    User, Task, UserPreferences, Conversation, Message
)

# Load environment variables
load_dotenv()

# Get CORS origins from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo task management with JWT authentication and AI chatbot integration",
    version="3.0.0-dev",  # Phase III: AI Chatbot Integration
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Frontend URLs
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers to frontend
)


@app.on_event("startup")
def on_startup():
    """
    Run initialization tasks when the application starts.

    - Creates database tables if they don't exist
    - Logs startup information
    """
    print("=" * 50)
    print("🚀 Starting Todo API Server (Phase III)")
    print("=" * 50)
    print(f"📦 Version: 3.0.0-dev")
    print(f"🤖 AI Chatbot: Enabled")
    print(f"🌐 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)

    # Create database tables (includes Phase III tables)
    create_db_and_tables()

    print("✅ Server ready! AI chatbot integration active.")
    print("=" * 50)


# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint with API information.

    Returns:
        API welcome message and version
    """
    return {
        "message": "Todo API - Phase III: AI Chatbot Integration",
        "version": "3.0.0-dev",
        "docs": "/docs",
        "health": "/health",
        "features": ["tasks", "authentication", "ai-chatbot"]
    }


# Health check endpoint
@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": "todo-api",
        "version": "3.0.0-dev",
        "phase": "III",
        "ai_enabled": os.getenv("OPENAI_API_KEY") is not None
    }


# Register API routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(chat.router, prefix="/api", tags=["chat"])


# Error handlers (optional)
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 Not Found errors."""
    return {
        "detail": "Endpoint not found. Visit /docs for API documentation."
    }


if __name__ == "__main__":
    # This allows running the app directly with: python -m src.main
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )
