'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { requireAuth, logout } from '@/lib/auth';
import { api } from '@/lib/api';
import { Task } from '@/lib/types';
import { AddTaskForm } from '@/components/AddTaskForm';
import { TaskItem } from '@/components/TaskItem';
import { Button } from '@/components/ui/Button';
import { ChatInterface } from '@/components/chat/ChatInterface';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');

  useEffect(() => {
    const currentUser = requireAuth();
    if (!currentUser) {
      router.push('/login');
      return;
    }
    setUser(currentUser);
    loadTasks(currentUser.id);
  }, [router]);

  async function loadTasks(userId: string, status: string = 'all') {
    setIsLoading(true);
    try {
      const fetchedTasks = await api.getTasks(userId, status);
      setTasks(fetchedTasks);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setIsLoading(false);
    }
  }

  function handleFilterChange(newFilter: 'all' | 'pending' | 'completed') {
    setFilter(newFilter);
    if (user) {
      loadTasks(user.id, newFilter);
    }
  }

  function handleLogout() {
    logout();
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <p className="text-sm text-gray-600 mt-1">Welcome, {user.name}!</p>
          </div>
          <div className="flex gap-3">
            <Button onClick={() => router.push('/settings')} variant="secondary">
              Settings
            </Button>
            <Button onClick={handleLogout} variant="secondary">
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Tasks */}
        <div className="space-y-6">
          {/* Add Task Form */}
          <AddTaskForm
            userId={user.id}
            onTaskAdded={() => loadTasks(user.id, filter)}
          />

          {/* Filter Tabs */}
          <div className="mb-6 flex gap-2 border-b border-gray-200">
          {(['all', 'pending', 'completed'] as const).map((f) => (
            <button
              key={f}
              onClick={() => handleFilterChange(f)}
              className={`px-4 py-2 font-medium capitalize ${
                filter === f
                  ? 'border-b-2 border-primary text-primary'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {f}
            </button>
          ))}
          </div>

          {/* Task List */}
          {isLoading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : tasks.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-600">
                {filter === 'all'
                  ? 'No tasks yet. Create your first task above or use the AI chat!'
                  : `No ${filter} tasks.`}
              </p>
            </div>
          ) : (
            <div>
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  userId={user.id}
                  onTaskUpdated={() => loadTasks(user.id, filter)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Right Column: AI Chat */}
        <div className="lg:sticky lg:top-8 h-fit">
          <ChatInterface
            userId={user.id}
            onTaskCreated={() => loadTasks(user.id, filter)}
          />
        </div>
        </div>
      </main>
    </div>
  );
}
