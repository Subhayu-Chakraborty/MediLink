/**
 * src/hooks/useReportUpload.ts
 * ────────────────────────────
 * Custom hook encapsulating the medical report file upload flow.
 * Manages upload state: loading, error, and success data.
 *
 * // TODO: Implement in Phase 1
 */

import { useState } from 'react'
import type { ReportUploadResponse } from '../types/report.types'

interface UseReportUploadState {
  isUploading: boolean
  error: string | null
  uploadedReport: ReportUploadResponse | null
}

interface UseReportUploadActions {
  uploadReport: (file: File) => Promise<void>
  reset: () => void
}

type UseReportUploadReturn = UseReportUploadState & UseReportUploadActions

// TODO: Implement in Phase 1
export function useReportUpload(): UseReportUploadReturn {
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [uploadedReport, setUploadedReport] = useState<ReportUploadResponse | null>(null)

  const uploadReport = async (_file: File): Promise<void> => {
    // TODO: Implement in Phase 1 — call reportService.uploadReport(file)
    void _file
  }

  const reset = (): void => {
    setIsUploading(false)
    setError(null)
    setUploadedReport(null)
  }

  return { isUploading, error, uploadedReport, uploadReport, reset }
}
