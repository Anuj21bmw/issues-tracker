// Create: frontend/src/lib/stores/toast.js
import { writable } from 'svelte/store';

const createToastStore = () => {
    const { subscribe, set, update } = writable([]);

    return {
        subscribe,
        
        success: (message) => {
            const id = Date.now();
            update(toasts => [...toasts, { id, type: 'success', message }]);
            setTimeout(() => {
                update(toasts => toasts.filter(t => t.id !== id));
            }, 5000);
        },
        
        error: (message) => {
            const id = Date.now();
            update(toasts => [...toasts, { id, type: 'error', message }]);
            setTimeout(() => {
                update(toasts => toasts.filter(t => t.id !== id));
            }, 7000);
        },
        
        info: (message) => {
            const id = Date.now();
            update(toasts => [...toasts, { id, type: 'info', message }]);
            setTimeout(() => {
                update(toasts => toasts.filter(t => t.id !== id));
            }, 4000);
        },
        
        remove: (id) => {
            update(toasts => toasts.filter(t => t.id !== id));
        },
        
        clear: () => {
            set([]);
        }
    };
};

export const toastStore = createToastStore();