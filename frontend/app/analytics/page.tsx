/**
 * Analytics Dashboard Page - Comprehensive analytics and reporting interface
 *
 * Implements: User Story 4 (Analytics and Reporting) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/analytics-api.yaml
 *
 * Features:
 * - FR-028: Line chart showing daily task completion trends
 * - FR-029: Pie/bar charts for task distribution by priority, status, and tags
 * - FR-031: Summary metrics (total tasks, completion rate, avg time, total time)
 * - FR-034: Date range filtering for analytics period
 * - FR-032/033: Export buttons for CSV and PDF reports
 */

'use client'

import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'

// ============================================================================
// TypeScript Interfaces (from analytics-api.yaml)
// ============================================================================

interface DateRange {
  start: string
  end: string
}

interface Metrics {
  total_tasks: number
  completed_tasks: number
  completion_rate: number
  average_completion_time_hours: number
  total_time_spent_hours: number
}

interface TasksByPriority {
  high: number
  medium: number
  low: number
}

interface TasksByStatus {
  completed: number
  in_progress: number
  pending: number
}

interface TaskByTag {
  tag: string
  count: number
}

interface CompletionTrendEntry {
  date: string
  completed: number
}

interface AnalyticsOverview {
  date_range: DateRange
  metrics: Metrics
  tasks_by_priority: TasksByPriority
  tasks_by_status: TasksByStatus
  tasks_by_tag: TaskByTag[]
  completion_trend: CompletionTrendEntry[]
}

// ============================================================================
// Chart Color Schemes
// ============================================================================

const PRIORITY_COLORS = {
  high: '#ef4444',    // red-500
  medium: '#f59e0b',  // amber-500
  low: '#10b981'      // green-500
}

const STATUS_COLORS = {
  completed: '#10b981',   // green-500
  in_progress: '#3b82f6', // blue-500
  pending: '#6b7280'      // gray-500
}

const TAG_COLORS = [
  '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981',
  '#06b6d4', '#6366f1', '#f97316', '#14b8a6', '#a855f7'
]

// ============================================================================
// Main Component
// ============================================================================

export default function AnalyticsDashboard() {
  // State management
  const [analytics, setAnalytics] = useState<AnalyticsOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')
  const [userId, setUserId] = useState<string>('user123') // TODO: Get from auth context

  // Initialize date range (default: last 30 days)
  useEffect(() => {
    const today = new Date()
    const thirtyDaysAgo = new Date(today)
    thirtyDaysAgo.setDate(today.getDate() - 30)

    setEndDate(today.toISOString().split('T')[0])
    setStartDate(thirtyDaysAgo.toISOString().split('T')[0])
  }, [])

  // Fetch analytics data when date range changes
  useEffect(() => {
    if (!startDate || !endDate) return

    fetchAnalyticsOverview()
  }, [startDate, endDate, userId])

  /**
   * Fetch analytics overview from API
   * Implements: GET /api/{user_id}/analytics/overview
   */
  const fetchAnalyticsOverview = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      })

      const response = await fetch(
        `http://localhost:8000/api/${userId}/analytics/overview?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`, // TODO: Use auth context
            'Content-Type': 'application/json'
          }
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data: AnalyticsOverview = await response.json()
      setAnalytics(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics')
      console.error('Analytics fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  /**
   * Export analytics data to CSV or PDF
   * Implements: GET /api/{user_id}/analytics/export
   */
  const handleExport = async (format: 'csv' | 'pdf') => {
    try {
      const params = new URLSearchParams({
        format,
        start_date: startDate,
        end_date: endDate
      })

      const response = await fetch(
        `http://localhost:8000/api/${userId}/analytics/export?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`)
      }

      // Download file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `tasks_report_${endDate}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      alert(`Export failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  // Transform priority data for pie chart
  const priorityChartData = analytics
    ? Object.entries(analytics.tasks_by_priority).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
        color: PRIORITY_COLORS[name as keyof typeof PRIORITY_COLORS]
      }))
    : []

  // Transform status data for pie chart
  const statusChartData = analytics
    ? Object.entries(analytics.tasks_by_status).map(([name, value]) => ({
        name: name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
        value,
        color: STATUS_COLORS[name as keyof typeof STATUS_COLORS]
      }))
    : []

  // ============================================================================
  // Render States
  // ============================================================================

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h2 className="text-red-800 font-semibold mb-2">Error Loading Analytics</h2>
          <p className="text-red-600">{error}</p>
          <button
            onClick={fetchAnalyticsOverview}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">No analytics data available</p>
      </div>
    )
  }

  // ============================================================================
  // Main Dashboard Render
  // ============================================================================

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
          <p className="text-gray-600">
            Viewing analytics from {analytics.date_range.start} to {analytics.date_range.end}
          </p>
        </div>

        {/* Date Range Filters & Export Buttons */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-wrap items-end gap-4">
            {/* Date Range Inputs */}
            <div className="flex-1 min-w-[200px]">
              <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="flex-1 min-w-[200px]">
              <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Export Buttons */}
            <div className="flex gap-2">
              <button
                onClick={() => handleExport('csv')}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                aria-label="Export to CSV"
              >
                Export CSV
              </button>
              <button
                onClick={() => handleExport('pdf')}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                aria-label="Export to PDF"
              >
                Export PDF
              </button>
            </div>
          </div>
        </div>

        {/* Summary Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
          <MetricCard
            title="Total Tasks"
            value={analytics.metrics.total_tasks}
            icon="📋"
          />
          <MetricCard
            title="Completed"
            value={analytics.metrics.completed_tasks}
            icon="✅"
          />
          <MetricCard
            title="Completion Rate"
            value={`${analytics.metrics.completion_rate}%`}
            icon="📊"
          />
          <MetricCard
            title="Avg Completion Time"
            value={`${analytics.metrics.average_completion_time_hours}h`}
            icon="⏱️"
          />
          <MetricCard
            title="Total Time Spent"
            value={`${analytics.metrics.total_time_spent_hours}h`}
            icon="🕐"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Completion Trend Line Chart */}
          <ChartCard title="Completion Trend" description="Daily task completions over time">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.completion_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(date) => new Date(date).toLocaleDateString()}
                  formatter={(value) => [`${value} tasks`, 'Completed']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="completed"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6' }}
                  name="Tasks Completed"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Tasks by Priority Pie Chart */}
          <ChartCard title="Tasks by Priority" description="Distribution of task priorities">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={priorityChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) =>
                    `${name}: ${value} (${((percent ?? 0) * 100).toFixed(0)}%)`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {priorityChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Tasks by Status Pie Chart */}
          <ChartCard title="Tasks by Status" description="Current task status breakdown">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value, percent }) =>
                    `${name}: ${value} (${((percent ?? 0) * 100).toFixed(0)}%)`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          {/* Tasks by Tag Bar Chart */}
          <ChartCard title="Tasks by Tag" description="Top tags by task count">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.tasks_by_tag.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tag" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" name="Task Count">
                  {analytics.tasks_by_tag.slice(0, 10).map((_, index) => (
                    <Cell key={`cell-${index}`} fill={TAG_COLORS[index % TAG_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>
    </div>
  )
}

// ============================================================================
// Helper Components
// ============================================================================

interface MetricCardProps {
  title: string
  value: string | number
  icon: string
}

function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl" role="img" aria-label={title}>
          {icon}
        </span>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

interface ChartCardProps {
  title: string
  description: string
  children: React.ReactNode
}

function ChartCard({ title, description, children }: ChartCardProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      {children}
    </div>
  )
}
