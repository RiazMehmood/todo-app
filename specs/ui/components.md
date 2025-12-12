# UI Components Specification

## Overview

Component library for the Todo web application built with Next.js 16+, React, and Tailwind CSS. Components follow atomic design principles and are organized by functionality.

## Design Principles

1. **Component-Driven**: Reusable, composable components
2. **Server Components First**: Use React Server Components by default
3. **Client Components When Needed**: For interactivity (onClick, forms, etc.)
4. **Tailwind CSS**: Utility-first styling, no CSS-in-JS
5. **Accessibility**: ARIA labels, keyboard navigation, semantic HTML
6. **Responsive**: Mobile-first design

## Component Hierarchy

```
App
├── Layout
│   ├── Header
│   └── Footer (optional)
├── Pages
│   ├── LoginPage
│   ├── SignupPage
│   └── DashboardPage
│       ├── TaskList
│       │   └── TaskItem (multiple)
│       └── AddTaskForm
└── Shared
    ├── Button
    ├── Input
    ├── Modal
    └── Loading
```

## Core Components

### 1. Header

**Purpose**: Navigation bar with auth controls

**Type**: Server Component

**Props:**
```typescript
interface HeaderProps {
  user?: {
    id: string;
    name: string;
    email: string;
  };
}
```

**Usage:**
```tsx
<Header user={session?.user} />
```

**Features:**
- App logo/title
- User display name (if logged in)
- Logout button (if logged in)
- Login/Signup links (if not logged in)

**Example:**
```tsx
// components/Header.tsx
export function Header({ user }: HeaderProps) {
  return (
    <header className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-2xl font-bold">Todo App</h1>
        {user ? (
          <div className="flex items-center gap-4">
            <span>Hello, {user.name}</span>
            <LogoutButton />
          </div>
        ) : (
          <div className="flex gap-2">
            <Link href="/login">Login</Link>
            <Link href="/signup">Signup</Link>
          </div>
        )}
      </div>
    </header>
  );
}
```

---

### 2. TaskList

**Purpose**: Display all user's tasks

**Type**: Server Component (fetches data)

**Props:**
```typescript
interface TaskListProps {
  userId: string;
  initialTasks?: Task[];
}
```

**Usage:**
```tsx
<TaskList userId={user.id} />
```

**Features:**
- Fetches tasks from API
- Displays tasks in a table or list
- Shows empty state if no tasks
- Loading state while fetching

**Example:**
```tsx
// components/TaskList.tsx
export async function TaskList({ userId }: TaskListProps) {
  const tasks = await fetchTasks(userId);

  if (tasks.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-2">
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
```

---

### 3. TaskItem

**Purpose**: Display individual task with actions

**Type**: Client Component (interactive)

**Props:**
```typescript
interface TaskItemProps {
  task: Task;
  onToggle?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
}
```

**Usage:**
```tsx
<TaskItem task={task} />
```

**Features:**
- Checkbox to toggle completion
- Task title and description
- Edit button
- Delete button
- Completed tasks have strikethrough styling

**Example:**
```tsx
// components/TaskItem.tsx
'use client';

export function TaskItem({ task }: TaskItemProps) {
  const [isCompleted, setIsCompleted] = useState(task.completed);

  async function handleToggle() {
    await toggleTask(task.id);
    setIsCompleted(!isCompleted);
  }

  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded shadow">
      <input
        type="checkbox"
        checked={isCompleted}
        onChange={handleToggle}
        className="w-5 h-5"
      />
      <div className="flex-1">
        <h3 className={isCompleted ? "line-through text-gray-500" : ""}>
          {task.title}
        </h3>
        {task.description && (
          <p className="text-sm text-gray-600">{task.description}</p>
        )}
      </div>
      <button onClick={() => onEdit(task.id)}>Edit</button>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  );
}
```

---

### 4. AddTaskForm

**Purpose**: Form to create new task

**Type**: Client Component (form submission)

**Props:**
```typescript
interface AddTaskFormProps {
  userId: string;
  onTaskAdded?: (task: Task) => void;
}
```

**Usage:**
```tsx
<AddTaskForm userId={user.id} />
```

**Features:**
- Title input (required)
- Description textarea (optional)
- Submit button
- Form validation
- Loading state during submission
- Success/error messages

**Example:**
```tsx
// components/AddTaskForm.tsx
'use client';

export function AddTaskForm({ userId }: AddTaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await createTask(userId, { title, description });
      setTitle('');
      setDescription('');
      // Revalidate or refresh
    } catch (error) {
      // Show error
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        required
        maxLength={200}
      />
      <Textarea
        label="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        maxLength={1000}
      />
      <Button type="submit" disabled={!title || isSubmitting}>
        {isSubmitting ? 'Adding...' : 'Add Task'}
      </Button>
    </form>
  );
}
```

---

### 5. EditTaskModal

**Purpose**: Modal to edit existing task

**Type**: Client Component

**Props:**
```typescript
interface EditTaskModalProps {
  task: Task;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedTask: Partial<Task>) => Promise<void>;
}
```

