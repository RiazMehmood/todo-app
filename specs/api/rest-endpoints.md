# REST API Endpoints

## Overview

The Todo API provides RESTful endpoints for managing tasks. All endpoints require JWT authentication and enforce user-level data isolation.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com` (or Vercel serverless function URL)

## Authentication

All endpoints (except auth endpoints) require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

**Error Responses:**
- `401 Unauthorized` - Missing, invalid, or expired token
- `403 Forbidden` - Token valid but user trying to access another user's resources

## Common Response Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE (optional) |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side error |

## Endpoints

### 1. List All Tasks

**GET** `/api/{user_id}/tasks`

Retrieve all tasks belonging to the authenticated user.

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID

**Query Parameters:**
- `status` (string, optional) - Filter by status: `"all"`, `"pending"`, `"completed"` (default: `"all"`)
- `sort` (string, optional) - Sort order: `"created"`, `"title"`, `"updated"` (default: `"created"`)

**Request Example:**
```bash
GET /api/user123/tasks?status=pending
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2025-12-09T10:30:00Z",
    "updated_at": "2025-12-09T10:30:00Z"
  },
  {
    "id": 2,
    "user_id": "user123",
    "title": "Call dentist",
    "description": null,
    "completed": true,
    "created_at": "2025-12-08T14:20:00Z",
    "updated_at": "2025-12-09T09:15:00Z"
  }
]
```

**Error Responses:**
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user

---

### 2. Get Single Task

**GET** `/api/{user_id}/tasks/{id}`

Retrieve details of a specific task.

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID
- `id` (integer, required) - Task ID

**Request Example:**
```bash
GET /api/user123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T10:30:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user
- `404 Not Found` - Task doesn't exist or doesn't belong to user

---

### 3. Create Task

**POST** `/api/{user_id}/tasks`

Create a new task for the authenticated user.

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID

**Request Body:**
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Field Validation:**
- `title` (string, required) - 1-200 characters
- `description` (string, optional) - Max 1000 characters

**Request Example:**
```bash
POST /api/user123/tasks
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T11:00:00Z",
  "updated_at": "2025-12-09T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error (empty title, title too long, etc.)
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user

**Validation Error Example (400):**
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

---

### 4. Update Task

**PUT** `/api/{user_id}/tasks/{id}`

Update an existing task's title and/or description.

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID
- `id` (integer, required) - Task ID

**Request Body:**
```json
{
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread, apples, bananas"
}
```

**Field Validation:**
- `title` (string, optional) - 1-200 characters (if provided)
- `description` (string, optional) - Max 1000 characters (if provided)

**Note**: Can update just `title`, just `description`, or both.

**Request Example:**
```bash
PUT /api/user123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Buy groceries and fruits"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries and fruits",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T11:15:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user
- `404 Not Found` - Task doesn't exist or doesn't belong to user

---

### 5. Delete Task

**DELETE** `/api/{user_id}/tasks/{id}`

Permanently delete a task.

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID
- `id` (integer, required) - Task ID

**Request Example:**
```bash
DELETE /api/user123/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK or 204 No Content):**
```json
{
  "message": "Task deleted successfully",
  "id": 1
}
```

Or simply `204 No Content` with empty body.

**Error Responses:**
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user
- `404 Not Found` - Task doesn't exist or doesn't belong to user

---

### 6. Toggle Task Completion

**PATCH** `/api/{user_id}/tasks/{id}/complete`

Toggle a task's completion status (true ↔ false).

**Path Parameters:**
- `user_id` (string, required) - Must match authenticated user's ID
- `id` (integer, required) - Task ID

**Request Body:** None (or optionally `{ "completed": true/false }`)

**Request Example:**
```bash
PATCH /api/user123/tasks/1/complete
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2025-12-09T10:30:00Z",
  "updated_at": "2025-12-09T11:20:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid/missing token
- `403 Forbidden` - `user_id` doesn't match authenticated user
- `404 Not Found` - Task doesn't exist or doesn't belong to user

---

## Authentication Endpoints (Optional)

Better Auth typically handles these, but if custom endpoints are needed:

### 7. User Signup

**POST** `/api/auth/signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2025-12-09T11:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `400 Bad Request` - Validation error (weak password, invalid email)
- `409 Conflict` - Email already registered

---

### 8. User Login

**POST** `/api/auth/login`

Authenticate existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

## Security

### Authorization Flow

1. User logs in → Receives JWT token
2. Frontend stores token (cookie or localStorage)
3. Frontend includes token in all API requests:
   ```
   Authorization: Bearer <token>
   ```
4. Backend middleware:
   - Extracts token from header
   - Verifies signature with `BETTER_AUTH_SECRET`
   - Decodes token to get `user_id`
   - Verifies `user_id` in URL matches token
   - Allows request to proceed or returns 401/403

### Data Isolation

All endpoints enforce user-level isolation:

```python
# Example backend code
tasks = session.query(Task).filter(
    Task.user_id == authenticated_user_id
).all()
```

A user can **never** see or modify another user's tasks.

## Rate Limiting (Future)

Not implemented in Phase II, but recommended for production:
- Limit requests per user/IP
- Example: 100 requests per minute per user

## CORS

Backend must allow requests from frontend domain:
```python
# FastAPI CORS configuration
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## OpenAPI Documentation

FastAPI automatically generates OpenAPI docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Future Enhancements (Not in Phase II)

- Pagination for task list (`?limit=20&offset=0`)
- Filtering by multiple criteria
- Bulk operations (delete multiple tasks)
- Task search endpoint
- Task statistics endpoint

## Testing

Use tools like:
- **curl** for command-line testing
- **Postman** for API exploration
- **httpx** for Python testing
- **Playwright** or **Cypress** for E2E testing

**Example curl command:**
```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"This is a test"}'
```
