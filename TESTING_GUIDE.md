# Manual Testing Guide - Phase 2 Todo Application

**Status**: Ready for Testing ✅
**Backend**: http://localhost:8000
**Frontend**: http://localhost:3000
**API Docs**: http://localhost:8000/docs

---

## Pre-Testing Checklist

- [x] Backend server running on port 8000
- [x] Frontend server running on port 3000
- [x] Database connection established
- [x] Database indexes created
- [ ] Browser DevTools open (F12) to monitor network/console

---

## Test Suite 1: Authentication (User Story 1 & 2)

### Test 1.1: User Signup (New Account)

**Steps:**
1. Open http://localhost:3000 in your browser
2. Navigate to `/signup` (or click "Sign Up" link)
3. Fill in the signup form:
   - Name: `Test User`
   - Email: `testuser@example.com`
   - Password: `password123` (min 8 chars)
   - Confirm Password: `password123`
4. Click "Sign Up" button

**Expected Results:**
- ✅ User account created in database
- ✅ JWT token issued and stored (check localStorage or cookies)
- ✅ Redirected to `/dashboard`
- ✅ Dashboard shows user name in header
- ✅ Empty state message: "No tasks yet. Create your first task!"

**Verify in Database:**
```sql
SELECT id, email, name, created_at FROM users WHERE email = 'testuser@example.com';
```

---

### Test 1.2: Signup Validation Errors

**Test 1.2a: Duplicate Email**
1. Try to signup again with same email: `testuser@example.com`
2. Expected: ❌ Error message "Email already registered" (HTTP 409)

**Test 1.2b: Password Too Short**
1. Try to signup with password < 8 characters: `pass`
2. Expected: ❌ Error message "Password must be at least 8 characters"

**Test 1.2c: Passwords Don't Match**
1. Password: `password123`, Confirm: `password456`
2. Expected: ❌ Error message "Passwords do not match"

---

### Test 1.3: User Login

**Steps:**
1. Logout if logged in (click "Logout" button)
2. Navigate to `/login`
3. Fill in login form:
   - Email: `testuser@example.com`
   - Password: `password123`
4. Click "Login" button

**Expected Results:**
- ✅ JWT token issued and stored
- ✅ Redirected to `/dashboard`
- ✅ See user name in header
- ✅ If user has tasks, they appear in the list

---

### Test 1.4: Login Validation Errors

**Test 1.4a: Incorrect Password**
1. Try to login with wrong password: `wrongpassword`
2. Expected: ❌ Error message "Invalid credentials" (HTTP 401)

**Test 1.4b: Non-existent Email**
1. Try to login with email: `nonexistent@example.com`
2. Expected: ❌ Error message "Invalid credentials" (HTTP 401)

---

### Test 1.5: Protected Routes

**Test 1.5a: Dashboard Access Without Login**
1. Logout (clear token from localStorage)
2. Try to access http://localhost:3000/dashboard directly
3. Expected: ✅ Redirected to `/login` with message "Please log in"

**Test 1.5b: Token Persistence**
1. Login successfully
2. Refresh the page (F5)
3. Expected: ✅ Remain logged in, dashboard still accessible

---

## Test Suite 2: Task CRUD Operations (User Story 3-7)

### Test 2.1: Create Task (User Story 3)

**Test 2.1a: Create Task with Title Only**
1. Login to dashboard
2. Find "Add Task" form
3. Enter title: `Buy groceries`
4. Leave description empty
5. Click "Add Task" or "Create" button

**Expected Results:**
- ✅ Task created with auto-generated ID
- ✅ Task appears in task list immediately
- ✅ Task shows title: "Buy groceries"
- ✅ Task shows as uncompleted (checkbox unchecked)
- ✅ Form clears after submission
- ✅ Created timestamp displayed

**Verify in Database:**
```sql
SELECT * FROM tasks WHERE title = 'Buy groceries';
```

---

**Test 2.1b: Create Task with Title and Description**
1. Enter title: `Finish project`
2. Enter description: `Complete Phase 2 implementation and testing`
3. Click "Add Task"

**Expected Results:**
- ✅ Task created with both title and description
- ✅ Description visible in task item (might be collapsed/expandable)

---

**Test 2.1c: Validation - Title Too Long**
1. Enter title with 201+ characters (copy/paste long text)
2. Try to create task

**Expected Results:**
- ❌ Error message "Title must be 200 characters or less" (HTTP 400)

---

**Test 2.1d: Validation - Empty Title**
1. Leave title empty
2. Try to create task

**Expected Results:**
- ❌ Form validation prevents submission (required field)
- ❌ Or error message "Title is required"

---

### Test 2.2: View Task List (User Story 4)

**Test 2.2a: View All Tasks**
1. Create 5 different tasks
2. View dashboard

**Expected Results:**
- ✅ All 5 tasks visible in list
- ✅ Tasks ordered by creation date (newest first)
- ✅ Each task shows: title, description (if any), completed status, created date

---

**Test 2.2b: Empty State**
1. Delete all tasks
2. View dashboard

