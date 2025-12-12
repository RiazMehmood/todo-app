# Frontend Guidelines - Next.js Todo App

## Overview

This is the **frontend** application for the Todo app, built with Next.js 16+ App Router. It provides a modern, responsive web interface for task management with authentication.

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (client-side)
- **API Client**: Fetch API / httpx
- **Deployment**: Vercel

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page (redirect)
│   ├── login/
│   │   └── page.tsx             # Login page
│   ├── signup/
│   │   └── page.tsx             # Signup page
│   ├── dashboard/
│   │   ├── page.tsx             # Main dashboard (protected)
│   │   └── loading.tsx          # Loading state
│   ├── globals.css              # Global styles
│   └── error.tsx                # Error boundary
├── components/
│   ├── Header.tsx               # Navigation header
│   ├── TaskList.tsx             # Task list (server component)
│   ├── TaskItem.tsx             # Individual task (client component)
│   ├── AddTaskForm.tsx          # Add task form (client component)
│   ├── LoginForm.tsx            # Login form
│   ├── SignupForm.tsx           # Signup form
│   └── ui/                      # Shared UI components
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Modal.tsx
├── lib/
│   ├── api.ts                   # API client with JWT handling
│   ├── auth.ts                  # Auth utilities
│   └── types.ts                 # TypeScript types
├── public/
│   └── ...                      # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Development Patterns

### Server Components by Default

Use React Server Components for:
- Layouts
- Static pages
- Data fetching components (TaskList)
- Components without interactivity

```tsx
// components/TaskList.tsx (Server Component)
export async function TaskList({ userId }: { userId: string }) {
  const tasks = await fetchTasks(userId);

  return (
    <div>
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  );
}
```

### Client Components When Needed

Use Client Components (`'use client'`) for:
- Forms with state (AddTaskForm, LoginForm)
- Interactive elements (TaskItem with checkbox)
- Components using hooks (useState, useEffect)
- Event handlers (onClick, onChange)

```tsx
// components/AddTaskForm.tsx (Client Component)
'use client';

import { useState } from 'react';

export function AddTaskForm({ userId }: { userId: string }) {
  const [title, setTitle] = useState('');
  // ... form logic
}
```

### Component Naming Conventions

- **PascalCase** for component files: `TaskList.tsx`, `AddTaskForm.tsx`
- **Descriptive names**: `LoginForm` not `Form`, `TaskItem` not `Item`
- **Server components**: No special suffix
- **Client components**: Start with `'use client'` directive

## API Client Pattern

All backend API calls should go through `lib/api.ts`:

```tsx
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiCall(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = getAuthToken(); // From Better Auth

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Token expired → redirect to login
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}

// Specific API methods
export const api = {
  getTasks: (userId: string) =>
    apiCall(`/api/${userId}/tasks`),

  createTask: (userId: string, data: { title: string; description?: string }) =>
    apiCall(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateTask: (userId: string, taskId: number, data: Partial<Task>) =>
    apiCall(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteTask: (userId: string, taskId: number) =>
    apiCall(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    }),

  toggleTask: (userId: string, taskId: number) =>
    apiCall(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    }),
};
```

## Styling Guidelines

### Tailwind CSS

- **Utility-first**: Use Tailwind utility classes
- **No inline styles**: Avoid `style={{ ... }}`
- **No CSS-in-JS**: No styled-components or emotion
- **Component classes**: Group related utilities

```tsx
// Good
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Click Me
</button>

// Bad
<button style={{ backgroundColor: 'blue', padding: '8px 16px' }}>
  Click Me
</button>
```

### Responsive Design

Use Tailwind responsive prefixes:

```tsx
<div className="
  w-full           /* Mobile: full width */
  md:w-1/2         /* Tablet: half width */
  lg:w-1/3         /* Desktop: one-third width */
  p-4              /* Padding on all sizes */
  md:p-6           /* More padding on tablet+ */
">
  ...
</div>
```

### Color Palette

- **Primary**: `blue-600` (buttons, links)
- **Success**: `green-600` (completed tasks)
- **Danger**: `red-600` (delete actions)
- **Gray**: `gray-100` to `gray-900` (backgrounds, text)

## Authentication

### Better Auth Setup

1. Install Better Auth:
```bash
npm install better-auth
```

2. Configure in `app/auth/config.ts`

