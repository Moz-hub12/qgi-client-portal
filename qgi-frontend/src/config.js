// API Configuration for different environments
const config = {
  development: {
    API_BASE_URL: 'http://localhost:5001',
    FRONTEND_URL: 'http://localhost:5173'
  },
  production: {
    API_BASE_URL: 'https://api.quantumgrowthinvestments.com',
    FRONTEND_URL: 'https://www.quantumgrowthinvestments.com'
  }
};

const environment = import.meta.env.MODE || 'development';

// Use environment variables if available, otherwise fall back to config
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || config[environment].API_BASE_URL;
export const FRONTEND_URL = import.meta.env.VITE_FRONTEND_URL || config[environment].FRONTEND_URL;

export default {
  API_BASE_URL,
  FRONTEND_URL
};
