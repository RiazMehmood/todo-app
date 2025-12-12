"""
JWT authentication middleware for the Todo application.

This module provides JWT token verification to protect API endpoints.
It extracts the user_id from the JWT token and stores it in request.state
for use in route handlers.
"""

from fastapi import Request, HTTPException
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get JWT secret from environment (must match frontend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not BETTER_AUTH_SECRET:
    raise ValueError("BETTER_AUTH_SECRET environment variable is not set")


async def verify_jwt(request: Request):
    """
    Verify JWT token from Authorization header and extract user info.

    This function should be used as a dependency in protected routes:
        @router.get("/tasks", dependencies=[Depends(verify_jwt)])
        def get_tasks(request: Request):
            user_id = request.state.user_id  # Access authenticated user ID
            ...

    Args:
        request: FastAPI request object

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired

    Side Effects:
        Sets request.state.user_id with the authenticated user's ID
        Sets request.state.user_email with the authenticated user's email (if available)
    """
    # Extract Authorization header
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    # Check Bearer token format
    if not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'"
        )

    # Extract token from "Bearer <token>"
    token = auth_header.split(' ')[1]

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            token,
            BETTER_AUTH_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        # Extract user information from payload
        user_id = payload.get('user_id') or payload.get('sub')  # Support both field names

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        # Store user info in request state for use in route handlers
        request.state.user_id = user_id
        request.state.user_email = payload.get('email')

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )
