const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const fetchJson = async <T>(path: string, options?: RequestInit): Promise<T> => {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json'
    },
    ...options
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || 'Network response was not ok');
  }

  return response.json();
};