3. Use session management:
```tsx
import { useSession } from '@/lib/auth';

export function Dashboard() {
  const { user, isLoading } = useSession();

  if (isLoading) return <Loading />;
  if (!user) redirect('/login');

  return <div>Hello, {user.name}</div>;
}
```

### Protected Routes

Use middleware or per-page checks:

```tsx
// app/dashboard/page.tsx
import { getSession } from '@/lib/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await getSession();

  if (!session) {
    redirect('/login');
  }

  return <Dashboard user={session.user} />;
}
```

## Form Handling

### Controlled Components

```tsx
'use client';

export function AddTaskForm({ userId }: { userId: string }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      await api.createTask(userId, { title, description });
      setTitle('');
      setDescription('');
      // Trigger revalidation or refresh
      window.location.reload(); // Simple approach
    } catch (err) {
      setError(err.message);
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
      <Input
        label="Description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        maxLength={1000}
      />
      {error && <p className="text-red-600">{error}</p>}
      <Button type="submit" disabled={!title || isSubmitting}>
        {isSubmitting ? 'Adding...' : 'Add Task'}
      </Button>
    </form>
  );
}
```

## Type Safety

### TypeScript Types

Define types in `lib/types.ts`:

```tsx
// lib/types.ts
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
}
```

Use types in components:

```tsx
interface TaskItemProps {
  task: Task;
}

export function TaskItem({ task }: TaskItemProps) {
  // ...
}
```

## Error Handling

### Display User-Friendly Errors

```tsx
try {
  await api.createTask(userId, data);
} catch (error) {
  if (error.message.includes('401')) {
    setError('Please log in again');
  } else if (error.message.includes('400')) {
    setError('Invalid task data');
  } else {
    setError('Something went wrong. Please try again.');
  }
}
```

### Error Boundaries

Use Next.js error boundaries:

```tsx
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-red-600">Error</h1>
        <p className="mt-4">{error.message}</p>
        <button onClick={reset} className="mt-8 px-4 py-2 bg-blue-600 text-white rounded">
          Try Again
        </button>
      </div>
    </div>
  );
}
```

## Loading States

### Skeleton Loading

```tsx
// app/dashboard/loading.tsx
export default function DashboardLoading() {
  return (
    <div className="container mx-auto p-8">
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    </div>
  );
}
```

## Accessibility

- Use semantic HTML: `<button>`, `<input>`, `<label>`
- Add ARIA labels: `aria-label="Delete task"`
- Keyboard navigation: Focus states with `focus:ring-2`
- Alt text for images

```tsx
<button
  aria-label="Delete task"
  className="focus:ring-2 focus:ring-blue-500 focus:outline-none"
  onClick={handleDelete}
>
  Delete
</button>
```

## Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

**Note**: Only `NEXT_PUBLIC_*` variables are exposed to the browser.

## Build and Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run start
```

### Deployment to Vercel
```bash
vercel deploy
```

Set environment variables in Vercel dashboard.

## Testing (Future)

Use Playwright or Cypress for E2E tests:

```typescript
test('can add a task', async ({ page }) => {
  await page.goto('/dashboard');
  await page.fill('input[name="title"]', 'Test task');
  await page.click('button[type="submit"]');
  await expect(page.locator('text=Test task')).toBeVisible();
});
```

## Specifications

Before implementing features, always read:
- `@specs/ui/components.md` - Component specifications
- `@specs/ui/pages.md` - Page specifications
- `@specs/api/rest-endpoints.md` - API contract
- `@specs/features/task-crud.md` - Feature requirements

## Common Tasks

### Add a new page
1. Create `app/new-page/page.tsx`
2. Follow page specification in `@specs/ui/pages.md`
3. Update navigation if needed

### Add a new component
1. Create `components/NewComponent.tsx`
2. Follow component specification in `@specs/ui/components.md`
3. Export from `components/index.ts` (if needed)

### Add a new API method
1. Add method to `lib/api.ts`
2. Follow endpoint specification in `@specs/api/rest-endpoints.md`
3. Handle errors appropriately

## Best Practices

1. **Server Components First**: Use server components unless you need interactivity
2. **Type Everything**: Use TypeScript types for props and data
3. **Tailwind Only**: No inline styles or CSS-in-JS
4. **Error Handling**: Always handle API errors gracefully
5. **Loading States**: Show loading indicators for async operations
6. **Accessibility**: Use semantic HTML and ARIA labels
7. **Responsive**: Mobile-first design with Tailwind responsive classes

## References

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Better Auth Docs](https://better-auth.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
