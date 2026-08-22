import { useState, useEffect } from 'react'
import { getSettings, updateSettings, getProviderStatus, testProvider } from '../api/client'

export default function Settings() {
  const [settings, setSettings] = useState(null)
  const [providerStatus, setProviderStatus] = useState({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState({})
  const [toast, setToast] = useState(null)

  // Form state
  const [form, setForm] = useState({
    active_provider: 'ollama',
    fallback_provider: '',
    fallback_enabled: false,
    ollama_base_url: 'http://localhost:11434',
    ollama_model: 'llama3.1',
    gemini_api_key: '',
    gemini_model: 'gemini-2.0-flash',
    timeout_seconds: 30,
  })

  useEffect(() => {
    Promise.all([
      getSettings().catch(() => null),
      getProviderStatus().catch(() => ({ providers: [] })),
    ]).then(([s, ps]) => {
      if (s) {
        setSettings(s)
        setForm({
          active_provider: s.active_provider,
          fallback_provider: s.fallback_provider,
          fallback_enabled: s.fallback_enabled,
          ollama_base_url: s.ollama_base_url,
          ollama_model: s.ollama_model,
          gemini_api_key: '', // Never prefill — only show masked
          gemini_model: s.gemini_model,
          timeout_seconds: s.timeout_seconds,
        })
      }
      const statusMap = {}
      ps.providers?.forEach(p => { statusMap[p.provider] = p })
      setProviderStatus(statusMap)
      setLoading(false)
    })
  }, [])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload = { ...form }
      // Don't send empty API key (would clear it)
      if (!payload.gemini_api_key) delete payload.gemini_api_key
      const updated = await updateSettings(payload)
      setSettings(updated)
      showToast('Settings saved successfully')
    } catch (e) {
      showToast(e.message, 'error')
    }
    setSaving(false)
  }

  const handleTest = async (providerName) => {
    setTesting(prev => ({ ...prev, [providerName]: true }))
    try {
      const result = await testProvider(providerName)
      setProviderStatus(prev => ({ ...prev, [providerName]: result }))
      showToast(`${providerName}: ${result.status} (${result.latency_ms}ms)`)
    } catch (e) {
      showToast(`${providerName}: ${e.message}`, 'error')
    }
    setTesting(prev => ({ ...prev, [providerName]: false }))
  }

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1 className="page-title">LLM Settings</h1>
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
        <h1 className="page-title">LLM Settings</h1>
        <p className="page-description">Configure AI providers — switch between Ollama and Gemini at runtime</p>
      </div>

      <div className="page-content animate-fade-in">
        {/* ── Provider Selector ─────────────────────────────────────── */}
        <div className="glass-card settings-section" style={{ marginBottom: '24px' }}>
          <div className="settings-section-title">
            <span className="settings-section-icon">🔌</span>
            LLM Provider
          </div>

          <div className="provider-selector">
            {['ollama', 'gemini'].map(prov => (
              <div
                key={prov}
                className={`provider-option ${form.active_provider === prov ? 'selected' : ''}`}
                onClick={() => setForm(prev => ({ ...prev, active_provider: prov }))}
              >
                <div className="provider-radio">
                  <div className="provider-radio-dot"></div>
                </div>
                <div className="provider-option-info">
                  <div className="provider-option-name">
                    {prov === 'ollama' ? '🦙 Ollama' : '✨ Gemini'}
                  </div>
                  <div className="provider-option-desc">
                    {prov === 'ollama' ? 'Local/self-hosted LLM' : 'Google Gemini API (cloud)'}
                  </div>
                </div>
                <div>
                  <span className={`status-dot ${providerStatus[prov]?.status || 'unknown'}`}></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Provider Configs ──────────────────────────────────────── */}
        <div className="settings-grid">
          {/* Ollama Config */}
          <div className="glass-card settings-section">
            <div className="settings-section-title">
              <span className="settings-section-icon">🦙</span>
              Ollama Settings
            </div>
            <div className="settings-fields">
              <div className="form-group">
                <label className="form-label">Base URL</label>
                <input
                  className="form-input"
                  type="text"
                  value={form.ollama_base_url}
                  onChange={e => setForm(prev => ({ ...prev, ollama_base_url: e.target.value }))}
                  placeholder="http://localhost:11434"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Model</label>
                <input
                  className="form-input"
                  type="text"
                  value={form.ollama_model}
                  onChange={e => setForm(prev => ({ ...prev, ollama_model: e.target.value }))}
                  placeholder="llama3.1"
                />
              </div>
              <div className="provider-actions">
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleTest('ollama')}
                  disabled={testing.ollama}
                >
                  {testing.ollama ? <span className="spinner"></span> : '🔗'} Test Connection
                </button>
              </div>
              {providerStatus.ollama && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <span className={`status-dot ${providerStatus.ollama.status}`}></span>
                  {' '}{providerStatus.ollama.message}
                </div>
              )}
            </div>
          </div>

          {/* Gemini Config */}
          <div className="glass-card settings-section">
            <div className="settings-section-title">
              <span className="settings-section-icon">✨</span>
              Gemini Settings
            </div>
            <div className="settings-fields">
              <div className="form-group">
                <label className="form-label">API Key</label>
                <input
                  className="form-input"
                  type="password"
                  value={form.gemini_api_key}
                  onChange={e => setForm(prev => ({ ...prev, gemini_api_key: e.target.value }))}
                  placeholder={settings?.gemini_api_key_masked || 'Enter API key'}
                />
                {settings?.gemini_api_key_masked && (
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Current: {settings.gemini_api_key_masked}
                  </span>
                )}
              </div>
              <div className="form-group">
                <label className="form-label">Model</label>
                <input
                  className="form-input"
                  type="text"
                  value={form.gemini_model}
                  onChange={e => setForm(prev => ({ ...prev, gemini_model: e.target.value }))}
                  placeholder="gemini-2.0-flash"
                />
              </div>
              <div className="provider-actions">
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleTest('gemini')}
                  disabled={testing.gemini}
                >
                  {testing.gemini ? <span className="spinner"></span> : '🔗'} Test Connection
                </button>
              </div>
              {providerStatus.gemini && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  <span className={`status-dot ${providerStatus.gemini.status}`}></span>
                  {' '}{providerStatus.gemini.message}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ── Fallback Settings ─────────────────────────────────────── */}
        <div className="glass-card settings-section" style={{ marginTop: '24px' }}>
          <div className="settings-section-title">
            <span className="settings-section-icon">🔄</span>
            Fallback Configuration
          </div>
          <div className="settings-fields" style={{ maxWidth: '400px' }}>
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={form.fallback_enabled}
                  onChange={e => setForm(prev => ({ ...prev, fallback_enabled: e.target.checked }))}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent-primary)' }}
                />
                Enable Fallback Provider
              </label>
            </div>
            {form.fallback_enabled && (
              <div className="form-group">
                <label className="form-label">Fallback Provider</label>
                <select
                  className="form-select"
                  value={form.fallback_provider}
                  onChange={e => setForm(prev => ({ ...prev, fallback_provider: e.target.value }))}
                >
                  <option value="">Select...</option>
                  {['ollama', 'gemini']
                    .filter(p => p !== form.active_provider)
                    .map(p => (
                      <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                    ))
                  }
                </select>
              </div>
            )}
            <div className="form-group">
              <label className="form-label">Timeout (seconds)</label>
              <input
                className="form-input"
                type="number"
                value={form.timeout_seconds}
                onChange={e => setForm(prev => ({ ...prev, timeout_seconds: parseInt(e.target.value) || 30 }))}
                min={5}
                max={120}
              />
            </div>
          </div>
        </div>

        {/* ── Save ──────────────────────────────────────────────────── */}
        <div className="settings-footer">
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            {saving ? <span className="spinner"></span> : '💾'} Save Configuration
          </button>
        </div>
      </div>

      {/* ── Toast ───────────────────────────────────────────────────── */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.msg}
        </div>
      )}
    </>
  )
}
