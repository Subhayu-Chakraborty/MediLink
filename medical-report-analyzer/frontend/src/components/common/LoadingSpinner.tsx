/**
 * src/components/common/LoadingSpinner.tsx
 */
import type { FC } from 'react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  fullPage?: boolean
}

const sizes = { sm: 'w-4 h-4', md: 'w-7 h-7', lg: 'w-10 h-10' }

const LoadingSpinner: FC<LoadingSpinnerProps> = ({ size = 'md', label, fullPage = false }) => {
  const spinner = (
    <div className="flex flex-col items-center gap-2">
      <svg className={`${sizes[size]} animate-spin text-blue-600`} fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      {label && <p className="text-sm text-slate-500">{label}</p>}
    </div>
  )

  if (fullPage) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-white/70 z-50">
        {spinner}
      </div>
    )
  }
  return spinner
}

export default LoadingSpinner
