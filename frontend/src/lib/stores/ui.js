import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';

const createUIStore = () => {
    const { subscribe, set, update } = writable({
        sidebarCollapsed: false,
        theme: 'light',
        loading: {},
        modals: {},
        notifications: {
            position: 'top-right',
            maxVisible: 5
        }
    });

    // Load saved UI preferences
    if (browser) {
        const savedTheme = localStorage.getItem('ui_theme');
        const savedSidebar = localStorage.getItem('ui_sidebar_collapsed');
        
        if (savedTheme || savedSidebar) {
            update(state => ({
                ...state,
                theme: savedTheme || 'light',
                sidebarCollapsed: savedSidebar === 'true'
            }));
        }
    }

    return {
        subscribe,

        toggleSidebar() {
            update(state => {
                const collapsed = !state.sidebarCollapsed;
                if (browser) {
                    localStorage.setItem('ui_sidebar_collapsed', collapsed.toString());
                }
                return { ...state, sidebarCollapsed: collapsed };
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

        setLoading(key, loading) {
            update(state => ({
                ...state,
                loading: { ...state.loading, [key]: loading }
            }));
        },

        openModal(modalId, data = {}) {
            update(state => ({
                ...state,
                modals: { ...state.modals, [modalId]: { open: true, data } }
            }));
        },

        closeModal(modalId) {
            update(state => ({
                ...state,
                modals: { ...state.modals, [modalId]: { open: false, data: {} } }
            }));
        }
    };
};

export const uiStore = createUIStore();


// Derived stores
export const theme = derived(uiStore, $ui => $ui.theme);
export const sidebarCollapsed = derived(uiStore, $ui => $ui.sidebarCollapsed);
export const loading = derived(uiStore, $ui => $ui.loading);