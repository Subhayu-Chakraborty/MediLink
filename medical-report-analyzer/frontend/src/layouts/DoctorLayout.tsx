/**
 * src/layouts/DoctorLayout.tsx
 * Dashboard layout for doctor pages.
 */
import type { FC, ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import Navbar from '../components/common/Navbar'

const NAV = [
  { label: 'Dashboard', path: '/doctor/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
]

interface DoctorLayoutProps { children: ReactNode }

const DoctorLayout: FC<DoctorLayoutProps> = ({ children }) => (
  <div className="min-h-screen flex flex-col">
    <Navbar />
    <div className="flex flex-1">
      <aside className="hidden md:flex flex-col w-56 bg-white border-r border-slate-200 p-4 shrink-0">
        <nav className="flex flex-col gap-1">
          {NAV.map(item => (
            <NavLink key={item.path} to={item.path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon}/>
              </svg>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-4 md:p-6 overflow-auto">{children}</main>
    </div>
  </div>
)

export default DoctorLayout
