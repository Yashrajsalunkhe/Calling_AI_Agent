import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './pages/Dashboard'
import Landing from './pages/Landing'
import Settings from './pages/Settings'
import Agents from './pages/Agents'
import MockCall from './pages/MockCall'
import { getProviderStatus } from './api/client'

function App() {
  const location = useLocation()
  const [providerInfo, setProviderInfo] = useState(null)

  useEffect(() => {
    getProviderStatus()
      .then(setProviderInfo)
      .catch(() => {})
  }, [location.pathname])

  const activeProvider = providerInfo?.active_provider || '...'

  if (location.pathname === '/') {
    return <Landing />
  }

  return (
    <div className="app-layout">
      {/* ── Sidebar ─────────────────────────────────────────────────── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-logo">✦</div>
            <div>
              <div className="sidebar-title">AI Call Agent</div>
              <div className="sidebar-subtitle">LLM Provider Hub</div>
            </div>
          </div>
        </div>

        <div className="sidebar-profile">
          <div className="profile-avatar">YA</div>
          <div>
            <div className="profile-name">Yashraj</div>
            <div className="profile-email">AI workspace</div>
          </div>
          <span className="profile-menu">•••</span>
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-section-title">Overview</div>
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">📊</span>
            Dashboard
          </NavLink>

          <div className="sidebar-section-title">AI Engine</div>
          <NavLink to="/settings/ai" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">⚙️</span>
            LLM Settings
          </NavLink>
          <NavLink to="/agents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">🤖</span>
            Agents
          </NavLink>

          <div className="sidebar-section-title">Testing</div>
          <NavLink to="/mock-call" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">💬</span>
            Mock Call
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status">
            <span className={`status-dot ${providerInfo?.providers?.[0]?.status || 'unknown'}`}></span>
            Active: {activeProvider}
          </div>
        </div>
      </aside>

      {/* ── Main Content ────────────────────────────────────────────── */}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings/ai" element={<Settings />} />
          <Route path="/agents" element={<Agents />} />
          <Route path="/mock-call" element={<MockCall />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
