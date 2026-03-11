import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import BorrowerApplication from './pages/BorrowerApplication'
import DocumentUpload from './pages/DocumentUpload'
import ApplicationStatus from './pages/ApplicationStatus'
import UnderwriterDashboard from './pages/UnderwriterDashboard'
import UnderwriterCopilot from './pages/UnderwriterCopilot'
import ComplianceDashboard from './pages/ComplianceDashboard'
import AdminSettings from './pages/AdminSettings'
import AllApplications from './pages/AllApplications'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/apply" replace />} />
          <Route path="apply" element={<BorrowerApplication />} />
          <Route path="apply/:sessionId/documents" element={<DocumentUpload />} />
          <Route path="apply/:appId/status" element={<ApplicationStatus />} />
          <Route path="applications" element={<AllApplications />} />
          <Route path="underwriter" element={<UnderwriterDashboard />} />
          <Route path="underwriter/:appId" element={<UnderwriterCopilot />} />
          <Route path="compliance" element={<ComplianceDashboard />} />
          <Route path="admin" element={<AdminSettings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
