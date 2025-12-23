// Lightweight API client for the frontend
// Provides: searchProperties(query)

const API_BASE = 'https://estate-site-production.up.railway.app';
const SEARCH_ENDPOINT = '/api/search';

/**
 * Search properties via backend API
 * @param {string} query - Natural language or keyword user query
 * @param {{ timeoutMs?: number }} [options] - Optional settings (e.g., timeout)
 * @returns {Promise<any>} - Parsed JSON response from the backend
 */
export async function searchProperties(query, options = {}) {
  if (typeof query !== 'string') {
    throw new TypeError('searchProperties(query) expects a string');
  }

  const timeoutMs = typeof options.timeoutMs === 'number' ? options.timeoutMs : 15000;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(new Error('Request timed out')), timeoutMs);

  try {
    const res = await fetch(`${API_BASE}${SEARCH_ENDPOINT}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
        body: JSON.stringify({ prompt: query }),
      signal: controller.signal,
    });

    // Read as text first to give better error messages if JSON parsing fails
    const text = await res.text();
    let data = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch (err) {
        const e = new Error(`Invalid JSON response: ${err?.message || 'unknown error'}`);
        e.cause = err;
        e.raw = text;
        e.status = res.status;
        throw e;
      }
    }

    if (!res.ok) {
      const message = (data && (data.error || data.message)) || res.statusText || 'Request failed';
      const e = new Error(`API error ${res.status}: ${message}`);
      e.status = res.status;
      e.data = data;
      throw e;
    }

    return data;
  } catch (err) {
    // Surface error to caller but also log for debugging
    // eslint-disable-next-line no-console
    console.error('[api.searchProperties] Error:', err);
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}
