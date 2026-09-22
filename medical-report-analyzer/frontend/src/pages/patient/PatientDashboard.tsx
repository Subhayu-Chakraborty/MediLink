/**
 * src/pages/patient/PatientDashboard.tsx
 * Full patient dashboard: profile, doctor connection, report upload, analysis.
 */
import { useEffect, useState, type FC } from 'react'
import PatientLayout from '../../layouts/PatientLayout'
import { useAuth } from '../../hooks/useAuth'
import { getMyProfile, getMyDoctorRequests } from '../../services/patientService'
import { listMyReports, getAnalysis } from '../../services/reportService'
import type { PatientProfile, DoctorRequestStatus } from '../../types/patient.types'
import type { ReportListItem, AnalysisResult } from '../../types/report.types'
import DoctorSearch from '../../components/patient/DoctorSearch'
import ReportUpload from '../../components/patient/ReportUpload'
import AnalysisSummary from '../../components/patient/AnalysisSummary'
import LoadingSpinner from '../../components/common/LoadingSpinner'

const PatientDashboard: FC = () => {
  const { user } = useAuth()
  const [profile, setProfile] = useState<PatientProfile | null>(null)
  const [requests, setRequests] = useState<DoctorRequestStatus[]>([])
  const [reports, setReports] = useState<ReportListItem[]>([])
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisResult | null>(null)
  const [loadingInit, setLoadingInit] = useState(true)
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const [activeTab, setActiveTab] = useState<'overview' | 'upload' | 'history'>('overview')

  const loadData = async () => {
    try {
      const [prof, reqs, reps] = await Promise.all([
        getMyProfile(),
        getMyDoctorRequests(),
        listMyReports(),
      ])
      setProfile(prof)
      setRequests(reqs)
      setReports(reps)
      // Auto-load latest analysis
      const latest = reps.find(r => r.has_analysis)
      if (latest) {
        setLoadingAnalysis(true)
        try {
          const result = await getAnalysis(latest.id)
          setSelectedAnalysis(result)
        } catch { /* ignore */ }
        setLoadingAnalysis(false)
      }
    } catch { /* ignore */ }
    finally { setLoadingInit(false) }
  }

  useEffect(() => { loadData() }, [])

  const handleUploaded = () => {
    // Reload everything after upload
    setTimeout(loadData, 1000)
    setActiveTab('overview')
  }

  const connectedDoctors = requests.filter(r => r.status === 'accepted')
  const pendingRequests  = requests.filter(r => r.status === 'pending')

  if (loadingInit) return (
    <PatientLayout>
      <div className="flex items-center justify-center h-64"><LoadingSpinner size="lg" label="Loading dashboard…" /></div>
    </PatientLayout>
  )

  return (
    <PatientLayout>
      <div className="max-w-5xl mx-auto">
        {/* Page header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800">
            Good day, {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p className="text-slate-500 text-sm mt-1">Your health overview and AI report analysis</p>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          {[
            { label: 'Reports', value: reports.length, color: 'blue' },
            { label: 'Connected Doctors', value: connectedDoctors.length, color: 'emerald' },
            { label: 'Pending Requests', value: pendingRequests.length, color: 'amber' },
          ].map(stat => (
            <div key={stat.label} className="card text-center py-4">
              <p className={`text-2xl font-bold text-${stat.color}-600`}>{stat.value}</p>
              <p className="text-xs text-slate-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-100 p-1 rounded-lg mb-5 w-fit">
          {(['overview', 'upload', 'history'] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-all
                ${activeTab === tab ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
              {tab}
            </button>
          ))}
        </div>

        {/* ── OVERVIEW TAB ── */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Left column */}
            <div className="lg:col-span-1 flex flex-col gap-4">
              {/* Profile card */}
              <div className="card">
                <h3 className="font-semibold text-slate-800 mb-3">My Profile</h3>
                {profile && (
                  <div className="flex flex-col gap-2 text-sm">
                    <Row label="Name" value={profile.full_name} />
                    <Row label="Email" value={profile.email} />
                    {profile.age && <Row label="Age" value={`${profile.age} years`} />}
                    {profile.gender && <Row label="Gender" value={profile.gender} />}
                    {profile.blood_group && <Row label="Blood Group" value={profile.blood_group} />}
                    {profile.phone && <Row label="Phone" value={profile.phone} />}
                  </div>
                )}
              </div>

              {/* Doctor connection status */}
              <div className="card">
                <h3 className="font-semibold text-slate-800 mb-3">Doctor Connections</h3>
                {connectedDoctors.length > 0 ? (
                  <div className="flex flex-col gap-2">
                    {connectedDoctors.map(r => (
                      <div key={r.request_id} className="flex items-center gap-2 text-sm">
                        <span className="badge-accepted">Connected</span>
                        <div>
                          <p className="font-medium text-slate-700">{r.doctor_name}</p>
                          <p className="text-xs text-slate-400">{r.doctor_specialization}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">No connected doctors. Search below.</p>
                )}

                {pendingRequests.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-200">
                    <p className="text-xs text-amber-600 font-medium mb-1">Pending requests:</p>
                    {pendingRequests.map(r => (
                      <div key={r.request_id} className="flex items-center gap-2 text-sm">
                        <span className="badge-pending">Pending</span>
                        <span className="text-slate-600 truncate">{r.doctor_name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Doctor search */}
              <DoctorSearch />
            </div>

            {/* Right column — analysis */}
            <div className="lg:col-span-2">
              {loadingAnalysis && (
                <div className="flex justify-center py-12"><LoadingSpinner label="Loading analysis…" /></div>
              )}
              {!loadingAnalysis && selectedAnalysis && (
                <AnalysisSummary analysis={selectedAnalysis} />
              )}
              {!loadingAnalysis && !selectedAnalysis && (
                <div className="card text-center py-12 text-slate-400">
                  <p className="text-4xl mb-3">🩺</p>
                  <p className="font-medium text-slate-600">No analysis yet</p>
                  <p className="text-sm mt-1">Upload a PDF medical report to get an AI-powered analysis.</p>
                  <button onClick={() => setActiveTab('upload')} className="btn-primary mt-4">
                    Upload Report
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── UPLOAD TAB ── */}
        {activeTab === 'upload' && (
          <div className="max-w-xl">
            <ReportUpload onUploaded={handleUploaded} />
          </div>
        )}

        {/* ── HISTORY TAB ── */}
        {activeTab === 'history' && (
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">Report History</h3>
            {reports.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No reports uploaded yet.</p>
            ) : (
              <div className="flex flex-col gap-2">
                {reports.map(r => (
                  <div key={r.id}
                    className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50 cursor-pointer"
                    onClick={async () => {
                      if (r.has_analysis) {
                        setLoadingAnalysis(true)
                        try {
                          const result = await getAnalysis(r.id)
                          setSelectedAnalysis(result)
                          setActiveTab('overview')
                        } catch { /* ignore */ }
                        setLoadingAnalysis(false)
                      }
                    }}>
                    <svg className="w-8 h-8 text-red-400 shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6ZM14 3.5 18.5 8H14V3.5Z"/>
                    </svg>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-700 text-sm truncate">{r.original_filename}</p>
                      <p className="text-xs text-slate-400">{new Date(r.uploaded_at).toLocaleString()}</p>
                    </div>
                    <span className={`badge shrink-0 ${
                      r.status === 'analyzed' ? 'badge-analyzed' :
                      r.status === 'failed'   ? 'badge-failed' : 'badge-uploaded'
                    }`}>{r.status}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </PatientLayout>
  )
}

const Row: FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between gap-2">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-700 text-right">{value}</span>
  </div>
)

export default PatientDashboard
