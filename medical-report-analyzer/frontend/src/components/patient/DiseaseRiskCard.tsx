/**
 * src/components/patient/DiseaseRiskCard.tsx
 * Visual risk level card for a single disease.
 */
import type { FC } from 'react'
import type { DiseaseRiskItem, RiskLevel } from '../../types/report.types'

interface DiseaseRiskCardProps {
  disease: string
  risk: DiseaseRiskItem
  icon: string
}

const riskConfig: Record<RiskLevel, { cls: string; bar: string; dot: string }> = {
  'Low Risk':          { cls: 'border-emerald-200 bg-emerald-50', bar: 'bg-emerald-500 w-1/4',  dot: 'bg-emerald-500' },
  'Moderate Risk':     { cls: 'border-amber-200 bg-amber-50',    bar: 'bg-amber-500 w-2/4',    dot: 'bg-amber-500' },
  'High Risk':         { cls: 'border-orange-200 bg-orange-50',  bar: 'bg-orange-500 w-3/4',   dot: 'bg-orange-500' },
  'Insufficient Data': { cls: 'border-slate-200 bg-slate-50',    bar: 'bg-slate-400 w-0',       dot: 'bg-slate-400' },
}

const DiseaseRiskCard: FC<DiseaseRiskCardProps> = ({ disease, risk, icon }) => {
  const cfg = riskConfig[risk.level] ?? riskConfig['Insufficient Data']
  return (
    <div className={`rounded-xl border-2 p-4 flex flex-col gap-3 ${cfg.cls}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <span className="font-semibold text-slate-800 text-sm">{disease}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full ${cfg.dot}`}/>
          <span className="text-xs font-medium text-slate-700">{risk.level}</span>
        </div>
      </div>

      {/* Risk bar */}
      <div className="h-1.5 bg-white/70 rounded-full overflow-hidden">
        <div className={`h-full rounded-full transition-all ${cfg.bar}`}/>
      </div>

      {/* Reason */}
      <p className="text-xs text-slate-600 leading-relaxed">{risk.reason}</p>
    </div>
  )
}

export default DiseaseRiskCard
