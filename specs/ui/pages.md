# UI Pages Specification

## Overview

Page-level specifications for the Todo web application. Built with Next.js 16+ App Router, each page defines its route, layout, data fetching, and component composition.

## Route Structure

```
/                     → Home/Landing page (redirect to /dashboard or /login)
/login                → Login page
/signup               → Signup page
/dashboard            → Main todo dashboard (protected)
```

## Pages

### 1. Home Page `/`

**File**: `app/page.tsx`

**Type**: Server Component

**Purpose**: Landing page or redirect

**Logic:**
- If user is authenticated → redirect to `/dashboard`
- If not authenticated → redirect to `/login` or show landing page

**Example:**
```tsx
// app/page.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';

export default async function HomePage() {
  const session = await getSession();

  if (session) {
    redirect('/dashboard');
  }

  redirect('/login');
}
```

**Alternative** (with landing page):
```tsx
export default async function HomePage() {
  const session = await getSession();

  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Welcome to Todo App</h1>
        <p className="mb-8">Manage your tasks efficiently</p>
        <div className="space-x-4">
          <Link href="/login">Login</Link>
          <Link href="/signup">Sign Up</Link>
        </div>
      </div>
    </div>
  );
}
```

---

### 2. Login Page `/login`

**File**: `app/login/page.tsx`

**Type**: Mixed (Server + Client Components)

**Purpose**: User authentication

**Features:**
- Email and password form
- Error messages for invalid credentials
- Link to signup page
- Redirect to dashboard on success

**Layout:**
```
┌────────────────────────────────────┐
│                                    │
│          Todo App Logo             │
│                                    │
│  ┌──────────────────────────────┐ │
│  │        Login                 │ │
│  │                              │ │
│  │  Email: [____________]       │ │
│  │                              │ │
│  │  Password: [____________]    │ │
│  │                              │ │
│  │  [x] Remember me             │ │
│  │                              │ │
│  │  [  Login  ]                 │ │
│  │                              │ │
│  │  Don't have an account?      │ │
│  │  Sign up                     │ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

**Example:**
```tsx
// app/login/page.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import { LoginForm } from '@/components/LoginForm';

export default async function LoginPage() {
  const session = await getSession();

  // Already logged in → redirect to dashboard
  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div className="text-center">
          <h2 className="text-3xl font-bold">Login to Todo App</h2>
          <p className="mt-2 text-gray-600">
            Welcome back! Please login to your account
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
```

**Metadata:**
```tsx
export const metadata = {
  title: 'Login | Todo App',
  description: 'Login to your Todo account',
};
```

---

### 3. Signup Page `/signup`

**File**: `app/signup/page.tsx`

**Type**: Mixed (Server + Client Components)

**Purpose**: User registration

**Features:**
- Name, email, and password form
- Password confirmation field
- Validation messages
- Link to login page
- Redirect to dashboard on success

**Layout:**
```
┌────────────────────────────────────┐
│                                    │
│          Todo App Logo             │
│                                    │
│  ┌──────────────────────────────┐ │
│  │        Sign Up               │ │
│  │                              │ │
│  │  Name: [____________]        │ │
│  │                              │ │
│  │  Email: [____________]       │ │
│  │                              │ │
│  │  Password: [____________]    │ │
│  │                              │ │
│  │  Confirm: [____________]     │ │
│  │                              │ │
│  │  [  Sign Up  ]               │ │
│  │                              │ │
│  │  Already have an account?    │ │
│  │  Login                       │ │
│  └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

**Example:**
```tsx
// app/signup/page.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import { SignupForm } from '@/components/SignupForm';

export default async function SignupPage() {
  const session = await getSession();

  if (session) {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div className="text-center">
          <h2 className="text-3xl font-bold">Create Account</h2>
          <p className="mt-2 text-gray-600">
            Sign up to start managing your tasks
          </p>
        </div>
        <SignupForm />
      </div>
    </div>
  );
}
```

**Metadata:**
```tsx
export const metadata = {
  title: 'Sign Up | Todo App',
  description: 'Create your Todo account',
};
```

---

### 4. Dashboard Page `/dashboard`

**File**: `app/dashboard/page.tsx`

**Type**: Server Component (with Client Components inside)

**Purpose**: Main task management interface

**Features:**
- Protected route (requires authentication)
- Display all user's tasks
- Add new task form
- Edit/delete/toggle tasks
- Filter by status (future)

**Layout:**
```
┌────────────────────────────────────────────────────────┐
│  Header: Todo App     |     Hello, John Doe  [Logout] │
├────────────────────────────────────────────────────────┤
│                                                        │
│  My Tasks                                              │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Add New Task                                    │ │
│  │  Title: [_____________________________]          │ │
│  │  Description: [______________________]           │ │
│  │  [Add Task]                                      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ [✓] Buy groceries           [Edit] [Delete]      │ │
│  │     Milk, eggs, bread                            │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ [ ] Call dentist            [Edit] [Delete]      │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ [✓] Finish project report   [Edit] [Delete]      │ │
│  │     Due by Friday                                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Example:**
```tsx
// app/dashboard/page.tsx
import { redirect } from 'next/navigation';
import { getSession } from '@/lib/auth';
import { Header } from '@/components/Header';
import { TaskList } from '@/components/TaskList';
import { AddTaskForm } from '@/components/AddTaskForm';

export default async function DashboardPage() {
  const session = await getSession();

  // Not logged in → redirect to login
  if (!session) {
    redirect('/login');
  }

  const user = session.user;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <main className="container mx-auto max-w-4xl p-8">
        <h1 className="text-3xl font-bold mb-8">My Tasks</h1>

        <section className="mb-8 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Add New Task</h2>
          <AddTaskForm userId={user.id} />
        </section>

        <section className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Your Tasks</h2>
          <TaskList userId={user.id} />
        </section>
      </main>
    </div>
  );
}
```

**Metadata:**
```tsx
export const metadata = {
  title: 'Dashboard | Todo App',
  description: 'Manage your tasks',
};
```

**Data Fetching:**
- Tasks fetched server-side in `TaskList` component
- Or use Next.js Server Actions for mutations

---

## Layout Component

**File**: `app/layout.tsx`

**Purpose**: Root layout for all pages

**Features:**
- Global HTML structure
- Metadata configuration
- Global styles
- Auth provider wrapper (if using Better Auth client context)

**Example:**
```tsx
// app/layout.tsx
import './globals.css';
import { Inter } from 'next/font/google';
import { AuthProvider } from '@/components/AuthProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Todo App - Manage Your Tasks',
  description: 'A modern todo application with AI-powered features',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

