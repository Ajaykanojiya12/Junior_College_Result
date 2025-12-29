// src/services/api.js
import axios from "axios";

const baseURL = process.env.REACT_APP_API_BASE_URL || ""; // empty uses proxy in dev

const api = axios.create({
  baseURL,
  // withCredentials: true, // allow cookies (Flask session) when using same origin or proxy
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to request headers if available
api.interceptors.request.use((config) => {
  // Prefer an impersonation token (set in sessionStorage) only when
  // the current tab is showing teacher pages. This prevents an admin
  // tab from accidentally using a teacher token and losing admin access.
  try {
    const path = typeof window !== 'undefined' ? window.location.pathname : '';
    const onTeacherPath = path && path.startsWith('/teacher');
    const impersonate = sessionStorage.getItem('impersonateToken');
    if (impersonate && onTeacherPath) {
      config.headers.Authorization = `Bearer ${impersonate}`;
      return config;
    }
  } catch (e) {
    // ignore
  }

  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle error responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extract meaningful error message from server response
    if (error.response?.data?.error) {
      error.message = error.response.data.error;
    } else if (error.response?.data?.message) {
      error.message = error.response.data.message;
    } else if (error.response?.status === 401) {
      error.message = "Invalid username or password";
    } else if (error.response?.status === 403) {
      error.message = "You don't have permission to access this";
    } else if (error.response?.status === 404) {
      error.message = "Resource not found";
    } else if (error.response?.status === 500) {
      error.message = "Server error. Please try again later";
    }
    return Promise.reject(error);
  }
);

export default api;
