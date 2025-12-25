// API endpoint for backend search
const API_URL = 'https://estate-site-production.up.railway.app';

export async function searchAPI(prompt) {
  console.log('🔍 Searching with API_URL:', API_URL);
  
  const resp = await fetch(`${API_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  })
  
  if (!resp.ok) {
    const errorText = await resp.text();
    console.error('❌ API Error:', resp.status, errorText);
    throw new Error(`Search failed: ${resp.status} ${errorText}`);
  }
  
  const data = await resp.json();
  console.log('✅ API Response:', data);
  return data;
}
