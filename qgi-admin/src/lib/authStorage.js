// src/lib/authStorage.js
export const ADMIN_TOKEN_KEY = 'admin_token';
export const ADMIN_REFRESH_KEY = 'admin_refresh_token';
export const ADMIN_USER_KEY  = 'admin_user';

// Migrate legacy keys once
(function migrateLegacyKeys() {
  try {
    const legacyToken = localStorage.getItem('adminToken') || localStorage.getItem('admin_Token');
    if (legacyToken && !localStorage.getItem(ADMIN_TOKEN_KEY)) {
      localStorage.setItem(ADMIN_TOKEN_KEY, legacyToken);
    }
    const legacyUser = localStorage.getItem('adminUser') || localStorage.getItem('admin_User');
    if (legacyUser && !localStorage.getItem(ADMIN_USER_KEY)) {
      localStorage.setItem(ADMIN_USER_KEY, legacyUser);
    }
    ['adminToken','admin_Token','adminUser','admin_User'].forEach(k => localStorage.removeItem(k));
  } catch {}
})();

export const getToken = () => {
  try { return localStorage.getItem(ADMIN_TOKEN_KEY); } catch { return null; }
};
export const setToken = (t) => { try { localStorage.setItem(ADMIN_TOKEN_KEY, t); } catch {} };
export const clearToken = () => { try { localStorage.removeItem(ADMIN_TOKEN_KEY); } catch {} };

export const getRefreshToken = () => {
  try { return localStorage.getItem(ADMIN_REFRESH_KEY); } catch { return null; }
};
export const setRefreshToken = (t) => { try { localStorage.setItem(ADMIN_REFRESH_KEY, t); } catch {} };
export const clearRefreshToken = () => { try { localStorage.removeItem(ADMIN_REFRESH_KEY); } catch {} };

export const getAdminUser = () => {
  try { const raw = localStorage.getItem(ADMIN_USER_KEY); return raw ? JSON.parse(raw) : null } catch { return null }
};
export const setAdminUser = (u) => { try { localStorage.setItem(ADMIN_USER_KEY, JSON.stringify(u ?? null)) } catch {} };
export const clearAdminUser = () => { try { localStorage.removeItem(ADMIN_USER_KEY) } catch {} };

export const clearAllAuth = () => {
  clearToken(); clearRefreshToken(); clearAdminUser();
};
