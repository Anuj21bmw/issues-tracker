// frontend/src/lib/stores/auth.js - Fixed API URLs
import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

// Use relative URLs that work in both development and production
const API_URL = '/api';

function createAuthStore() {
	const { subscribe, set, update } = writable({
		user: null,
		token: null,
		isAuthenticated: false,
		loading: false
	});

	return {
		subscribe,
		async login(email, password) {
			update(state => ({ ...state, loading: true }));
			
			try {
				const formData = new FormData();
				formData.append('username', email);
				formData.append('password', password);

				const response = await fetch(`${API_URL}/auth/login`, {
					method: 'POST',
					body: formData
				});

				const data = await response.json();

				if (!response.ok) {
					throw new Error(data.detail || 'Login failed');
				}

				if (browser) {
					localStorage.setItem('token', data.access_token);
				}

				// Get user data
				const userResponse = await fetch(`${API_URL}/auth/me`, {
					headers: {
						'Authorization': `Bearer ${data.access_token}`
					}
				});

				const userData = await userResponse.json();

				if (userResponse.ok) {
					set({
						user: userData,
						token: data.access_token,
						isAuthenticated: true,
						loading: false
					});

					// Redirect based on role
					if (userData.role === 'ADMIN' || userData.role === 'MAINTAINER') {
						goto('/dashboard');
					} else {
						goto('/issues');
					}
				} else {
					throw new Error('Failed to get user data');
				}
			} catch (error) {
				set({
					user: null,
					token: null,
					isAuthenticated: false,
					loading: false
				});
				throw error;
			}
		},

		async register(userData) {
			update(state => ({ ...state, loading: true }));
			
			try {
				const response = await fetch(`${API_URL}/auth/register`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(userData)
				});

				const data = await response.json();

				if (!response.ok) {
					throw new Error(data.detail || 'Registration failed');
				}

				update(state => ({ ...state, loading: false }));
				goto('/auth/login');
			} catch (error) {
				update(state => ({ ...state, loading: false }));
				throw error;
			}
		},

		async logout() {
			if (browser) {
				localStorage.removeItem('token');
			}
			
			set({
				user: null,
				token: null,
				isAuthenticated: false,
				loading: false
			});

			goto('/auth/login');
		},

		async checkAuth() {
			if (!browser) return;

			const token = localStorage.getItem('token');
			if (!token) {
				set({
					user: null,
					token: null,
					isAuthenticated: false,
					loading: false
				});
				return;
			}

			try {
				const response = await fetch(`${API_URL}/auth/me`, {
					headers: {
						'Authorization': `Bearer ${token}`
					}
				});

				if (response.ok) {
					const userData = await response.json();
					set({
						user: userData,
						token,
						isAuthenticated: true,
						loading: false
					});
				} else {
					// Token is invalid, remove it
					localStorage.removeItem('token');
					set({
						user: null,
						token: null,
						isAuthenticated: false,
						loading: false
					});
				}
			} catch (error) {
				console.error('Auth check failed:', error);
				localStorage.removeItem('token');
				set({
					user: null,
					token: null,
					isAuthenticated: false,
					loading: false
				});
			}
		},

		getAuthHeaders() {
			const token = browser ? localStorage.getItem('token') : null;
			return token ? { 'Authorization': `Bearer ${token}` } : {};
		}
	};
}

export const authStore = createAuthStore();