/**
 * src/components/doctor/RequestCard.tsx
 * Single patient request with accept/reject actions.
 */
import type { FC } from 'react'
import type { PatientRequestItem } from '../../types/doctor.types'
import LoadingSpinner from '../common/LoadingSpinner'

interface RequestCardProps {
  request: PatientRequestItem
  onAccept: (id: string) => Promise<void>
  onReject: (id: string) => Promise<void>
  loading?: boolean
}

const RequestCard: FC<RequestCardProps> = ({ request, onAccept, onReject, loading }) => (
  <div className="card flex items-center gap-4">
    <div className="w-10 h-10 rounded-full bg-violet-100 text-violet-700 flex items-center justify-center font-bold shrink-0">
      {request.patient_name.charAt(0)}
    </div>
    <div className="flex-1 min-w-0">
      <p className="font-medium text-slate-800 truncate">{request.patient_name}</p>
      <p className="text-xs text-slate-400 truncate">{request.patient_email}</p>
      <p className="text-xs text-slate-400 mt-0.5">
        Requested {new Date(request.requested_at).toLocaleDateString()}
      </p>
    </div>
    <div className="flex gap-2 shrink-0">
      <button
        onClick={() => onReject(request.request_id)}
        disabled={loading}
        className="btn-secondary btn-sm text-red-600 border-red-200 hover:bg-red-50">
        Reject
      </button>
      <button
        onClick={() => onAccept(request.request_id)}
        disabled={loading}
        className="btn-success btn-sm">
        {loading ? <LoadingSpinner size="sm" /> : 'Accept'}
      </button>
    </div>
  </div>
)

export default RequestCard
