// API configuration for different environments
const getApiBaseUrl = () => {
  // In production (Vercel), use relative paths
  if (import.meta.env.MODE === 'production') {
    return '';
  }
  // In development, use the proxy or localhost
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const analyzeResume = async (resumeText: string, jobDescriptionText: string) => {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      resume_text: resumeText,
      job_description_text: jobDescriptionText,
    }),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
};

export const checkHealth = async () => {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return response.json();
};
