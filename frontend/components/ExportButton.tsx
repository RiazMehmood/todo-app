/**
 * ExportButton Component - Reusable button for exporting analytics data
 *
 * Implements: User Story 4 (Analytics and Reporting - Export) from intermediate-advanced-features.md
 * Contract: specs/005-cloud-native-deployment/contracts/analytics-api.yaml
 *
 * Features:
 * - FR-032: Export tasks and analytics to CSV format
 * - FR-033: Export analytics reports to PDF format
 * - FR-034: Date range filtering for exports
 * - Loading state during export generation
 * - Error handling with user feedback
 */

'use client'

import { useState } from 'react'

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ExportButtonProps {
  /** User ID for the export */
  userId: string
  /** Export format */
  format: 'csv' | 'pdf'
  /** Start date for export period (YYYY-MM-DD) */
  startDate?: string
  /** End date for export period (YYYY-MM-DD) */
  endDate?: string
  /** Button label (optional, defaults based on format) */
  label?: string
  /** Button style variant */
  variant?: 'primary' | 'secondary' | 'success' | 'danger'
  /** Button size */
  size?: 'sm' | 'md' | 'lg'
  /** Callback when export completes successfully */
  onExportComplete?: () => void
  /** Callback when export fails */
  onExportError?: (error: string) => void
}

// ============================================================================
// Style Variants
// ============================================================================

const VARIANT_STYLES = {
  primary: 'bg-blue-600 hover:bg-blue-700 text-white',
  secondary: 'bg-gray-600 hover:bg-gray-700 text-white',
  success: 'bg-green-600 hover:bg-green-700 text-white',
  danger: 'bg-red-600 hover:bg-red-700 text-white'
}

const SIZE_STYLES = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg'
}

// ============================================================================
// Main Component
// ============================================================================

export default function ExportButton({
  userId,
  format,
  startDate,
  endDate,
  label,
  variant = format === 'csv' ? 'success' : 'danger',
  size = 'md',
  onExportComplete,
  onExportError
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)

  /**
   * Handle export action
   * Implements: GET /api/{user_id}/analytics/export
   */
  const handleExport = async () => {
    setIsExporting(true)

    try {
      // Build query parameters
      const params = new URLSearchParams({ format })
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)

      // Make API request
      const response = await fetch(
        `http://localhost:8000/api/${userId}/analytics/export?${params}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Export failed' }))
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
      }

      // Get filename from Content-Disposition header or generate default
      const contentDisposition = response.headers.get('Content-Disposition')
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/)
      const filename = filenameMatch
        ? filenameMatch[1]
        : `tasks_report_${endDate || new Date().toISOString().split('T')[0]}.${format}`

      // Download file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()

      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Success callback
      onExportComplete?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown export error'
      console.error('Export error:', err)
      onExportError?.(errorMessage)

      // Show user-friendly error
      alert(`Export failed: ${errorMessage}`)
    } finally {
      setIsExporting(false)
    }
  }

  // Default labels based on format
  const defaultLabel = format === 'csv' ? 'Export CSV' : 'Export PDF'
  const buttonLabel = label || defaultLabel

  // Icon based on format
  const icon = format === 'csv' ? '📊' : '📄'

  // Combine styles
  const baseStyles = 'rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 justify-center'
  const variantClass = VARIANT_STYLES[variant]
  const sizeClass = SIZE_STYLES[size]
  const className = `${baseStyles} ${variantClass} ${sizeClass}`

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className={className}
      aria-label={`Export analytics as ${format.toUpperCase()}`}
      aria-busy={isExporting}
    >
      {isExporting ? (
        <>
          <span className="animate-spin">⏳</span>
          <span>Exporting...</span>
        </>
      ) : (
        <>
          <span role="img" aria-label={format}>
            {icon}
          </span>
          <span>{buttonLabel}</span>
        </>
      )}
    </button>
  )
}

// ============================================================================
// Specialized Export Button Variants
// ============================================================================

/**
 * CSV Export Button (green variant)
 */
export function ExportCSVButton(props: Omit<ExportButtonProps, 'format'>) {
  return <ExportButton {...props} format="csv" variant="success" />
}

/**
 * PDF Export Button (red variant)
 */
export function ExportPDFButton(props: Omit<ExportButtonProps, 'format'>) {
  return <ExportButton {...props} format="pdf" variant="danger" />
}
