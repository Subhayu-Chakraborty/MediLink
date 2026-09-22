/**
 * src/components/doctor/PatientReportView.tsx
 * View a connected patient's reports and analysis results.
 */
import { useEffect, useState, type FC } from 'react'
import { getPatientReports, getPatientReport } from '../../services/doctorService'
import { getAnalysis } from '../../services/reportService'
import type { ReportListItem, ReportDetail, AnalysisResult } from '../../types/report.types'
import LoadingSpinner from '../common/LoadingSpinner'
import AnalysisSummary from '../patient/AnalysisSummary'

interface PatientReportViewProps {
  patientId: string
  patientName: string
}

const PatientReportView: FC<PatientReportViewProps> = ({ patientId, patientName }) => {
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedReport, setSelectedReport] = useState<ReportDetail | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)

  useEffect(() => {
    setLoading(true)
    getPatientReports(patientId)
      .then(setReports)
      .catch(() => setReports([]))
      .finally(() => setLoading(false))
  }, [patientId])

  const handleSelectReport = async (report: ReportListItem) => {
    setLoadingDetail(true)
    setSelectedReport(null)
    setAnalysis(null)
    try {
      const detail = await getPatientReport(patientId, report.id)
      setSelectedReport(detail)
      if (detail.has_analysis) {
        const result = await getAnalysis(report.id)
        setAnalysis(result)
      }
    } catch { /* ignore */ }
    finally { setLoadingDetail(false) }
  }

  if (loading) return <div className="py-8 flex justify-center"><LoadingSpinner label="Loading reports…" /></div>

  return (
    <div>
      <h3 className="font-semibold text-slate-800 mb-3">Reports for {patientName}</h3>

      {reports.length === 0 ? (
        <p className="text-sm text-slate-400">This patient has not uploaded any reports yet.</p>
      ) : (
        <div className="flex flex-col gap-2 mb-5">
          {reports.map(r => (
            <button key={r.id} onClick={() => handleSelectReport(r)}
              className={`text-left p-3 rounded-lg border text-sm transition-all
                ${selectedReport?.id === r.id ? 'border-blue-400 bg-blue-50' : 'border-slate-200 hover:border-slate-300 bg-white'}`}>
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-700 truncate">{r.original_filename}</span>
                <span className={`badge ${r.status === 'analyzed' ? 'badge-analyzed' : r.status === 'failed' ? 'badge-failed' : 'badge-uploaded'} ml-2 shrink-0`}>
                  {r.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{new Date(r.uploaded_at).toLocaleString()}</p>
            </button>
          ))}
        </div>
      )}

      {loadingDetail && <div className="py-4 flex justify-center"><LoadingSpinner label="Loading report…" /></div>}

      {analysis && <AnalysisSummary analysis={analysis} />}

      {selectedReport && !analysis && !loadingDetail && (
        <div className="card">
          <p className="text-sm text-slate-500">This report has not been analysed yet.</p>
          {selectedReport.extracted_text && (
            <details className="mt-3">
              <summary className="text-xs text-blue-600 cursor-pointer">View extracted text</summary>
              <pre className="mt-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg overflow-auto max-h-60 whitespace-pre-wrap">
                {selectedReport.extracted_text}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  )
}

export default PatientReportView
