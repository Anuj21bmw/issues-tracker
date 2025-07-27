import { browser } from '$app/environment';
import { get } from 'svelte/store';
import { authStore } from '$lib/stores/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function getApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  
  if (browser) {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }
  
  return headers;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = getApiUrl(endpoint);
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...(options.headers || {})
    }
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    if (response.status === 401) {
      if (browser) {
        authStore.logout();
      }
      throw new Error('Authentication required');
    }
    
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function uploadFile(
  endpoint: string,
  formData: FormData
): Promise<any> {
  const url = getApiUrl(endpoint);
  
  const headers: Record<string, string> = {};
  if (browser) {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: formData
  });

  if (!response.ok) {
    if (response.status === 401) {
      if (browser) {
        authStore.logout();
      }
      throw new Error('Authentication required');
    }
    
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed: HTTP ${response.status}`);
  }

  return response.json();
}
