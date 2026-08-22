/**
 * API Client — Centralized fetch wrapper for backend communication.
 *
 * All API calls go through this module.
 * API keys and secrets are NEVER handled in the frontend.
 */

const API_BASE = '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ── Settings ──────────────────────────────────────────────────────────────
export function getSettings() {
  return request('/settings/llm');
}

export function updateSettings(data) {
  return request('/settings/llm', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// ── Providers ─────────────────────────────────────────────────────────────
export function getProviderStatus() {
  return request('/providers/status');
}

export function testProvider(name) {
  return request(`/providers/${name}/test`, { method: 'POST' });
}

// ── Agents ────────────────────────────────────────────────────────────────
export function getAgents() {
  return request('/agents/');
}

export function createAgent(data) {
  return request('/agents/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function getAgent(id) {
  return request(`/agents/${id}`);
}

export function updateAgent(id, data) {
  return request(`/agents/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function deleteAgent(id) {
  return request(`/agents/${id}`, { method: 'DELETE' });
}

// ── Conversation ──────────────────────────────────────────────────────────
export function startConversation(data = {}) {
  return request('/conversation/start', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function sendMessage(sessionId, message) {
  return request(`/conversation/${sessionId}/message`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

export function endConversation(sessionId) {
  return request(`/conversation/${sessionId}/end`, { method: 'POST' });
}

export function getConversationHistory(sessionId) {
  return request(`/conversation/${sessionId}/history`);
}
