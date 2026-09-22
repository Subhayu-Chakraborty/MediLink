/**
 * src/layouts/AuthLayout.tsx
 * Centered card layout for login/register pages.
 */
import type { FC, ReactNode } from 'react'

interface AuthLayoutProps { children: ReactNode; title: string; subtitle?: string }

const AuthLayout: FC<AuthLayoutProps> = ({ children, title, subtitle }) => (
  <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-slate-50 flex items-center justify-center p-4">
    <div className="w-full max-w-md">
      {/* Brand header */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-600 text-white mb-4">
          <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2Zm-7 3a1 1 0 0 1 1 1v3h3a1 1 0 0 1 0 2h-3v3a1 1 0 0 1-2 0v-3H8a1 1 0 0 1 0-2h3V7a1 1 0 0 1 1-1Z"/>
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-slate-800">{title}</h1>
        {subtitle && <p className="text-slate-500 mt-1 text-sm">{subtitle}</p>}
      </div>
      <div className="card-elevated">{children}</div>
      <p className="text-center text-xs text-slate-400 mt-6">
        MedReport AI — For informational purposes only. Not a substitute for professional medical advice.
      </p>
    </div>
  </div>
)

export default AuthLayout
