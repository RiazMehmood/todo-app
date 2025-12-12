'use client';

import { useState } from 'react';
import { Task } from '@/lib/types';
import { api } from '@/lib/api';
import { Button } from './ui/Button';

interface TaskItemProps {
  task: Task;
  userId: string;
  onTaskUpdated: () => void;
}

export function TaskItem({ task, userId, onTaskUpdated }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [isLoading, setIsLoading] = useState(false);

  async function handleToggle() {
    setIsLoading(true);
    try {
      await api.toggleTask(userId, task.id);
      onTaskUpdated();
    } catch (err) {
      console.error('Failed to toggle task:', err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpdate() {
    setIsLoading(true);
    try {
      await api.updateTask(userId, task.id, {
        title: editTitle.trim(),
        description: editDescription.trim() || undefined,
      });
      setIsEditing(false);
      onTaskUpdated();
    } catch (err) {
      console.error('Failed to update task:', err);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    setIsLoading(true);
    try {
      await api.deleteTask(userId, task.id);
      onTaskUpdated();
    } catch (err) {
      console.error('Failed to delete task:', err);
    } finally {
      setIsLoading(false);
    }
  }

  if (isEditing) {
    return (
      <div className="card mb-4 border-2 border-primary">
        <div className="space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="input"
            maxLength={200}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="input resize-none"
            rows={2}
            maxLength={1000}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleUpdate}
              disabled={!editTitle.trim() || isLoading}
              variant="primary"
            >
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
            <Button
              onClick={() => {
                setIsEditing(false);
                setEditTitle(task.title);
                setEditDescription(task.description || '');
              }}
              variant="secondary"
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card mb-4 flex items-start gap-4">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        disabled={isLoading}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
      />
      <div className="flex-1">
        <h3
          className={`text-lg font-medium ${
            task.completed ? 'line-through text-gray-500' : 'text-gray-900'
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p className={`mt-1 text-sm ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
            {task.description}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-400">
          Created: {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>
      <div className="flex gap-2">
        <Button
          onClick={() => setIsEditing(true)}
          variant="secondary"
          disabled={isLoading}
          className="text-sm px-3 py-1"
        >
          Edit
        </Button>
        <Button
          onClick={handleDelete}
          variant="danger"
          disabled={isLoading}
          className="text-sm px-3 py-1"
        >
          Delete
        </Button>
      </div>
    </div>
  );
}
