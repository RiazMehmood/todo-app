'use client';

import { useState, FormEvent } from 'react';
import { api } from '@/lib/api';
import { Priority, RecurrencePattern, DayOfWeek } from '@/lib/types';
import { Button } from './ui/Button';
import { Input } from './ui/Input';

interface AddTaskFormProps {
  userId: string;
  onTaskAdded: () => void;
}

export function AddTaskForm({ userId, onTaskAdded }: AddTaskFormProps) {
  // Basic fields
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  // Phase V - Intermediate: Priority & Tags
  const [priority, setPriority] = useState<Priority>('medium');
  const [tagsInput, setTagsInput] = useState('');

  // Phase V - Advanced: Due Dates & Reminders
  const [dueDate, setDueDate] = useState('');
  const [remindBefore, setRemindBefore] = useState(60); // Default: 60 minutes

  // Phase V - Advanced: Recurring Tasks
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern>('daily');
  const [recurrenceInterval, setRecurrenceInterval] = useState(1);
  const [recurrenceDays, setRecurrenceDays] = useState<DayOfWeek[]>([]);
  const [recurrenceEndDate, setRecurrenceEndDate] = useState('');

  // UI state
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const daysOfWeek: DayOfWeek[] = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
  ];

  function toggleRecurrenceDay(day: DayOfWeek) {
    setRecurrenceDays((prev) =>
      prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      // Parse tags from comma-separated input
      const tags =
        tagsInput
          .split(',')
          .map((t) => t.trim())
          .filter((t) => t.length > 0) || undefined;

      // Validate recurring task fields
      if (isRecurring) {
        if (!recurrencePattern) {
          setError('Recurrence pattern is required for recurring tasks');
          setIsSubmitting(false);
          return;
        }
        if (recurrencePattern === 'weekly' && recurrenceDays.length === 0) {
          setError('Please select at least one day for weekly recurring tasks');
          setIsSubmitting(false);
          return;
        }
      }

      await api.createTask(userId, {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        tags,
        due_date: dueDate || undefined,
        remind_before_minutes: dueDate ? remindBefore : undefined,
        is_recurring: isRecurring,
        recurrence_pattern: isRecurring ? recurrencePattern : undefined,
        recurrence_interval: isRecurring ? recurrenceInterval : undefined,
        recurrence_days:
          isRecurring && recurrencePattern === 'weekly' ? recurrenceDays : undefined,
        recurrence_end_date: isRecurring && recurrenceEndDate ? recurrenceEndDate : undefined,
      });

      // Reset form
      resetForm();

      // Notify parent to refresh task list
      onTaskAdded();
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setIsSubmitting(false);
    }
  }

  function resetForm() {
    setTitle('');
    setDescription('');
    setPriority('medium');
    setTagsInput('');
    setDueDate('');
    setRemindBefore(60);
    setIsRecurring(false);
    setRecurrencePattern('daily');
    setRecurrenceInterval(1);
    setRecurrenceDays([]);
    setRecurrenceEndDate('');
    setShowAdvanced(false);
  }

  return (
    <div className="card mb-6">
      <h2 className="text-xl font-bold mb-4">Add New Task</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Title */}
        <Input
          label="Title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          placeholder="What needs to be done?"
        />

        {/* Description */}
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

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value as Priority)}
            className="input"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        {/* Tags */}
        <Input
          label="Tags (optional)"
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          placeholder="work, urgent, personal (comma-separated)"
        />

        {/* Advanced Features Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {showAdvanced ? '− Hide' : '+ Show'} Advanced Options (Due Date, Reminders,
          Recurring)
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="border-t pt-4 space-y-4">
            {/* Due Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Due Date (optional)
              </label>
              <input
                type="datetime-local"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                className="input"
              />
            </div>

            {/* Reminder */}
            {dueDate && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Remind me before (minutes)
                </label>
                <input
                  type="number"
                  value={remindBefore}
                  onChange={(e) => setRemindBefore(Number(e.target.value))}
                  min={0}
                  className="input"
                />
              </div>
            )}

            {/* Recurring Task */}
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={isRecurring}
                  onChange={(e) => setIsRecurring(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm font-medium text-gray-700">Recurring Task</span>
              </label>
            </div>

            {/* Recurrence Settings */}
            {isRecurring && (
              <div className="ml-6 space-y-3 border-l-2 border-gray-200 pl-4">
                {/* Pattern */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Repeat Pattern
                  </label>
                  <select
                    value={recurrencePattern}
                    onChange={(e) => setRecurrencePattern(e.target.value as RecurrencePattern)}
                    className="input"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                {/* Interval */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Every (interval)
                  </label>
                  <input
                    type="number"
                    value={recurrenceInterval}
                    onChange={(e) => setRecurrenceInterval(Number(e.target.value))}
                    min={1}
                    max={365}
                    className="input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {recurrencePattern === 'daily' && `Every ${recurrenceInterval} day(s)`}
                    {recurrencePattern === 'weekly' && `Every ${recurrenceInterval} week(s)`}
                    {recurrencePattern === 'monthly' && `Every ${recurrenceInterval} month(s)`}
                  </p>
                </div>

                {/* Days of Week (for weekly pattern) */}
                {recurrencePattern === 'weekly' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Repeat on days
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {daysOfWeek.map((day) => (
                        <button
                          key={day}
                          type="button"
                          onClick={() => toggleRecurrenceDay(day)}
                          className={`px-3 py-1 text-sm rounded ${
                            recurrenceDays.includes(day)
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                          }`}
                        >
                          {day.slice(0, 3).toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* End Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date (optional)
                  </label>
                  <input
                    type="date"
                    value={recurrenceEndDate}
                    onChange={(e) => setRecurrenceEndDate(e.target.value)}
                    className="input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty for indefinite recurrence
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="rounded-md bg-red-50 p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Submit Button */}
        <Button type="submit" disabled={!title.trim() || isSubmitting} className="w-full">
          {isSubmitting ? 'Adding...' : 'Add Task'}
        </Button>
      </form>
    </div>
  );
}
