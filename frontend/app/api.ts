export const API_URL = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');

export function authHeaders(token: string, extra: HeadersInit = {}): HeadersInit {
  return { Authorization: `Bearer ${token}`, ...extra };
}

export async function apiFetch(path: string, token: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers);
  headers.set('Authorization', `Bearer ${token}`);
  return fetch(`${API_URL}${path}`, { ...init, headers });
}

export async function readApiError(response: Response, fallback = 'حدث خطأ في الخادم') {
  try {
    const data = await response.json();
    return typeof data?.detail === 'string' ? data.detail : fallback;
  } catch {
    return fallback;
  }
}
