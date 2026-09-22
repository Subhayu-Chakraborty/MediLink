/**
 * src/components/patient/DoctorSearch.tsx
 * Search doctor by ID and send connection request.
 */
import { useState, type FC } from 'react'
import { searchDoctor } from '../../services/doctorService'
import { sendDoctorRequest } from '../../services/patientService'
import type { DoctorSearchResult } from '../../types/doctor.types'
import LoadingSpinner from '../common/LoadingSpinner'

const DoctorSearch: FC = () => {
  const [doctorId, setDoctorId] = useState('')
  const [result, setResult] = useState<DoctorSearchResult | null>(null)
  const [searching, setSearching] = useState(false)
  const [sending, setSending] = useState(false)
  const [searchError, setSearchError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  const handleSearch = async () => {
    if (!doctorId.trim()) return
    setSearching(true)
    setSearchError('')
    setResult(null)
    setSuccessMsg('')
    try {
      const data = await searchDoctor(doctorId.trim().toUpperCase())
      setResult(data)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setSearchError(msg || 'Doctor not found.')
    } finally {
      setSearching(false)
    }
  }

  const handleSendRequest = async () => {
    if (!result) return
    setSending(true)
    setSuccessMsg('')
    setSearchError('')
    try {
      const res = await sendDoctorRequest(result.doctor_id)
      setSuccessMsg(res.message)
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setSearchError(msg || 'Failed to send request.')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="card">
      <h3 className="font-semibold text-slate-800 mb-3">🔍 Find a Doctor</h3>
      <p className="text-sm text-slate-500 mb-4">Enter the doctor's unique ID to search and connect.</p>

      <div className="flex gap-2">
        <input
          type="text"
          className="form-input flex-1"
          placeholder="e.g. DR-ABC123"
          value={doctorId}
          onChange={e => setDoctorId(e.target.value.toUpperCase())}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} disabled={searching || !doctorId.trim()} className="btn-primary">
          {searching ? <LoadingSpinner size="sm" /> : 'Search'}
        </button>
      </div>

      {searchError && (
        <div className="alert-error mt-3">{searchError}</div>
      )}
      {successMsg && (
        <div className="alert-success mt-3">{successMsg}</div>
      )}

      {result && (
        <div className="mt-4 border border-slate-200 rounded-lg p-4 bg-slate-50">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
                  {result.full_name.charAt(0)}
                </div>
                <div>
                  <p className="font-semibold text-slate-800">{result.full_name}</p>
                  <p className="text-xs text-blue-600 font-mono">{result.doctor_id}</p>
                </div>
              </div>
              <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-600">
                <span className="badge bg-blue-50 text-blue-700">{result.specialization}</span>
                {result.experience > 0 && <span>{result.experience} yrs exp.</span>}
                {result.hospital && <span>📍 {result.hospital}</span>}
              </div>
            </div>
            <button onClick={handleSendRequest} disabled={sending} className="btn-primary btn-sm shrink-0">
              {sending ? <LoadingSpinner size="sm" /> : 'Send Request'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default DoctorSearch
