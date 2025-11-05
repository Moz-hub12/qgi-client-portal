import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect, createContext, useContext } from 'react'
import { API_BASE_URL } from './config'

// 🔐 Centralized auth storage helpers
import {
  getToken as getStoredToken,
  setToken as storeToken,
  clearToken as wipeToken,
  setAdminUser as storeAdminUser, // optional but handy
} from './lib/authStorage'

// Pages & layout - import at top to avoid hoisting issues
import AdminLoginPage from './pages/AdminLoginPage'
import DashboardV2 from './pages/DashboardV2'
import ClientsPage from './pages/ClientsPage'
import ClientDetailPage from './pages/ClientDetailPage'
import CompliancePage from './pages/CompliancePage'
import ReportsPage from './pages/ReportsPage'
import AdminLayout from './components/AdminLayout'

// Context for admin authentication
const AdminAuthContext = createContext(null)

// Admin auth provider component
function AdminAuthProvider({ children }) {
  const [admin, setAdmin] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(getStoredToken())

  useEffect(() => {
    // Check if admin is authenticated on app load or when token changes
    if (token) {
      fetchCurrentAdmin()
    } else {
      setAdmin(null)
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  const fetchCurrentAdmin = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/admin/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (response.ok) {
        const data = await response.json()
        setAdmin(data.admin)
        // optional: keep a cached copy of the admin in storage for quick reads
        if (data.admin) storeAdminUser(data.admin)
      } else {
        // Token invalid/expired → clear and reset state
        wipeToken()
        setToken(null)
        setAdmin(null)
      }
    } catch (error) {
      console.error('Failed to fetch current admin:', error)
      wipeToken()
      setToken(null)
      setAdmin(null)
    } finally {
      setLoading(false)
    }
  }

  const login = (newToken, adminData) => {
    // Save & set both token and admin
    storeToken(newToken)
    setToken(newToken)
    setAdmin(adminData || null)
    if (adminData) storeAdminUser(adminData)
  }

  const logout = async () => {
    try {
      await fetch(`${API_BASE_URL}/api/admin/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
    } catch (error) {
      console.error('Logout error (ignored):', error)
    } finally {
      wipeToken()
      setToken(null)
      setAdmin(null)
    }
  }

  return (
    <AdminAuthContext.Provider value={{ admin, login, logout, loading, token }}>
      {children}
    </AdminAuthContext.Provider>
  )
}

// Hook to use admin auth context
export const useAdminAuth = () => {
  const ctx = useContext(AdminAuthContext)
  if (!ctx) throw new Error('useAdminAuth must be used within an AdminAuthProvider')
  return ctx
}

// Protected route wrapper
function AdminProtectedRoute({ children }) {
  const { admin, loading } = useAdminAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-muted-foreground border-t-transparent" />
      </div>
    )
  }

  if (!admin) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <AdminAuthProvider>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            {/* Public */}
            <Route path="/login" element={<AdminLoginPage />} />

            {/* Protected */}
            <Route
              path="/"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <DashboardV2 />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />

            <Route
              path="/dashboard"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <DashboardV2 />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />

            <Route
              path="/clients"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <ClientsPage />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />

            <Route
              path="/clients/:clientId"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <ClientDetailPage />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />
            <Route
              path="/compliance"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <CompliancePage />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />
            
            <Route
              path="/reports"
              element={
                <AdminProtectedRoute>
                  <AdminLayout>
                    <ReportsPage />
                  </AdminLayout>
                </AdminProtectedRoute>
              }
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AdminAuthProvider>
  )
}
