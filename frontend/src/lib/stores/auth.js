import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

const API_URL = 'http://localhost:8000/api';

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

					goto('/dashboard');
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
			if (!token) return;

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
					localStorage.removeItem('token');
					set({
						user: null,
						token: null,
						isAuthenticated: false,
						loading: false
					});
				}
			} catch (error) {
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