**Expected Results:**
- ✅ See message: "No tasks yet. Create your first task!" (or similar)
- ✅ Add task form still accessible

---

**Test 2.2c: Filter by Status (if implemented)**
1. Create some completed and uncompleted tasks
2. Try filter: "All" / "Pending" / "Completed"

**Expected Results:**
- ✅ "All" shows all tasks
- ✅ "Pending" shows only uncompleted tasks
- ✅ "Completed" shows only completed tasks

---

### Test 2.3: Mark Task Complete/Incomplete (User Story 5)

**Test 2.3a: Mark Task as Complete**
1. Find an uncompleted task
2. Click the checkbox (or "Mark Complete" button)

**Expected Results:**
- ✅ Checkbox becomes checked
- ✅ Task title shows strikethrough (line-through style)
- ✅ Task text turns gray
- ✅ `updated_at` timestamp changes in database

**Verify in Database:**
```sql
SELECT id, title, completed, updated_at FROM tasks WHERE id = <task_id>;
```

---

**Test 2.3b: Mark Task as Incomplete**
1. Find a completed task
2. Click the checkbox again

**Expected Results:**
- ✅ Checkbox becomes unchecked
- ✅ Strikethrough removed
- ✅ Task text returns to normal color
- ✅ `updated_at` timestamp updated

---

**Test 2.3c: Status Persists After Refresh**
1. Toggle task completion
2. Refresh page (F5)

**Expected Results:**
- ✅ Task completion status persists correctly

---

### Test 2.4: Update Task Details (User Story 6)

**Test 2.4a: Edit Task Title**
1. Find a task
2. Click "Edit" button (or pencil icon)
3. Modal/form opens with current task data
4. Change title to: `Buy organic groceries`
5. Click "Save" button

**Expected Results:**
- ✅ Modal/form closes
- ✅ Task title updated in list
- ✅ `updated_at` timestamp changed
- ✅ Task ID remains the same

**Verify in Database:**
```sql
SELECT id, title, updated_at FROM tasks WHERE id = <task_id>;
```

---

**Test 2.4b: Edit Task Description**
1. Click "Edit" on a task
2. Update description to: `Make sure to buy fruits and vegetables`
3. Save changes

**Expected Results:**
- ✅ Description updated in task list/detail view
- ✅ `updated_at` timestamp changed

---

**Test 2.4c: Edit Validation - Empty Title**
1. Click "Edit"
2. Clear the title field (make it empty)
3. Try to save

**Expected Results:**
- ❌ Error message "Title is required" (HTTP 400)
- ❌ Or form validation prevents saving

---

**Test 2.4d: Cancel Edit**
1. Click "Edit"
2. Make changes but don't save
3. Click "Cancel" button

**Expected Results:**
- ✅ Modal/form closes
- ✅ Changes NOT saved
- ✅ Original task data remains unchanged

---

### Test 2.5: Delete Task (User Story 7)

**Test 2.5a: Delete Task**
1. Find a task
2. Click "Delete" button (or trash icon)
3. Confirmation dialog appears: "Are you sure?"
4. Click "Confirm" or "Yes"

**Expected Results:**
- ✅ Task removed from list immediately
- ✅ Task permanently deleted from database (not soft delete)
- ✅ Success message appears (optional)

**Verify in Database:**
```sql
SELECT COUNT(*) FROM tasks WHERE id = <deleted_task_id>;
-- Should return 0
```

---

**Test 2.5b: Cancel Delete**
1. Click "Delete"
2. Click "Cancel" in confirmation dialog

**Expected Results:**
- ✅ Task remains in list
- ✅ No changes to database

---

## Test Suite 3: Multi-User Isolation (User Story 4 - Data Isolation)

### Test 3.1: Create Second User

**Steps:**
1. Logout from first user account
2. Signup with new credentials:
   - Name: `Second User`
   - Email: `user2@example.com`
   - Password: `password123`
3. Login as second user

**Expected Results:**
- ✅ New user account created
- ✅ Dashboard is empty (no tasks from first user visible)

---

### Test 3.2: Verify Data Isolation

**Test 3.2a: User A Cannot See User B's Tasks**
1. Login as User A (`testuser@example.com`)
2. Create 3 tasks: "Task A1", "Task A2", "Task A3"
3. Note the task IDs
4. Logout and login as User B (`user2@example.com`)
5. View dashboard

**Expected Results:**
- ✅ User B sees ONLY empty dashboard
- ✅ User B does NOT see User A's tasks ("Task A1", "Task A2", "Task A3")

---

**Test 3.2b: User B Cannot Access User A's Tasks via API**
1. Login as User B
2. Get User B's JWT token from localStorage
3. Try to fetch User A's tasks via API:
   ```bash
   curl -H "Authorization: Bearer <user_b_token>" \
        http://localhost:8000/api/<user_a_id>/tasks
   ```

**Expected Results:**
- ❌ HTTP 403 Forbidden
- ❌ Error message: "Cannot access other user's tasks" or "Unauthorized"

---

**Test 3.2c: Both Users Can Manage Their Own Tasks**
1. User A creates 2 tasks
2. User B creates 3 tasks
3. User A sees only their 2 tasks
4. User B sees only their 3 tasks

