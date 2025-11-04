// src/lib/apiFetch.js
import { API_BASE_URL } from '../config'
import {
  getToken, setToken, getRefreshToken, setRefreshToken, clearAllAuth
} from './authStorage'

// helper to do JSON fetch and auto-refresh access token on 401
export async function apiFetch(path, opts = {}, retry = true) {
  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`

  const token = getToken()
  const headers = Object.assign({}, opts.headers || {}, {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  })
  const fetchOpts = Object.assign({}, opts, { headers })

  const res = await fetch(url, fetchOpts)
  if (res.status !== 401) return res

  // 401 handling: try refresh once
  if (!retry) return res

  const refresh = getRefreshToken()
  if (!refresh) {
    // nothing to do
    return res
  }

  // Attempt refresh
  try {
    const r = await fetch(`${API_BASE_URL}/api/admin/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${refresh}` // backend expects refresh token auth (or change if server expects differently)
      }
    })

    if (!r.ok) {
      // refresh failed — sign out
      clearAllAuth()
      return res
    }

    const body = await r.json()
    if (body && body.access_token) {
      setToken(body.access_token)
      // retry original request once with new token
      return apiFetch(path, opts, false)
    } else {
      clearAllAuth()
      return res
    }
  } catch (e) {
    // network or unexpected error — logout as a safe fallback
    clearAllAuth()
    return res
  }
}
