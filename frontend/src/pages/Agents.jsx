import { useState, useEffect } from 'react'
import { getAgents, createAgent, updateAgent, deleteAgent } from '../api/client'

export default function Agents() {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingAgent, setEditingAgent] = useState(null)
  const [toast, setToast] = useState(null)

  const defaultForm = {
    name: '',
    description: '',
    llm_provider: '',
    llm_model: '',
    system_prompt: 'You are a helpful AI calling assistant.',
    language: 'English',
    voice: 'default',
  }
  const [form, setForm] = useState(defaultForm)

  const loadAgents = async () => {
    try {
      const data = await getAgents()
      setAgents(data)
    } catch (e) {
      showToastMsg(e.message, 'error')
    }
    setLoading(false)
  }

  useEffect(() => { loadAgents() }, [])

  const showToastMsg = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const openCreate = () => {
    setEditingAgent(null)
    setForm(defaultForm)
    setShowModal(true)
  }

  const openEdit = (agent) => {
    setEditingAgent(agent)
    setForm({
      name: agent.name,
      description: agent.description || '',
      llm_provider: agent.llm_provider || '',
      llm_model: agent.llm_model || '',
      system_prompt: agent.system_prompt,
      language: agent.language,
      voice: agent.voice,
    })
    setShowModal(true)
  }

  const handleSave = async () => {
    try {
      const payload = { ...form }
      // Send null for empty provider/model to use global
      if (!payload.llm_provider) payload.llm_provider = null
      if (!payload.llm_model) payload.llm_model = null

      if (editingAgent) {
        await updateAgent(editingAgent.id, payload)
        showToastMsg('Agent updated')
      } else {
        await createAgent(payload)
        showToastMsg('Agent created')
      }
      setShowModal(false)
      loadAgents()
    } catch (e) {
      showToastMsg(e.message, 'error')
    }
  }

  const handleDelete = async (agent) => {
    if (!confirm(`Delete agent "${agent.name}"?`)) return
    try {
      await deleteAgent(agent.id)
      showToastMsg('Agent deleted')
      loadAgents()
    } catch (e) {
      showToastMsg(e.message, 'error')
    }
  }

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1 className="page-title">Agents</h1>
        </div>
        <div className="page-content" style={{ display: 'flex', justifyContent: 'center', paddingTop: '60px' }}>
          <div className="spinner"></div>
        </div>
      </>
    )
  }

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Agents</h1>
        <p className="page-description">Manage AI agents with per-agent LLM provider selection</p>
      </div>

      <div className="page-content animate-fade-in">
        <div style={{ marginBottom: '20px' }}>
          <button className="btn btn-primary" onClick={openCreate}>
            ➕ Create Agent
          </button>
        </div>

        {agents.length === 0 ? (
          <div className="glass-card" style={{ padding: '48px', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>🤖</div>
            <div style={{ color: 'var(--text-secondary)' }}>No agents yet. Create your first agent to get started.</div>
          </div>
        ) : (
          <div className="agents-grid">
            {agents.map(agent => (
              <div key={agent.id} className="glass-card agent-card">
                <div className="agent-card-header">
                  <span className="agent-name">{agent.name}</span>
                  <span className={`agent-active-badge ${agent.is_active ? 'active' : 'inactive'}`}>
                    {agent.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                {agent.description && (
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
                    {agent.description}
                  </p>
                )}
                <div className="agent-details">
                  <div className="agent-detail">
                    <span className="agent-detail-label">LLM Provider</span>
                    <span className="agent-detail-value">
                      {agent.llm_provider
                        ? `${agent.llm_provider === 'ollama' ? '🦙' : '✨'} ${agent.llm_provider}`
                        : '🌐 Global'}
                    </span>
                  </div>
                  <div className="agent-detail">
                    <span className="agent-detail-label">Model</span>
                    <span className="agent-detail-value" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      {agent.llm_model || 'Default'}
                    </span>
                  </div>
                  <div className="agent-detail">
                    <span className="agent-detail-label">Language</span>
                    <span className="agent-detail-value">{agent.language}</span>
                  </div>
                  <div className="agent-detail">
                    <span className="agent-detail-label">Voice</span>
                    <span className="agent-detail-value">{agent.voice}</span>
                  </div>
                </div>
                <div className="agent-actions">
                  <button className="btn btn-secondary btn-sm" onClick={() => openEdit(agent)}>✏️ Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(agent)}>🗑 Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Create/Edit Modal ─────────────────────────────────────── */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h2 className="modal-title">
              {editingAgent ? `Edit Agent: ${editingAgent.name}` : 'Create New Agent'}
            </h2>

            <div className="settings-fields">
              <div className="form-group">
                <label className="form-label">Name</label>
                <input className="form-input" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="Sales Assistant" />
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <input className="form-input" value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} placeholder="Handles inbound sales calls" />
              </div>
              <div className="form-group">
                <label className="form-label">LLM Provider (leave empty for global)</label>
                <select className="form-select" value={form.llm_provider} onChange={e => setForm(p => ({ ...p, llm_provider: e.target.value }))}>
                  <option value="">Use Global Provider</option>
                  <option value="ollama">🦙 Ollama</option>
                  <option value="gemini">✨ Gemini</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Model (leave empty for default)</label>
                <input className="form-input" value={form.llm_model} onChange={e => setForm(p => ({ ...p, llm_model: e.target.value }))} placeholder="e.g. llama3.1 or gemini-2.0-flash" />
              </div>
              <div className="form-group">
                <label className="form-label">System Prompt</label>
                <textarea
                  className="form-input"
                  value={form.system_prompt}
                  onChange={e => setForm(p => ({ ...p, system_prompt: e.target.value }))}
                  rows={4}
                  style={{ resize: 'vertical', fontFamily: 'var(--font-sans)' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Language</label>
                  <input className="form-input" value={form.language} onChange={e => setForm(p => ({ ...p, language: e.target.value }))} />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Voice</label>
                  <input className="form-input" value={form.voice} onChange={e => setForm(p => ({ ...p, voice: e.target.value }))} />
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSave} disabled={!form.name.trim()}>
                {editingAgent ? 'Save Changes' : 'Create Agent'}
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && <div className={`toast toast-${toast.type}`}>{toast.msg}</div>}
    </>
  )
}
