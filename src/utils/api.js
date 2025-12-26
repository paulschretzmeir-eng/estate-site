// API endpoint for backend search
const API_URL = 'https://estate-site-production.up.railway.app/api';

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

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = localStorage.getItem('auth_token');
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error: ${response.status} ${errorText}`);
  }

  return response.json();
}

// ============================================
// CHAT FUNCTIONS
// ============================================

export async function sendChatMessage({ chatId, message, conversationHistory }) {
  return apiCall('/chat/message', {
    method: 'POST',
    body: JSON.stringify({
      chat_id: chatId === 'new' ? null : chatId,
      message,
      conversation_history: conversationHistory,
    }),
  });
}

export async function getChatHistory(chatId) {
  return apiCall(`/chat/${chatId}`);
}

export async function getChatList() {
  return apiCall('/chat/list');
}

export async function deleteChat(chatId) {
  return apiCall(`/chat/${chatId}`, {
    method: 'DELETE',
  });
}

export async function updateChatTitle(chatId, title) {
  return apiCall(`/chat/${chatId}/title`, {
    method: 'PUT',
    body: JSON.stringify({ title }),
  });
}

// ============================================
// FAVORITES
// ============================================

export async function addToFavorites(propertyId) {
  return apiCall('/favorites', {
    method: 'POST',
    body: JSON.stringify({ property_id: propertyId }),
  });
}

export async function removeFromFavorites(propertyId) {
  return apiCall(`/favorites/${propertyId}`, {
    method: 'DELETE',
  });
}

export async function getFavorites() {
  return apiCall('/favorites');
}

// ============================================
// OAUTH (Google, Apple)
// ============================================

export function initiateGoogleOAuth() {
  // Redirect to backend OAuth endpoint
  window.location.href = `${API_URL}/auth/google`;
}

export function initiateAppleOAuth() {
  // Redirect to backend OAuth endpoint
  window.location.href = `${API_URL}/auth/apple`;
}

export async function handleOAuthCallback(provider, code) {
  const response = await apiCall(`/auth/${provider}/callback`, {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
  
  if (response.token) {
    localStorage.setItem('auth_token', response.token);
    localStorage.setItem('user', JSON.stringify(response.user));
  }
  
  return response;
}
