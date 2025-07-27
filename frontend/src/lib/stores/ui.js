// src/lib/stores/ui.js
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// UI state store
const createUIStore = () => {
    const { subscribe, set, update } = writable({
        theme: 'light',
        sidebarOpen: true,
        mobileMenuOpen: false,
        chatOpen: false,
        isLoading: false,
        modal: null
    });

    // Load theme from localStorage on initialization
    if (browser) {
        const savedTheme = localStorage.getItem('ui_theme') || 'light';
        update(state => ({ ...state, theme: savedTheme }));
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    return {
        subscribe,
        
        toggleTheme() {
            update(state => {
                const newTheme = state.theme === 'light' ? 'dark' : 'light';
                
                if (browser) {
                    localStorage.setItem('ui_theme', newTheme);
                    document.documentElement.setAttribute('data-theme', newTheme);
                }
                
                return { ...state, theme: newTheme };
            });
        },

        setTheme(theme) {
            update(state => {
                if (browser) {
                    localStorage.setItem('ui_theme', theme);
                    document.documentElement.setAttribute('data-theme', theme);
                }
                
                return { ...state, theme };
            });
        },

        toggleSidebar() {
            update(state => ({ ...state, sidebarOpen: !state.sidebarOpen }));
        },

        setSidebar(open) {
            update(state => ({ ...state, sidebarOpen: open }));
        },

        toggleMobileMenu() {
            update(state => ({ ...state, mobileMenuOpen: !state.mobileMenuOpen }));
        },

        setMobileMenu(open) {
            update(state => ({ ...state, mobileMenuOpen: open }));
        },

        toggleChat() {
            update(state => ({ ...state, chatOpen: !state.chatOpen }));
        },

        setChat(open) {
            update(state => ({ ...state, chatOpen: open }));
        },

        setLoading(loading) {
            update(state => ({ ...state, isLoading: loading }));
        },

        openModal(modal) {
            update(state => ({ ...state, modal }));
        },

        closeModal() {
            update(state => ({ ...state, modal: null }));
        }
    };
};

export const uiStore = createUIStore();