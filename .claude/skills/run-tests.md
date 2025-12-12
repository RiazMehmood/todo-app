# Run Tests Skill

**Description:** Execute all tests (E2E, unit, integration)

## Backend Tests (pytest)

### Setup
```bash
cd backend
source .venv/bin/activate
pip install pytest httpx
```

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src

# Specific test file
pytest tests/test_auth.py

# Verbose output
pytest -v
```

## Frontend Tests (Playwright)

### Setup
```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

### Run E2E Tests
```bash
# All tests
npx playwright test

# Headed mode (see browser)
npx playwright test --headed

# Specific test
npx playwright test tests/auth.spec.ts

# Generate report
npx playwright show-report
```

## Manual Test Checklist

### Authentication
- [ ] Signup with valid data
- [ ] Signup with duplicate email (should fail)
- [ ] Login with correct credentials
- [ ] Login with incorrect credentials (should fail)
- [ ] Access dashboard when authenticated
- [ ] Redirect to login when not authenticated

### Task Operations
- [ ] Create task with title only
- [ ] Create task with title and description
- [ ] View all tasks
- [ ] Mark task complete
- [ ] Mark task incomplete
- [ ] Edit task title
- [ ] Edit task description
- [ ] Delete task
- [ ] Filter tasks (all/pending/completed)

### Multi-User Isolation
- [ ] Create second user
- [ ] Verify User A only sees User A's tasks
- [ ] Verify User B only sees User B's tasks

## Success Criteria
✅ All automated tests pass
✅ All manual test checklist items work
✅ No console errors
✅ Data isolation verified