**Usage:**
```tsx
<EditTaskModal
  task={selectedTask}
  isOpen={isEditModalOpen}
  onClose={() => setIsEditModalOpen(false)}
  onSave={handleSaveTask}
/>
```

**Features:**
- Modal overlay with backdrop
- Pre-filled form with task data
- Save and Cancel buttons
- Validation
- Close on Escape key

---

### 6. LoginForm

**Purpose**: User login form

**Type**: Client Component

**Props:**
```typescript
interface LoginFormProps {
  onSuccess?: () => void;
}
```

**Features:**
- Email input
- Password input
- "Remember me" checkbox (optional)
- Submit button
- Link to signup page
- Error messages

**Example:**
```tsx
// components/LoginForm.tsx
'use client';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await signIn({ email, password });
      router.push('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="email"
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
      />
      <Input
        type="password"
        label="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="text-red-500">{error}</p>}
      <Button type="submit">Login</Button>
      <p>
        Don't have an account? <Link href="/signup">Sign up</Link>
      </p>
    </form>
  );
}
```

---

### 7. SignupForm

**Purpose**: User registration form

**Type**: Client Component

**Props:**
```typescript
interface SignupFormProps {
  onSuccess?: () => void;
}
```

**Features:**
- Name input
- Email input
- Password input
- Confirm password input
- Submit button
- Link to login page
- Validation and error messages

---

## Shared/Utility Components

### Button

**Purpose**: Reusable button component

**Props:**
```typescript
interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}
```

**Example:**
```tsx
<Button variant="primary" size="md">
  Click Me
</Button>
```

---

### Input

**Purpose**: Reusable text input

**Props:**
```typescript
interface InputProps {
  label?: string;
  type?: 'text' | 'email' | 'password';
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  required?: boolean;
  maxLength?: number;
  error?: string;
}
```

**Example:**
```tsx
<Input
  label="Task Title"
  value={title}
  onChange={(e) => setTitle(e.target.value)}
  required
  maxLength={200}
  error={titleError}
/>
```

---

### Modal

**Purpose**: Reusable modal dialog

**Props:**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}
```

**Example:**
```tsx
<Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Edit Task">
  <EditTaskForm task={task} />
</Modal>
```

---

### Loading

**Purpose**: Loading spinner/skeleton

**Example:**
```tsx
<Loading />
// or
<TaskListSkeleton />
```

---

### EmptyState

**Purpose**: Display when no tasks exist

**Example:**
```tsx
function EmptyState() {
  return (
    <div className="text-center py-12 text-gray-500">
      <p className="text-xl">No tasks yet</p>
      <p>Add your first task to get started!</p>
    </div>
  );
}
```

---

## Styling Guidelines

### Tailwind CSS Classes

**Colors:**
- Primary: `bg-blue-600`, `text-blue-600`
- Success: `bg-green-600`, `text-green-600`
- Danger: `bg-red-600`, `text-red-600`
- Gray: `bg-gray-100`, `text-gray-600`

**Spacing:**
- Padding: `p-4`, `px-6`, `py-2`
- Margin: `m-4`, `mx-auto`, `my-8`
- Gap: `gap-2`, `gap-4`

**Layout:**
- Flexbox: `flex`, `items-center`, `justify-between`
- Grid: `grid`, `grid-cols-2`, `gap-4`
- Container: `container`, `mx-auto`, `max-w-4xl`

**Typography:**
- Headings: `text-2xl`, `font-bold`
- Body: `text-base`, `text-gray-700`
- Small: `text-sm`, `text-gray-500`

### Responsive Design

Use responsive prefixes:
```tsx
<div className="w-full md:w-1/2 lg:w-1/3">
  ...
</div>
```

---

## Accessibility

- Use semantic HTML (`<button>`, `<input>`, `<label>`)
- Add ARIA labels where needed
- Keyboard navigation support
- Focus states for interactive elements
- Alt text for images

**Example:**
```tsx
<button
  aria-label="Delete task"
  onClick={handleDelete}
  className="focus:ring-2 focus:ring-blue-500"
>
  Delete
</button>
```

---

## State Management

- Use React's `useState` for local component state
- Use Next.js server actions for mutations
- Use optimistic updates where appropriate
- Consider React Context for shared state (if needed)

---

## Future Enhancements (Not in Phase II)

- Drag-and-drop for task reordering
- Filter and search components
- Task priority badges
- Due date picker
- Tag selection component
- Dark mode toggle

---

## Component Testing

Use Playwright or Cypress for E2E testing:
```typescript
test('can add a task', async ({ page }) => {
  await page.goto('/dashboard');
  await page.fill('input[name="title"]', 'Test task');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Test task')).toBeVisible();
});
```

---

## References

- [Next.js App Router](https://nextjs.org/docs/app)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Server Components](https://react.dev/reference/react/use-server)
- [ARIA Best Practices](https://www.w3.org/WAI/ARIA/apg/)
