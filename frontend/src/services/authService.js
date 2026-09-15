// frontend/src/services/authService.js

const API_BASE = '/api';

function getTokens() {
  return {
    access: localStorage.getItem('access_token'),
    refresh: localStorage.getItem('refresh_token'),
  };
}

function setTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

async function refreshAccessToken() {
  const { refresh } = getTokens();
  if (!refresh) throw new Error('توکن refresh موجود نیست');

  const response = await fetch(`${API_BASE}/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearTokens();
    throw new Error('نشست شما منقضی شده است');
  }

  const data = await response.json();
  setTokens(data.access, null);
  return data.access;
}

export async function request(url, options = {}, retry = true) {
  const { access } = getTokens();

  const config = {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(access ? { Authorization: `Bearer ${access}` } : {}),
      ...(options.headers || {}),
    },
  };

  if (options.body) config.body = options.body;

  const response = await fetch(`${API_BASE}${url}`, config);

  if (response.status === 401 && retry && access) {
    try {
      await refreshAccessToken();
      return request(url, options, false);
    } catch {
      clearTokens();
      throw new Error('نشست شما منقضی شده است');
    }
  }

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
  login: async (national_code, password) => {
    const data = await request('/login/', {
      method: 'POST',
      body: JSON.stringify({ national_code, password }),
    });
    setTokens(data.access, data.refresh);
    return data;
  },
  logout: async () => {
    const { refresh } = getTokens();
    try {
      await request('/logout/', {
        method: 'POST',
        body: JSON.stringify({ refresh }),
      });
    } finally {
      clearTokens();
    }
  },
  currentUser: () => request('/user/'),
  checkAuth: () => request('/check-auth/'),
  doctorPatients: () => request('/doctor/patients/'),
  doctorReferrals: () => request('/doctor/referrals/'),
  adminUsers: () => request('/admin/users/'),
  adminDoctors: () => request('/admin/doctors/'),
  adminReceptionists: () => request('/admin/receptionists/'),
};
