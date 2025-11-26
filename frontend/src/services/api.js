import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const parseResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_BASE_URL}/resume/parse`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data.detail || 'Unknown error occurred';

      // Provide user-friendly error messages based on status codes
      if (status === 400) {
        throw new Error(`Invalid file: ${detail}`);
      } else if (status === 413) {
        throw new Error('File is too large. Maximum size is 10MB.');
      } else if (status === 422) {
        // 422 is used for both extraction failures and validation failures
        // The detail message from backend is already user-friendly
        throw new Error(detail);
      } else if (status === 500) {
        throw new Error('Server error while processing PDF. Please try again.');
      } else {
        throw new Error(detail);
      }
    }

    if (error.request) {
      throw new Error('Cannot connect to server. Please make sure the backend is running on http://localhost:8000');
    }

    throw new Error('An unexpected error occurred. Please try again.');
  }
};
