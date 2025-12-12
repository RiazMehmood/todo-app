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
from .routes import auth, tasks

# Load environment variables
load_dotenv()

# Get CORS origins from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="RESTful API for multi-user todo task management with JWT authentication",
    version="2.0.0",
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
    print("🚀 Starting Todo API Server")
    print("=" * 50)
    print(f"📦 Version: 2.0.0")
    print(f"🌐 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)

    # Create database tables
    create_db_and_tables()

    print("✅ Server ready!")
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
        "message": "Todo API - Phase II",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
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
        "version": "2.0.0"
    }


# Register API routers
app.include_router(auth.router)
app.include_router(tasks.router)


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
