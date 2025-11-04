// API Configuration for admin portal
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5001',
    CLIENT_PORTAL_URL: 'http://localhost:5173'
  },
  production: {
    API_BASE_URL: 'https://api.quantumgrowthinvestments.com',
    CLIENT_PORTAL_URL: 'https://www.quantumgrowthinvestments.com'
  }
};

const environment = import.meta.env.MODE || 'development';

// Use environment variables if available, otherwise fall back to config
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || config[environment].API_BASE_URL;
export const CLIENT_PORTAL_URL = import.meta.env.VITE_CLIENT_PORTAL_URL || config[environment].CLIENT_PORTAL_URL;

export default {
  API_BASE_URL,
  CLIENT_PORTAL_URL
};

