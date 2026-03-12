/**
 * Root application router.
 * - Public routes: /login
 * - Protected routes: everything else, wrapped in Layout
 * - Role guard: /admin requires admin role
 */
import { Navigate, Route, Routes } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from './store/authStore'
import { authApi } from './services/api'
import Layout from "./components/Layout/Layout";


// Pages
import LoginPage           from './pages/Login/LoginPage'
import DashboardPage       from './pages/Dashboard/DashboardPage'
import UploadPage          from './pages/Upload/UploadPage'
import RunsListPage        from './pages/RunsList/RunsListPage'
import RunDetailPage       from './pages/RunDetail/RunDetailPage'
import PipelinePage        from './pages/Pipeline/PipelinePage'
import SectionEditorPage   from './pages/SectionEditor/SectionEditorPage'
import ComplianceReviewPage from './pages/ComplianceReview/ComplianceReviewPage'
import AdminPanelPage      from './pages/AdminPanel/AdminPanelPage'
import ProfilePage         from './pages/Profile/ProfilePage'

function ProtectedRoute({ children, roles }: { children: React.ReactNode; roles?: string[] }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Force password change on first login — gate all routes except /profile
  if (user?.force_password_change) {
    const currentPath = window.location.pathname
    if (currentPath !== '/profile') {
      return <Navigate to="/profile" replace />
    }
  }

  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />
  }

  return <Layout>{children}</Layout>
}

export default function App() {
  const { setUser, isAuthenticated } = useAuthStore()

  // Re-validate session on app mount (handles page reload with existing cookie)
  useEffect(() => {
    if (!isAuthenticated) return
    authApi.me()
      .then((res) => setUser(res.data))
      .catch(() => setUser(null))
  }, [])

  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Protected — any authenticated user */}
      <Route path="/dashboard" element={
        <ProtectedRoute><DashboardPage /></ProtectedRoute>
      } />
      <Route path="/upload" element={
        <ProtectedRoute><UploadPage /></ProtectedRoute>
      } />
      <Route path="/runs" element={
        <ProtectedRoute><RunsListPage /></ProtectedRoute>
      } />
      <Route path="/runs/:runId" element={
        <ProtectedRoute><RunDetailPage /></ProtectedRoute>
      } />
      <Route path="/runs/:runId/pipeline" element={
        <ProtectedRoute><PipelinePage /></ProtectedRoute>
      } />
      <Route path="/runs/:runId/sections/:sectionNumber" element={
        <ProtectedRoute><SectionEditorPage /></ProtectedRoute>
      } />
      <Route path="/runs/:runId/compliance" element={
        <ProtectedRoute roles={['reviewer', 'admin']}><ComplianceReviewPage /></ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute><ProfilePage /></ProtectedRoute>
      } />

      {/* Admin only */}
      <Route path="/admin" element={
        <ProtectedRoute roles={['admin']}><AdminPanelPage /></ProtectedRoute>
      } />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}
