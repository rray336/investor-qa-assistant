import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add any auth headers if needed in future
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed later
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', error.request);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const uploadPDFs = async (files, confidentialFlags) => {
  const formData = new FormData();
  
  // Append files
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  // Append confidential flags
  confidentialFlags.forEach((flag) => {
    formData.append('confidential', flag);
  });

  return api.post('/upload-pdfs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 60000, // 1 minute for file uploads
  });
};

export const askQuestion = async (question) => {
  return api.post('/ask-question', { question });
};

export const getPDFs = async () => {
  return api.get('/pdfs');
};

export const clearAllData = async () => {
  return api.delete('/clear-all');
};

export const healthCheck = async () => {
  return api.get('/health');
};

export default api;