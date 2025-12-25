"""
Configuration module for Todo Backend API

Loads environment variables and provides configuration constants
for database, Redis, WebSocket, and other services.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Authentication Configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is required")

# Redis Configuration (for WebSocket pub/sub and presence tracking)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = int(os.getenv("WS_HEARTBEAT_INTERVAL", "10"))  # seconds
WS_PRESENCE_TIMEOUT = int(os.getenv("WS_PRESENCE_TIMEOUT", "30"))  # seconds
WS_MAX_CONNECTIONS = int(os.getenv("WS_MAX_CONNECTIONS", "1000"))

# Search Configuration
POSTGRES_SEARCH_LIMIT = int(os.getenv("POSTGRES_SEARCH_LIMIT", "1000"))
ENABLE_SEARCH_SUGGESTIONS = os.getenv("ENABLE_SEARCH_SUGGESTIONS", "true").lower() == "true"

# Bulk Operations Configuration
BULK_OPERATION_LIMIT = int(os.getenv("BULK_OPERATION_LIMIT", "500"))  # max tasks per operation
BULK_OPERATION_TIMEOUT = int(os.getenv("BULK_OPERATION_TIMEOUT", "30"))  # seconds

# Analytics Configuration
ANALYTICS_CACHE_TTL = int(os.getenv("ANALYTICS_CACHE_TTL", "300"))  # 5 minutes cache
MAX_EXPORT_SIZE = int(os.getenv("MAX_EXPORT_SIZE", "10000"))  # max tasks in CSV export
ENABLE_PDF_EXPORT = os.getenv("ENABLE_PDF_EXPORT", "true").lower() == "true"

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Application Settings
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV == "development"
