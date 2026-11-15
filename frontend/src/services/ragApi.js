const API_BASE = 'http://127.0.0.1:8000'

async function request(path, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
  } catch {
    throw new Error(
      'Cannot connect to FastAPI. Check that the backend is running on port 8000.'
    )
  }

  let data

  try {
    data = await response.json()
  } catch {
    throw new Error(`Invalid API response (HTTP ${response.status}).`)
  }

  if (!response.ok) {
    const detail = data.detail || data.error
    throw new Error(
      typeof detail === 'string'
        ? detail
        : JSON.stringify(detail || `HTTP ${response.status}`)
    )
  }

  return data
}

export const ragApi = {
  evaluations: () => request('/api/rag/evaluations'),

  evaluation: (id) =>
    request(`/api/rag/evaluations/${encodeURIComponent(id)}`),

  health: () => request('/api/rag/health'),

  config: () => request('/api/rag/config'),

  retrieve: (payload) =>
    request('/api/rag/retrieve', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  compare: (payload) =>
    request('/api/rag/compare', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
}
