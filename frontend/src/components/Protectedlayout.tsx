import { Navigate, Outlet } from 'react-router-dom'
import AppNavbar from './AppNavbar'

// Wraps every page that needs a logged-in user. One place checks for the
// token and shows the shared navbar, so individual pages don't repeat it.
export default function ProtectedLayout() {
  const token = localStorage.getItem('apnasargam_token')

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen bg-bg">
      <AppNavbar />
      <Outlet />
    </div>
  )
}
