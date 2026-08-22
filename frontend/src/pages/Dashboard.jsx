import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getProviderStatus, getAgents } from '../api/client'

export default function Dashboard() {
  const [providers, setProviders] = useState(null)
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getProviderStatus().catch(() => null),
      getAgents().catch(() => []),
    ]).then(([prov, ag]) => {
      setProviders(prov)
      setAgents(ag)
      setLoading(false)
    })
  }, [])

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-description">AI Calling Agent overview</p>
        </div>
        <div className="page-content" style={{ display: 'flex', justifyContent: 'center', paddingTop: '60px' }}>
          <div className="spinner"></div>
        </div>
      </>
    )
  }

  const activeProvider = providers?.active_provider || 'N/A'
  const providerList = providers?.providers || []

  return (
    <>
      <div className="page-header">
        <div className="dashboard-heading-row">
          <div>
            <div className="dashboard-kicker">CONTROL ROOM / 01</div>
            <h1 className="page-title">Dashboard</h1>
            <p className="page-description">AI Calling Agent / System Overview</p>
          </div>
          <Link className="btn btn-primary dashboard-call-button" to="/mock-call">☎ Start a call</Link>
        </div>
      </div>

      <div className="page-content animate-fade-in">
        <section className="dashboard-hero">
          <div className="hero-grid-lines" aria-hidden="true"></div>
          <div className="hero-copy">
            <div className="hero-status"><span className="hero-status-dot"></span> VOICE NETWORK ONLINE</div>
            <h2>Calls in. <span>Answers out.</span></h2>
            <p>Your AI calling team is ready to listen, reason, and respond in real time.</p>
            <div className="hero-chips">
              <span>01 / LIVE AGENT</span>
              <span>02 / LOW LATENCY</span>
              <span>03 / HUMAN HANDOFF</span>
            </div>
          </div>
          <div className="robot-stage" aria-label="Animated AI calling agent">
            <div className="signal signal-one"></div>
            <div className="signal signal-two"></div>
            <div className="signal signal-three"></div>
            <div className="call-orb orb-one">☎</div>
            <div className="call-orb orb-two">•••</div>
            <div className="robot-antenna"></div>
            <div className="robot-head">
              <div className="robot-eye"></div>
              <div className="robot-eye"></div>
              <div className="robot-mouth"><i></i><i></i><i></i></div>
            </div>
            <div className="robot-neck"></div>
            <div className="robot-body">
              <div className="robot-screen">AI<br /><small>READY</small></div>
              <div className="robot-speaker"></div>
            </div>
            <div className="robot-arm robot-arm-left"></div>
            <div className="robot-arm robot-arm-right"></div>
            <div className="robot-hand robot-hand-left">✦</div>
            <div className="robot-hand robot-hand-right">◌</div>
            <div className="robot-leg robot-leg-left"></div>
            <div className="robot-leg robot-leg-right"></div>
          </div>
        </section>

        {/* ── Stats ─────────────────────────────────────────────────── */}
        <div className="stats-grid">
          <div className="glass-card stat-card stat-card-blue">
            <div className="stat-value">{activeProvider}</div>
            <div className="stat-label">Active Provider</div>
          </div>
          <div className="glass-card stat-card stat-card-yellow">
            <div className="stat-value">{agents.length}</div>
            <div className="stat-label">Agents</div>
          </div>
          <div className="glass-card stat-card stat-card-green">
            <div className="stat-value">{providerList.filter(p => p.status === 'connected').length}</div>
            <div className="stat-label">Providers Online</div>
          </div>
          <div className="glass-card stat-card stat-card-pink">
            <div className="stat-value">v1.0</div>
            <div className="stat-label">Version</div>
          </div>
        </div>

        {/* ── Provider Status Cards ─────────────────────────────────── */}
        <h2 className="section-heading">
          AI Providers
        </h2>
        <div className="provider-cards">
          {providerList.map(p => (
            <div
              key={p.provider}
              className="glass-card provider-card"
              style={{ '--provider-color': p.provider === 'ollama' ? 'var(--ollama-primary)' : 'var(--gemini-primary)' }}
            >
              <div className="provider-card-header">
                <span className="provider-name">
                  {p.provider === 'ollama' ? '🦙' : '✨'} {p.provider.charAt(0).toUpperCase() + p.provider.slice(1)}
                </span>
                {activeProvider === p.provider && (
                  <span className="provider-badge active">● Active</span>
                )}
              </div>

              <div className="provider-detail">
                <span className="provider-detail-label">Status</span>
                <span className="provider-detail-value">
                  <span className={`status-dot ${p.status}`}></span>
                  {p.status.replace('_', ' ')}
                </span>
              </div>

              <div className="provider-detail">
                <span className="provider-detail-label">Model</span>
                <span className="provider-detail-value" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                  {p.model || 'N/A'}
                </span>
              </div>

              {p.latency_ms > 0 && (
                <div className="provider-detail">
                  <span className="provider-detail-label">Latency</span>
                  <span className="provider-detail-value">{p.latency_ms}ms</span>
                </div>
              )}

              {p.message && (
                <div className="provider-detail" style={{ borderBottom: 'none' }}>
                  <span className="provider-detail-label" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {p.message}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* ── Active Agents ─────────────────────────────────────────── */}
        {agents.length > 0 && (
          <>
            <h2 className="section-heading agents-heading">
              Active Agents
            </h2>
            <div className="agents-grid">
              {agents.slice(0, 4).map(agent => (
                <div key={agent.id} className="glass-card agent-card">
                  <div className="agent-card-header">
                    <span className="agent-name">{agent.name}</span>
                    <span className={`agent-active-badge ${agent.is_active ? 'active' : 'inactive'}`}>
                      {agent.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div className="agent-details">
                    <div className="agent-detail">
                      <span className="agent-detail-label">Provider</span>
                      <span className="agent-detail-value">{agent.llm_provider || 'Global'}</span>
                    </div>
                    <div className="agent-detail">
                      <span className="agent-detail-label">Language</span>
                      <span className="agent-detail-value">{agent.language}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </>
  )
}
