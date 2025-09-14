// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'
const API_URL = import.meta.env.VITE_API_URL || `${API_BASE_URL}/api/v1`

export const config = {
  apiUrl: API_URL,
  apiBaseUrl: API_BASE_URL,
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  isDevelopment: import.meta.env.VITE_ENVIRONMENT !== 'production'
}

export default config
