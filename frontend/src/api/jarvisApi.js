import axios from 'axios';

// Determine API base URL based on environment
const getApiBase = () => {
  // In production, use the environment variable
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }

  // In development, use the relative path for vite proxy
  if (import.meta.env.DEV) {
    return '/api';
  }

  // Fallback to absolute backend URL from env or production default
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'https://jarvis-production-5709a.up.railway.app';
  return `${backendUrl}/api`;
};

const API_BASE = getApiBase();

class JarvisAPI {
  async processText(text, contextId = null) {
    try {
      console.log(`[API] Sending text request to ${API_BASE}/text`);
      console.log(`[API] Backend URL: ${API_BASE}`);
      console.log(`[API] Text: ${text}, Context: ${contextId}`);

      const response = await axios.post(`${API_BASE}/text`, {
        text,
        context_id: contextId
      });

      console.log('[API] Response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('API Error in processText:', error.response?.data || error.message);
      console.error('API Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        config: error.config
      });
      throw error;
    }
  }

  async processMultimodal(formData) {
    try {
      const response = await axios.post(`${API_BASE}/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('API Error in processMultimodal:', error.response?.data || error.message);
      throw error;
    }
  }

  async getScene(contextId) {
    try {
      const response = await axios.get(`${API_BASE}/scene/${contextId}`);
      return response.data;
    } catch (error) {
      console.error('API Error in getScene:', error.response?.data || error.message);
      throw error;
    }
  }

  async listScenes() {
    try {
      const response = await axios.get(`${API_BASE}/scenes`);
      return response.data;
    } catch (error) {
      console.error('API Error in listScenes:', error.response?.data || error.message);
      throw error;
    }
  }

  async deleteScene(contextId) {
    try {
      const response = await axios.delete(`${API_BASE}/scene/${contextId}`);
      return response.data;
    } catch (error) {
      console.error('API Error in deleteScene:', error.response?.data || error.message);
      throw error;
    }
  }

  async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      return response.data;
    } catch (error) {
      console.error('API Error in healthCheck:', error.response?.data || error.message);
      throw error;
    }
  }

  async deleteObject(contextId, objectIndex) {
    try {
      const response = await axios.delete(`${API_BASE}/scene/${contextId}/object/${objectIndex}`);
      return response.data;
    } catch (error) {
      console.error('API Error in deleteObject:', error.response?.data || error.message);
      throw error;
    }
  }
}

export default new JarvisAPI();
