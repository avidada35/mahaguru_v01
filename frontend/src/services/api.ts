import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import { getToken, removeToken } from '@/utils/token';

// Type guard for import.meta.env (Vite)
interface ImportMetaEnv {
  VITE_API_BASE_URL?: string;
}
declare const importMetaEnv: ImportMetaEnv;
const API_BASE_URL = (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_API_BASE_URL) || 'http://localhost:8000/api/v1';

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh token
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, { withCredentials: true });
        const { access_token } = response.data;
        
        // Store the new token
        localStorage.setItem('access_token', access_token);
        
        // Update the Authorization header
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh token fails, log the user out
        removeToken();
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;

// StudentGPT API function
export const sendStudentGPTMessage = async (message: string): Promise<string> => {
  try {
    const response = await api.post('/studentgpt/chat', { message });
    return response.data.response;
  } catch (error: any) {
    if (error.response?.status === 504) {
      return 'StudentGPT is taking too long. Please try a shorter question.';
    }
    throw error;
  }
};
