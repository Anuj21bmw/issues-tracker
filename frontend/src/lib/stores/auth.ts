import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
}

function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>({
    user: null,
    isAuthenticated: false,
    loading: true
  });

  return {
    subscribe,
    
    async init() {
      if (!browser) return;
      
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('auth_user');
      
      if (token && userData) {
        try {
          const user = JSON.parse(userData);
          set({
            user,
            isAuthenticated: true,
            loading: false
          });
        } catch {
          this.logout();
        }
      } else {
        set({
          user: null,
          isAuthenticated: false,
          loading: false
        });
      }
    },
    
    login(token: string, user: User) {
      if (browser) {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('auth_user', JSON.stringify(user));
      }
      
      set({
        user,
        isAuthenticated: true,
        loading: false
      });
    },
    
    logout() {
      if (browser) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('auth_user');
      }
      
      set({
        user: null,
        isAuthenticated: false,
        loading: false
      });
    },
    
    updateUser(user: User) {
      if (browser) {
        localStorage.setItem('auth_user', JSON.stringify(user));
      }
      
      update(state => ({
        ...state,
        user
      }));
    }
  };
}

export const authStore = createAuthStore();
