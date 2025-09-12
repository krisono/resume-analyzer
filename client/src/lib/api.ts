// API configuration for different environments
const getApiBaseUrl = () => {
  // In development, try to use proxy first, fall back to deployed API
  if (import.meta.env.MODE === 'development') {
    // Use the deployed Vercel API for development
    return 'https://resume-analyzer-ruddy-theta.vercel.app';
  }
  // In production (Vercel), use relative paths
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const analyzeResume = async (resumeText: string, jobDescriptionText: string) => {
  const apiUrl = `${API_BASE_URL}/api/analyze`;
  console.log('Making API request to:', apiUrl);
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resume_text: resumeText,
        job_description_text: jobDescriptionText,
      }),
    });

    console.log('API response status:', response.status, response.statusText);

    if (!response.ok) {
      // Try to get error details from response
      let errorMessage = `Analysis failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        console.log('Error response data:', errorData);
        if (errorData.error) {
          errorMessage = errorData.error;
        }
      } catch (e) {
        // If we can't parse JSON, use the status text
        console.log('Could not parse error response');
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();
    console.log('API response successful:', result);
    
    // Check if the response contains an error field
    if (result.error) {
      throw new Error(result.error);
    }
    
    return result;
  } catch (error) {
    console.error('API call failed:', error);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error. Please check your connection.');
    }
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};
