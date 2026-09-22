/**
 * src/components/patient/ParameterTable.tsx
 * Table of extracted medical parameters with color-coded status.
 */
import type { FC } from 'react'
import type { MedicalParameter } from '../../types/report.types'

interface ParameterTableProps {
  parameters: MedicalParameter[]
}

const statusCls: Record<string, string> = {
  Normal:   'param-normal',
  Low:      'param-low',
  High:     'param-high',
  Critical: 'param-critical',
}

const statusBadgeCls: Record<string, string> = {
  Normal:   'badge bg-emerald-100 text-emerald-700',
  Low:      'badge bg-blue-100 text-blue-700',
  High:     'badge bg-orange-100 text-orange-700',
  Critical: 'badge bg-red-100 text-red-700',
}

const ParameterTable: FC<ParameterTableProps> = ({ parameters }) => {
  if (parameters.length === 0) {
    return (
      <div className="text-sm text-slate-400 italic py-4 text-center">
        No parameters were extracted from this report.
      </div>
    )
  }

  const abnormal = parameters.filter(p => p.status !== 'Normal')
  const normal   = parameters.filter(p => p.status === 'Normal')

  return (
    <div>
      {abnormal.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold text-orange-600 uppercase tracking-wide mb-2">
            ⚠ Abnormal Values ({abnormal.length})
          </p>
          <ParameterRows params={abnormal} />
        </div>
      )}
      {normal.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wide mb-2">
            ✓ Normal Values ({normal.length})
          </p>
          <ParameterRows params={normal} />
        </div>
      )}
    </div>
  )
}

const ParameterRows: FC<{ params: MedicalParameter[] }> = ({ params }) => (
  <div className="overflow-x-auto rounded-lg border border-slate-200">
    <table className="w-full text-sm">
      <thead>
        <tr className="bg-slate-50 border-b border-slate-200">
          <th className="text-left py-2 px-3 font-medium text-slate-600 text-xs">Parameter</th>
          <th className="text-right py-2 px-3 font-medium text-slate-600 text-xs">Value</th>
          <th className="text-left py-2 px-3 font-medium text-slate-600 text-xs">Reference</th>
          <th className="text-center py-2 px-3 font-medium text-slate-600 text-xs">Status</th>
        </tr>
      </thead>
      <tbody>
        {params.map((p, i) => (
          <tr key={i} className="border-b border-slate-100 last:border-0">
            <td className="py-2 px-3 font-medium text-slate-700">{p.name}</td>
            <td className={`py-2 px-3 text-right font-mono ${statusCls[p.status] ?? ''}`}>
              {p.value} <span className="text-slate-400 font-sans text-xs">{p.unit}</span>
            </td>
            <td className="py-2 px-3 text-slate-400 text-xs">{p.reference_range || '—'}</td>
            <td className="py-2 px-3 text-center">
              <span className={statusBadgeCls[p.status] ?? 'badge bg-slate-100 text-slate-600'}>
                {p.status}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)

export default ParameterTable
