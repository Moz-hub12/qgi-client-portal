import React from 'react'
import { NavLink } from 'react-router-dom'
// Optimized icon imports for tree-shaking
import LayoutGrid from 'lucide-react/dist/esm/icons/layout-grid'
import Users from 'lucide-react/dist/esm/icons/users'
import ShieldCheck from 'lucide-react/dist/esm/icons/shield-check'
import BarChart3 from 'lucide-react/dist/esm/icons/bar-chart-3'

// If you want to show the logged-in admin or add a logout button,
// you can import your auth hook:
// import { useAdminAuth } from '../App'

export default function AdminLayout({ children }) {
  // const { admin, logout } = useAdminAuth()

  const nav = [
    { label: 'Dashboard', to: '/dashboard', icon: LayoutGrid },
    { label: 'Clients',   to: '/clients',   icon: Users },
    { label: 'Compliance',to: '/compliance',icon: ShieldCheck },
    { label: 'Reports',   to: '/reports',   icon: BarChart3 },
  ]

  const linkBase =
    'flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition'
  const linkInactive = 'text-slate-600 hover:bg-slate-100'
  const linkActive   = 'bg-slate-900 text-white hover:bg-slate-900'

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-white text-slate-900">
      <div className="flex">
        {/* Sidebar */}
        <aside className="hidden md:flex md:flex-col w-64 shrink-0 border-r bg-white">
          <div className="h-16 flex items-center px-6 border-b">
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600" />
              <span className="tracking-wide font-semibold">Quantum Growth</span>
            </div>
          </div>
          <nav className="p-3 space-y-1">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `${linkBase} ${isActive ? linkActive : linkInactive}`
                }
                end={n.to === '/dashboard'}
              >
                <n.icon className="h-4 w-4" />
                {n.label}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto p-4 text-xs text-slate-400">
            © {new Date().getFullYear()} QGI
          </div>
        </aside>

        {/* Main */}
        <main className="flex-1 min-h-screen">
          {/* Topbar */}
          <div className="h-16 border-b bg-white sticky top-0 z-10">
            <div className="h-full px-4 md:px-8 flex items-center justify-between">
              <h1 className="text-xl md:text-2xl font-semibold tracking-tight">Admin</h1>
              <div className="flex items-center gap-3">
                {/* Example slot for profile / logout
                <span className="text-sm text-slate-600">{admin?.email}</span>
                <button
                  onClick={logout}
                  className="px-3 py-1.5 text-sm rounded-xl border hover:bg-slate-50"
                >
                  Logout
                </button>
                */}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="px-4 md:px-8 py-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

