const API_BASE = import.meta.env.VITE_API_URL || 'https://estate-site-production.up.railway.app'

export async function searchAPI(prompt) {
  const resp = await fetch(`${API_BASE}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  })
  if (!resp.ok) throw new Error('Search request failed')
  return resp.json()
}
