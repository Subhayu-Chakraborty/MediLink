/**
 * src/pages/doctor/DoctorDashboard.tsx
 * Full doctor dashboard: profile, requests, patient list, report viewer.
 */
import { useEffect, useState, type FC } from 'react'
import DoctorLayout from '../../layouts/DoctorLayout'
import { useAuth } from '../../hooks/useAuth'
import {
  getMyProfile,
  getPendingRequests,
  respondToRequest,
  getMyPatients,
  updateMyProfile,
} from '../../services/doctorService'
import type { DoctorProfile, PatientRequestItem, PatientSummary } from '../../types/doctor.types'
import RequestCard from '../../components/doctor/RequestCard'
import PatientList from '../../components/doctor/PatientList'
import PatientReportView from '../../components/doctor/PatientReportView'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import ChatWindow from '../../components/common/ChatWindow'

const DoctorDashboard: FC = () => {
  const { user } = useAuth()
  const [profile, setProfile] = useState<DoctorProfile | null>(null)
  const [requests, setRequests] = useState<PatientRequestItem[]>([])
  const [patients, setPatients] = useState<PatientSummary[]>([])
  const [selectedPatient, setSelectedPatient] = useState<PatientSummary | null>(null)
  const [loadingInit, setLoadingInit] = useState(true)
  const [respondingId, setRespondingId] = useState<string | null>(null)
  const [savingLocation, setSavingLocation] = useState(false)
  const [locationMessage, setLocationMessage] = useState('')
  const [activeTab, setActiveTab] = useState<'overview' | 'requests' | 'patients'>('overview')

  const loadData = async () => {
    try {
      const [prof, reqs, pts] = await Promise.all([
        getMyProfile(),
        getPendingRequests(),
        getMyPatients(),
      ])
      setProfile(prof)
      setRequests(reqs)
      setPatients(pts)
    } catch { /* ignore */ }
    finally { setLoadingInit(false) }
  }

  useEffect(() => { loadData() }, [])

  const handleRespond = async (requestId: string, accept: boolean) => {
    setRespondingId(requestId)
    try {
      await respondToRequest(requestId, accept)
      await loadData()  // refresh
    } catch { /* ignore */ }
    finally { setRespondingId(null) }
  }

  const handleSaveCurrentLocation = () => {
    setLocationMessage('')
    if (!('geolocation' in navigator)) {
      setLocationMessage('Location services are not available in this browser.')
      return
    }

    setSavingLocation(true)
    navigator.geolocation.getCurrentPosition(
      async position => {
        try {
          const { latitude, longitude } = position.coords
          const updated = await updateMyProfile({ latitude, longitude })
          setProfile(updated)
          setLocationMessage('Practice location saved.')
        } catch {
          setLocationMessage('Unable to save location.')
        } finally {
          setSavingLocation(false)
        }
      },
      () => {
        setLocationMessage('Allow location access to save your practice location.')
        setSavingLocation(false)
      },
      { enableHighAccuracy: true, timeout: 10000 },
    )
  }

  if (loadingInit) return (
    <DoctorLayout>
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" label="Loading dashboard…" />
      </div>
    </DoctorLayout>
  )

  return (
    <DoctorLayout>
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-800">
            Dr. {user?.full_name?.split(' ').slice(-1)[0]} 🩺
          </h1>
          {profile && (
            <div className="flex items-center gap-3 mt-1">
              <span className="badge bg-blue-50 text-blue-700 font-mono">{profile.doctor_id}</span>
              <span className="text-sm text-slate-500">{profile.specialization}</span>
              {profile.hospital && <span className="text-sm text-slate-400">· {profile.hospital}</span>}
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          {[
            { label: 'Connected Patients', value: patients.length, color: 'emerald' },
            { label: 'Pending Requests', value: requests.length, color: 'amber' },
            { label: 'Experience', value: profile ? `${profile.experience}y` : '—', color: 'blue' },
          ].map(s => (
            <div key={s.label} className="card text-center py-4">
              <p className={`text-2xl font-bold text-${s.color}-600`}>{s.value}</p>
              <p className="text-xs text-slate-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-slate-100 p-1 rounded-lg mb-5 w-fit">
          {(['overview', 'requests', 'patients'] as const).map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-all relative
                ${activeTab === tab ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>
              {tab}
              {tab === 'requests' && requests.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center">
                  {requests.length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* ── OVERVIEW TAB ── */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* Profile */}
            <div className="lg:col-span-1">
              <div className="card">
                <h3 className="font-semibold text-slate-800 mb-4">My Profile</h3>
                {profile && (
                  <div className="flex flex-col gap-2 text-sm">
                    <Row label="Name" value={profile.full_name} />
                    <Row label="Email" value={profile.email} />
                    <Row label="Doctor ID" value={profile.doctor_id} />
                    <Row label="Specialization" value={profile.specialization} />
                    <Row label="Experience" value={`${profile.experience} years`} />
                    {profile.hospital && <Row label="Hospital" value={profile.hospital} />}
                    {profile.phone && <Row label="Phone" value={profile.phone} />}
                  </div>
                )}
                <div className="mt-4 pt-3 border-t border-slate-200">
                  <p className="text-xs text-slate-400">
                    Share your Doctor ID (<strong className="font-mono text-blue-600">{profile?.doctor_id}</strong>) with patients so they can connect with you.
                  </p>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-200">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-slate-700">Practice location</p>
                      <p className="text-xs text-slate-400">
                        {profile?.latitude && profile?.longitude
                          ? `${profile.latitude.toFixed(4)}, ${profile.longitude.toFixed(4)}`
                          : 'No GPS location saved'}
                      </p>
                    </div>
                    <button
                      onClick={handleSaveCurrentLocation}
                      disabled={savingLocation}
                      className="btn-secondary btn-sm shrink-0"
                    >
                      {savingLocation ? <LoadingSpinner size="sm" /> : 'Use GPS'}
                    </button>
                  </div>
                  {locationMessage && <p className="text-xs text-slate-500 mt-2">{locationMessage}</p>}
                </div>
              </div>
            </div>

            {/* Recent requests + patients */}
            <div className="lg:col-span-2 flex flex-col gap-4">
              {/* Pending requests preview */}
              {requests.length > 0 && (
                <div className="card">
                  <div className="section-header">
                    <h3 className="font-semibold text-slate-800">Pending Requests</h3>
                    <button onClick={() => setActiveTab('requests')} className="text-xs text-blue-600 hover:underline">
                      View all
                    </button>
                  </div>
                  <div className="flex flex-col gap-2">
                    {requests.slice(0, 2).map(r => (
                      <RequestCard key={r.request_id} request={r}
                        onAccept={id => handleRespond(id, true)}
                        onReject={id => handleRespond(id, false)}
                        loading={respondingId === r.request_id} />
                    ))}
                  </div>
                </div>
              )}

              {/* Patient list preview */}
              <div className="card">
                <div className="section-header">
                  <h3 className="font-semibold text-slate-800">My Patients</h3>
                  <button onClick={() => setActiveTab('patients')} className="text-xs text-blue-600 hover:underline">
                    View all
                  </button>
                </div>
                <PatientList
                  patients={patients.slice(0, 4)}
                  selectedId={selectedPatient?.user_id}
                  onSelect={id => {
                    const p = patients.find(pt => pt.user_id === id)
                    setSelectedPatient(p ?? null)
                    setActiveTab('patients')
                  }}
                />
              </div>
            </div>
          </div>
        )}

        {/* ── REQUESTS TAB ── */}
        {activeTab === 'requests' && (
          <div className="card">
            <h3 className="font-semibold text-slate-800 mb-4">
              Patient Requests ({requests.length})
            </h3>
            {requests.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No pending requests.</p>
            ) : (
              <div className="flex flex-col gap-3">
                {requests.map(r => (
                  <RequestCard key={r.request_id} request={r}
                    onAccept={id => handleRespond(id, true)}
                    onReject={id => handleRespond(id, false)}
                    loading={respondingId === r.request_id} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── PATIENTS TAB ── */}
        {activeTab === 'patients' && (
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
            <div className="lg:col-span-2 card">
              <h3 className="font-semibold text-slate-800 mb-3">Connected Patients</h3>
              <PatientList
                patients={patients}
                selectedId={selectedPatient?.user_id}
                onSelect={id => {
                  const p = patients.find(pt => pt.user_id === id)
                  setSelectedPatient(p ?? null)
                }}
              />
            </div>
            <div className="lg:col-span-3 card">
              {selectedPatient ? (
                <div className="flex flex-col gap-4">
                  <PatientReportView
                    patientId={selectedPatient.user_id}
                    patientName={selectedPatient.full_name}
                  />
                  <ChatWindow
                    receiverId={selectedPatient.user_id}
                    receiverName={selectedPatient.full_name}
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-40 text-slate-400 text-sm">
                  Select a patient to view their reports.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </DoctorLayout>
  )
}

const Row: FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between gap-2">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-700 text-right break-all">{value}</span>
  </div>
)

export default DoctorDashboard
