import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor for future JWT injection
apiClient.interceptors.request.use((config) => {
  // We will inject the token here in Phase 1
  return config;
});

// Interceptor for standardized error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Standardized error extraction
    const message = error.response?.data?.message || "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

export default apiClient;
