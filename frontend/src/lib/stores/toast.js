import { writable } from 'svelte/store';

const createToastStore = () => {
    const { subscribe, update } = writable([]);

    return {
        subscribe,
        
        add(toast) {
            const id = Math.random().toString(36).substr(2, 9);
            const newToast = {
                id,
                type: 'info', // 'success', 'error', 'warning', 'info'
                message: '',
                duration: 5000,
                dismissible: true,
                ...toast
            };

            update(toasts => [...toasts, newToast]);

            // Auto-remove after duration
            if (newToast.duration > 0) {
                setTimeout(() => {
                    this.remove(id);
                }, newToast.duration);
            }

            return id;
        },

        remove(id) {
            update(toasts => toasts.filter(t => t.id !== id));
        },

        clear() {
            update(() => []);
        },

        // Convenience methods
        success(message, options = {}) {
            return this.add({ type: 'success', message, ...options });
        },

        error(message, options = {}) {
            return this.add({ type: 'error', message, duration: 7000, ...options });
        },

        warning(message, options = {}) {
            return this.add({ type: 'warning', message, ...options });
        },

        info(message, options = {}) {
            return this.add({ type: 'info', message, ...options });
        }
    };
};

export const toastStore = createToastStore();
