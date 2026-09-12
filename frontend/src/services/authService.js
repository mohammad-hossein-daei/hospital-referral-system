// frontend/src/services/authService.js

const API_BASE = '/api';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

export async function request(url, options = {}) {
  const config = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    credentials: 'include',
  };

  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method)) {
    const csrf = getCookie('csrftoken');
    if (csrf) config.headers['X-CSRFToken'] = csrf;
  }

  if (options.body) config.body = options.body;

  const response = await fetch(`${API_BASE}${url}`, config);

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : { message: await response.text() };

  if (!response.ok) {
    const message =
      data?.errors?.non_field_errors?.[0] ||
      data?.message ||
      data?.detail ||
      'خطای ناشناخته';
    throw new Error(message);
  }

  return data;
}

export const authService = {
  getCsrf: () => fetch('/api/csrf/', { credentials: 'include' }),
  login: (national_code, password) =>
    request('/login/', {
      method: 'POST',
      body: JSON.stringify({ national_code, password }),
    }),
  logout: () => request('/logout/', { method: 'POST' }),
  currentUser: () => request('/user/'),
  checkAuth: () => request('/check-auth/'),
  doctorPatients: () => request('/doctor/patients/'),
  doctorReferrals: () => request('/doctor/referrals/'),  
};