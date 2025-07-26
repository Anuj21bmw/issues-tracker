import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { API_CONFIG, getApiUrl } from './config.js';

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
        const savedToken = localStorage.getItem('auth_token');
        const savedUser = localStorage.getItem('auth_user');
        
        if (savedToken && savedUser) {
            try {
                const user = JSON.parse(savedUser);
                set({
                    user,
                    token: savedToken,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null
                });
            } catch (e) {
                console.error('Failed to parse saved user data:', e);
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

                const response = await fetch(getApiUrl(API_CONFIG.endpoints.auth.login), {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Login failed' }));
                    throw new Error(errorData.detail || 'Login failed');
                }

                const data = await response.json();
                const token = data.access_token;

                // Get user data
                const userResponse = await fetch(getApiUrl(API_CONFIG.endpoints.auth.me), {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!userResponse.ok) {
                    throw new Error('Failed to get user data');
                }

                const user = await userResponse.json();

                // Save to localStorage
                if (browser) {
                    localStorage.setItem('auth_token', token);
                    localStorage.setItem('auth_user', JSON.stringify(user));
                }

                set({
                    user,
                    token,
                    isAuthenticated: true,
                    isLoading: false,
                    error: null
                });

                return { success: true, user };

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
                const response = await fetch(getApiUrl(API_CONFIG.endpoints.auth.register), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({ detail: 'Registration failed' }));
                    throw new Error(errorData.detail || 'Registration failed');
                }

                const user = await response.json();
                
                update(state => ({ ...state, isLoading: false }));
                
                return { success: true, user };

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

        // Helper to get auth headers
        getAuthHeaders() {
            const state = this.get();
            if (state.token) {
                return {
                    'Authorization': `Bearer ${state.token}`
                };
            }
            return {};
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

