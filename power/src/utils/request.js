import axios from 'axios';

// Prefer same-origin in production (nginx reverse proxy), configurable via VUE_APP_API_BASE_URL.
// - dev default: http://127.0.0.1:5000
// - prod default: "" (same origin)
const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL ||
  (process.env.NODE_ENV === 'production' ? '' : 'http://127.0.0.1:5000');

const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
});

service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

service.interceptors.response.use(
  response => response,
  error => {
    const status = error.response ? error.response.status : null;
    if (status === 401) {
      console.error('身份验证失败 (401)，请重新登录');
      localStorage.removeItem('token');
      localStorage.removeItem('role');
    }
    return Promise.reject(error);
  }
);

export default service;