---

## Navigation Flow

```
Start
  │
  ▼
 [ / ]  ──authenticated?──> Yes ──> [/dashboard]
  │
  │
  No
  │
  ▼
[/login] <──────┬────────> [/signup]
  │             │              │
  │             │              │
  Login         Link           Signup
  │                            │
  │                            │
  └────────> [/dashboard] <────┘
```

---

## Protected Routes

Use middleware or per-page authentication checks:

**Option 1: Page-level check** (shown above)
```tsx
const session = await getSession();
if (!session) redirect('/login');
```

**Option 2: Middleware** (`middleware.ts`)
```tsx
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token');

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/dashboard/:path*',
};
```

---

## Error Pages

### 404 Page

**File**: `app/not-found.tsx`

```tsx
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold">404</h1>
        <p className="text-xl mt-4">Page not found</p>
        <Link href="/dashboard" className="mt-8 inline-block">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
```

### Error Page

**File**: `app/error.tsx`

```tsx
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
        <h1 className="text-3xl font-bold">Something went wrong!</h1>
        <p className="mt-4">{error.message}</p>
        <button onClick={reset} className="mt-8">
          Try again
        </button>
      </div>
    </div>
  );
}
```

---

## Loading States

**File**: `app/dashboard/loading.tsx`

```tsx
export default function DashboardLoading() {
  return (
    <div className="container mx-auto max-w-4xl p-8">
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
        <div className="h-64 bg-gray-200 rounded mb-4"></div>
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    </div>
  );
}
```

---

## Responsive Design

All pages should be mobile-responsive:

```tsx
<main className="container mx-auto px-4 sm:px-6 lg:px-8">
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    ...
  </div>
</main>
```

---

## SEO Optimization

Use Next.js metadata API:

```tsx
export const metadata = {
  title: 'Dashboard | Todo App',
  description: 'Manage your tasks efficiently',
  openGraph: {
    title: 'Todo App',
    description: 'Manage your tasks efficiently',
    type: 'website',
  },
};
```

---

## Analytics (Future)

Add analytics tracking:

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

---

## Future Pages (Not in Phase II)

- `/settings` - User settings
- `/profile` - User profile
- `/tasks/[id]` - Single task detail page
- `/archive` - Archived tasks
- `/analytics` - Task statistics

---

## Accessibility

- Use semantic HTML (`<main>`, `<section>`, `<header>`)
- Add skip navigation links
- Ensure keyboard navigation works
- Provide ARIA landmarks

**Example:**
```tsx
<main role="main" aria-label="Main content">
  <h1>Dashboard</h1>
  ...
</main>
```

---

## Performance

- Use Next.js image optimization
- Implement lazy loading for heavy components
- Use React Suspense for data fetching
- Minimize client-side JavaScript

---

## Testing

Test each page:
```typescript
test('dashboard shows tasks for logged-in user', async ({ page }) => {
  await login(page);
  await page.goto('/dashboard');
  await expect(page.locator('h1')).toContainText('My Tasks');
});
```

---

## References

- [Next.js App Router](https://nextjs.org/docs/app)
- [Next.js Metadata](https://nextjs.org/docs/app/building-your-application/optimizing/metadata)
- [Next.js Authentication](https://nextjs.org/docs/app/building-your-application/authentication)