**Expected Results:**
- ✅ Complete data isolation between users
- ✅ Each user can only see, edit, delete their own tasks

**Verify in Database:**
```sql
-- User A's tasks
SELECT COUNT(*) FROM tasks WHERE user_id = '<user_a_id>';  -- Should be 2

-- User B's tasks
SELECT COUNT(*) FROM tasks WHERE user_id = '<user_b_id>';  -- Should be 3
```

---

## Test Suite 4: User Logout (User Story 8)

### Test 4.1: Logout Functionality

**Steps:**
1. Login to account
2. Verify user name displayed in header
3. Click "Logout" button

**Expected Results:**
- ✅ JWT token removed from localStorage/cookies
- ✅ Redirected to `/login` page
- ✅ Success message: "Logged out successfully" (optional)

---

### Test 4.2: Post-Logout Access Control

**Test 4.2a: Cannot Access Dashboard After Logout**
1. After logout, try to access http://localhost:3000/dashboard

**Expected Results:**
- ✅ Redirected back to `/login`
- ✅ Message: "Please log in to continue"

---

**Test 4.2b: API Requests Fail Without Token**
1. After logout, try API request:
   ```bash
   curl http://localhost:8000/api/<user_id>/tasks
   ```

**Expected Results:**
- ❌ HTTP 401 Unauthorized
- ❌ Error message: "Missing or invalid Authorization header"

---

## Test Suite 5: Error Handling & UX

### Test 5.1: Loading States

**Check that loading indicators appear for:**
- [ ] Login button during authentication
- [ ] Signup button during account creation
- [ ] Add task button during task creation
- [ ] Update task button during edit
- [ ] Delete confirmation during deletion

---

### Test 5.2: Error Messages

**Test error handling for:**
- [x] Network errors (disconnect WiFi temporarily)
- [x] 401 Unauthorized (expired/invalid token)
- [x] 403 Forbidden (accessing other user's resources)
- [x] 404 Not Found (non-existent task ID)
- [x] 400 Bad Request (validation errors)
- [x] 500 Internal Server Error (backend crashes)

**Expected:**
- ✅ User-friendly error messages (no stack traces)
- ✅ No blank screens
- ✅ Guidance on how to resolve the error

---

### Test 5.3: Responsive Design

**Test on different screen sizes:**
- [ ] Desktop (1920x1080)
- [ ] Tablet (768x1024)
- [ ] Mobile (375x667)

**Expected:**
- ✅ Layout adapts to screen size
- ✅ No horizontal scrolling on mobile
- ✅ Buttons and forms are tappable on mobile

---

## Test Suite 6: Performance & Database

### Test 6.1: Database Indexes (Completed ✓)

**Verify indexes exist:**
```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'tasks'
ORDER BY indexname;
```

**Expected indexes:**
- ✅ `idx_tasks_user_id` - Index on user_id
- ✅ `idx_tasks_completed` - Index on completed
- ✅ `tasks_pkey` - Primary key on id

---

### Test 6.2: Query Performance

**Test with 100+ tasks:**
1. Create 100 tasks for one user
2. Measure page load time for dashboard
3. Filter by status (pending/completed)

**Expected:**
- ✅ Dashboard loads in < 2 seconds
- ✅ No noticeable lag when filtering

---

## Testing Completion Checklist

After completing all tests, verify:

### Functionality
- [ ] All user stories (US1-US8) work correctly
- [ ] No critical bugs or blockers
- [ ] Error handling works as expected
- [ ] Data isolation verified

### Code Quality
- [ ] No console errors in browser DevTools
- [ ] No unhandled promise rejections
- [ ] API returns correct HTTP status codes
- [ ] Database constraints enforced

### User Experience
- [ ] Forms are intuitive and validated
- [ ] Loading states provide feedback
- [ ] Error messages are helpful
- [ ] Responsive on mobile/tablet/desktop

### Security
- [ ] JWT authentication required for all protected routes
- [ ] Users cannot access other users' data
- [ ] Passwords are hashed (not plain text in DB)
- [ ] CORS properly configured

### Performance
- [ ] Database indexes created
- [ ] Page loads quickly
- [ ] No memory leaks (run for extended period)

---

## Bug Report Template

If you find bugs, document them using this format:

```
**Bug**: [Short description]
**Severity**: Critical / High / Medium / Low
**Steps to Reproduce**:
1. ...
2. ...
3. ...

**Expected**: [What should happen]
**Actual**: [What actually happened]
**Screenshots**: [If applicable]
**Console Errors**: [From DevTools]
**Environment**: Browser, OS
```

---

## Next Steps After Testing

Once all tests pass:
1. ✅ **Document test results** - Note any bugs found and fixed
2. ✅ **Create demo video** (90 seconds for hackathon)
3. ✅ **Deploy to production** (Vercel for frontend, Railway/Render for backend)
4. ✅ **Update README** with deployment URLs
5. ✅ **Submit hackathon deliverables**

---

**Happy Testing!** 🧪🚀
