// src/lib/stores/auth.js
import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { API_CONFIG, getApiUrl, getAuthHeaders } from '$lib/config.js';

// Auth state
const createAuthStore = () => {
    const { subscribe, set, update } = writable({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
    });

    // Load token from localStorage on initialization
    if (browser) {
        try {
            const savedToken = localStorage.getItem('auth_token');
            const savedUser = localStorage.getItem('auth_user');
            
            if (savedToken && savedUser) {
                const user = JSON.parse(savedUser);
                set({
                    user,
                    token: savedToken,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null
                });
            }
        } catch (e) {
            console.error('Failed to parse saved user data:', e);
            if (browser) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('auth_user');
            }
        }
    }

    return {
        subscribe,
        
        async login(email, password) {
            update(state => ({ ...state, isLoading: true, error: null }));
            
            try {
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);

                const response = await fetch(getApiUrl('/api/auth/login'), {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    let errorMessage = 'Login failed';
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.detail || errorMessage;
                    } catch (e) {
                        // If we can't parse the error, use the default message
                    }
                    throw new Error(errorMessage);
                }

                const data = await response.json();
                
                // Handle different response formats
                let accessToken, user;
                if (data.access_token) {
                    accessToken = data.access_token;
                    user = data.user || { email, full_name: email };
                } else if (data.token) {
                    accessToken = data.token;
                    user = data.user || { email, full_name: email };
                } else {
                    throw new Error('Invalid response format');
                }

                // Save to localStorage
                if (browser) {
                    localStorage.setItem('auth_token', accessToken);
                    localStorage.setItem('auth_user', JSON.stringify(user));
                }

                set({
                    user,
                    token: accessToken,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null
                });

                // Navigate to dashboard
                await goto('/dashboard');
                return { success: true };

            } catch (error) {
                const errorMessage = error.message || 'Login failed';
                update(state => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async register(userData) {
            update(state => ({ ...state, isLoading: true, error: null }));
            
            try {
                const response = await fetch(getApiUrl('/api/auth/register'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });

                if (!response.ok) {
                    let errorMessage = 'Registration failed';
                    try {
                        const errorData = await response.json();
                        errorMessage = errorData.detail || errorMessage;
                    } catch (e) {
                        // Use default message if parsing fails
                    }
                    throw new Error(errorMessage);
                }

                const data = await response.json();
                const { access_token, user } = data;

                // Save to localStorage
                if (browser) {
                    localStorage.setItem('auth_token', access_token);
                    localStorage.setItem('auth_user', JSON.stringify(user));
                }

                set({
                    user,
                    token: access_token,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null
                });

                await goto('/dashboard');
                return { success: true };

            } catch (error) {
                const errorMessage = error.message || 'Registration failed';
                update(state => ({
                    ...state,
                    isLoading: false,
                    error: errorMessage
                }));
                return { success: false, error: errorMessage };
            }
        },

        async verifyToken() {
            if (!browser) return;
            
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            try {
                const response = await fetch(getApiUrl('/api/auth/me'), {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const user = await response.json();
                    
                    if (browser) {
                        localStorage.setItem('auth_user', JSON.stringify(user));
                    }

                    update(state => ({
                        ...state,
                        user,
                        token,
                        isAuthenticated: true,
                        isLoading: false
                    }));
                } else {
                    // Token is invalid
                    this.logout();
                }
            } catch (error) {
                console.error('Token verification failed:', error);
                this.logout();
            }
        },

        logout() {
            if (browser) {
                localStorage.removeItem('auth_token');
                localStorage.removeItem('auth_user');
            }
            
            set({
                user: null,
                token: null,
                isAuthenticated: false,
                isLoading: false,
                error: null
            });
            
            goto('/auth/login');
        },

        clearError() {
            update(state => ({ ...state, error: null }));
        },

        // Helper to get auth headers (for backward compatibility)
        getAuthHeaders() {
            return getAuthHeaders();
        },

        // Get current state
        get() {
            let currentState;
            subscribe(state => currentState = state)();
            return currentState;
        }
    };
};

export const authStore = createAuthStore();

// Derived stores for convenience
export const user = derived(authStore, $auth => $auth.user);
export const isAuthenticated = derived(authStore, $auth => $auth.isAuthenticated);
export const isLoading = derived(authStore, $auth => $auth.isLoading);
export const authError = derived(authStore, $auth => $auth.error);