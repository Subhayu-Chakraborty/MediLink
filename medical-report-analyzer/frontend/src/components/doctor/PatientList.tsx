/**
 * src/components/doctor/PatientList.tsx
 * List of connected patients with click to view reports.
 */
import type { FC } from 'react'
import type { PatientSummary } from '../../types/doctor.types'

interface PatientListProps {
  patients: PatientSummary[]
  onSelect: (patientId: string) => void
  selectedId?: string
}

const PatientList: FC<PatientListProps> = ({ patients, onSelect, selectedId }) => {
  if (patients.length === 0) {
    return (
      <div className="text-center text-sm text-slate-400 py-8">
        No connected patients yet. Accept patient requests to see them here.
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {patients.map(p => (
        <button
          key={p.user_id}
          onClick={() => onSelect(p.user_id)}
          className={`w-full text-left flex items-center gap-3 p-3 rounded-lg border transition-all
            ${selectedId === p.user_id
              ? 'border-blue-400 bg-blue-50'
              : 'border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50'}`}>
          <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold shrink-0">
            {p.full_name.charAt(0)}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-slate-800 text-sm truncate">{p.full_name}</p>
            <p className="text-xs text-slate-400 truncate">{p.email}</p>
          </div>
          <div className="text-right shrink-0">
            <p className="text-xs font-medium text-blue-600">{p.report_count} report{p.report_count !== 1 ? 's' : ''}</p>
            {p.age && <p className="text-xs text-slate-400">{p.age}y {p.gender ?? ''}</p>}
          </div>
        </button>
      ))}
    </div>
  )
}

export default PatientList
