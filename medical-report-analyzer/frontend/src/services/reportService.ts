/**
 * src/services/reportService.ts
 * Report API calls: upload, list, detail, analysis.
 */
import api from './api'
import type { ReportUploadResponse, ReportListItem, ReportDetail, AnalysisResult } from '../types/report.types'

export async function uploadReport(file: File): Promise<ReportUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const res = await api.post<ReportUploadResponse>('/reports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function listMyReports(): Promise<ReportListItem[]> {
  const res = await api.get<ReportListItem[]>('/reports/list')
  return res.data
}

export async function getReport(reportId: string): Promise<ReportDetail> {
  const res = await api.get<ReportDetail>(`/reports/${reportId}`)
  return res.data
}

export async function triggerAnalysis(reportId: string): Promise<{ report_id: string; status: string; message: string }> {
  const res = await api.post(`/analysis/${reportId}`)
  return res.data
}

export async function getAnalysis(reportId: string): Promise<AnalysisResult> {
  const res = await api.get<AnalysisResult>(`/analysis/${reportId}`)
  return res.data
}
