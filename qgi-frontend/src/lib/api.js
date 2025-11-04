const API = import.meta.env.VITE_API_BASE_URL;

export async function api(path, { method='GET', body, token, headers } = {}) {
  const h = { ...(headers || {}) };
  if (token) h.Authorization = `Bearer ${token}`;

  const opts = { method, headers: h, credentials: 'include' };

  if (body instanceof FormData) {
    opts.body = body; // let browser set multipart boundary
  } else if (body != null) {
    h['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}
