import { useEffect, useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import MainLayout from './components/MainLayout'
import PlaceholderPage from './pages/PlaceholderPage'
import DatabaseConnections from './pages/DatabaseConnections'
import MenuProfiles from './pages/MenuProfiles'
import MenuItems from './pages/MenuItems'
import Customers from './pages/Customers'
import CustomerDetail from './pages/CustomerDetail'
import { MenuProvider } from './store/MenuContext'

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
    <MenuProvider>
      <Routes>
        <Route path="/" element={<MainLayout onLogout={handleLogout} />}>
          {/* Default redirect to Monitoring › Notifications */}
          <Route index element={<Navigate to="/monitoring/notifications" replace />} />

          {/* Configuration — Database Connections */}
          <Route path="configuration/database-connections" element={<DatabaseConnections />} />

          {/* Configuration — Menu Profiles */}
          <Route path="configuration/menu-profiles" element={<MenuProfiles />} />

          {/* Configuration — Menu Items */}
          <Route path="configuration/menu-items" element={<MenuItems />} />

          {/* Customer Management — Phase 05 */}
          <Route path="customers" element={<Customers />} />
          <Route path="customers/:id" element={<CustomerDetail />} />

          {/* All sections render the placeholder until each page is implemented */}
          <Route path="*" element={<PlaceholderPage />} />
        </Route>
      </Routes>
    </MenuProvider>
  )
}
