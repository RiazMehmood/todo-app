'use client';

import { useState, FormEvent } from 'react';
import { api } from '@/lib/api';
import { Button } from './ui/Button';
import { Input } from './ui/Input';

interface AddTaskFormProps {
  userId: string;
  onTaskAdded: () => void;
}

export function AddTaskForm({ userId, onTaskAdded }: AddTaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await api.createTask(userId, {
        title: title.trim(),
        description: description.trim() || undefined,
      });

      // Reset form
      setTitle('');
      setDescription('');

      // Notify parent to refresh task list
      onTaskAdded();
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="card mb-6">
      <h2 className="text-xl font-bold mb-4">Add New Task</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          placeholder="What needs to be done?"
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={1000}
            rows={3}
            className="input resize-none"
            placeholder="Add more details..."
          />
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <Button
          type="submit"
          disabled={!title.trim() || isSubmitting}
          className="w-full"
        >
          {isSubmitting ? 'Adding...' : 'Add Task'}
        </Button>
      </form>
    </div>
  );
}
