const API_BASE = import.meta.env.VITE_API_URL || '';

function getToken() {
  return localStorage.getItem('token');
}

function setToken(token) {
  localStorage.setItem('token', token);
}

function clearToken() {
  localStorage.removeItem('token');
}

async function apiRequest(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
    ...options.headers,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || 'Request failed');
  }
  return data;
}

export const api = {
  login: async (username, password) => {
    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Login failed');
    setToken(data.access_token);
    return data;
  },

  register: (userData) =>
    apiRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),

  getMe: () => apiRequest('/api/v1/auth/me'),

  getDocuments: () => apiRequest('/api/v1/documents'),

  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiRequest('/api/v1/documents', {
      method: 'POST',
      body: formData,
    });
  },

  deleteDocument: (id) =>
    apiRequest(`/api/v1/documents/${id}`, { method: 'DELETE' }),

  askQuestion: (question, documentId, topK = 5) =>
    apiRequest('/api/v1/qa/ask', {
      method: 'POST',
      body: JSON.stringify({ question, document_id: documentId, top_k: topK }),
    }),

  createConversation: (documentId, title) =>
    apiRequest('/api/v1/conversations', {
      method: 'POST',
      body: JSON.stringify({ document_id: documentId, title }),
    }),

  getConversations: () => apiRequest('/api/v1/conversations'),

  getConversation: (id) => apiRequest(`/api/v1/conversations/${id}`),

  sendMessage: (conversationId, content) =>
    apiRequest(`/api/v1/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  logout: () => {
    clearToken();
  },

  isAuthenticated: () => !!getToken(),
};
