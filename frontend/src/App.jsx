import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import MainLayout from './components/MainLayout'
import PlaceholderPage from './pages/PlaceholderPage'

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'))

  useEffect(() => {
    const handleAutoLogout = () => setIsAuthenticated(false)
    window.addEventListener('auth:logout', handleAutoLogout)
    return () => window.removeEventListener('auth:logout', handleAutoLogout)
  }, [])

  const handleLoginSuccess = () => setIsAuthenticated(true)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    localStorage.removeItem('user')
    setIsAuthenticated(false)
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <Routes>
      <Route path="/" element={<MainLayout onLogout={handleLogout} />}>
        {/* Default redirect to Monitoring › Notifications */}
        <Route index element={<Navigate to="/monitoring/notifications" replace />} />

        {/* All sections render the placeholder until each page is implemented */}
        <Route path="*" element={<PlaceholderPage />} />
      </Route>
    </Routes>
  )
}
