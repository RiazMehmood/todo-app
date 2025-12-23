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
  const [toggleMessage, setToggleMessage] = useState('');

  // Helper to get priority badge color
  function getPriorityColor(priority: string) {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  }

  // Check if task is overdue
  function isOverdue(): boolean {
    if (!task.due_date || task.completed) return false;
    return new Date(task.due_date) < new Date();
  }

  // Format due date display
  function formatDueDate(): string {
    if (!task.due_date) return '';
    const date = new Date(task.due_date);
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Due today';
    if (diffDays === 1) return 'Due tomorrow';
    if (diffDays === -1) return 'Due yesterday';
    if (diffDays < 0) return `Overdue by ${Math.abs(diffDays)} days`;
    if (diffDays < 7) return `Due in ${diffDays} days`;

    return `Due ${date.toLocaleDateString()}`;
  }

  async function handleToggle() {
    setIsLoading(true);
    setToggleMessage('');
    try {
      const response = await api.toggleTask(userId, task.id);

      // Show message if recurring task created new instance
      if (response.message) {
        setToggleMessage(response.message);
        setTimeout(() => setToggleMessage(''), 5000);
      }

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
    <div className="card mb-4 flex items-start gap-4 hover:shadow-md transition-shadow">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={handleToggle}
        disabled={isLoading}
        className="mt-1 h-5 w-5 rounded border-gray-300 text-primary focus:ring-primary cursor-pointer"
      />
      <div className="flex-1 min-w-0">
        {/* Title */}
        <div className="flex items-start gap-2 flex-wrap">
          <h3
            className={`text-lg font-medium ${
              task.completed ? 'line-through text-gray-500' : 'text-gray-900'
            }`}
          >
            {task.title}
          </h3>

          {/* Priority Badge */}
          <span
            className={`px-2 py-0.5 text-xs font-medium rounded border ${getPriorityColor(
              task.priority
            )}`}
          >
            {task.priority.toUpperCase()}
          </span>

          {/* Recurring Indicator */}
          {task.is_recurring && (
            <span className="px-2 py-0.5 text-xs font-medium rounded bg-blue-100 text-blue-800 border border-blue-200">
              ⟳ {task.recurrence_pattern}
            </span>
          )}
        </div>

        {/* Description */}
        {task.description && (
          <p className={`mt-1 text-sm ${task.completed ? 'text-gray-400' : 'text-gray-600'}`}>
            {task.description}
          </p>
        )}

        {/* Tags */}
        {task.tags && task.tags.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {task.tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded-full border border-gray-200"
              >
                #{tag}
              </span>
            ))}
          </div>
        )}

        {/* Due Date & Meta Info */}
        <div className="mt-2 flex flex-wrap gap-3 text-xs">
          {/* Due Date */}
          {task.due_date && (
            <span
              className={`font-medium ${
                isOverdue()
                  ? 'text-red-600'
                  : task.completed
                  ? 'text-gray-400'
                  : 'text-orange-600'
              }`}
            >
              📅 {formatDueDate()}
            </span>
          )}

          {/* Created Date */}
          <span className="text-gray-400">
            Created: {new Date(task.created_at).toLocaleDateString()}
          </span>

          {/* AI Created Indicator */}
          {task.created_via_ai && (
            <span className="text-purple-600 font-medium">🤖 AI Created</span>
          )}
        </div>

        {/* Recurring Task Details */}
        {task.is_recurring && task.recurrence_days && task.recurrence_days.length > 0 && (
          <div className="mt-2 text-xs text-gray-500">
            Repeats on: {task.recurrence_days.map((d) => d.slice(0, 3)).join(', ')}
          </div>
        )}

        {/* Toggle Message (for recurring tasks) */}
        {toggleMessage && (
          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
            {toggleMessage}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2 flex-shrink-0">
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
